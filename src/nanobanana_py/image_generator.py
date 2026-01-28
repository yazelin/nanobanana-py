"""Gemini 圖片生成器"""

import asyncio
import base64
import io
import logging
import os
import platform
import subprocess
from typing import Any

import httpx
from PIL import Image

from .file_handler import (
    find_input_file,
    generate_filename,
    get_output_directory,
    read_image_as_base64,
    save_image_buffer,
)
from .types import (
    AuthConfig,
    ImageGenerationRequest,
    ImageGenerationResponse,
    ImageResolution,
)

logger = logging.getLogger("nanobanana")

# API 設定
API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_MODEL = "gemini-2.5-flash-image"
DEFAULT_RESOLUTION: ImageResolution = "1K"
DEFAULT_PARALLEL = 2
DEFAULT_TIMEOUT = 60.0  # 秒

# Fallback 模型列表（按優先順序）
# 可透過 NANOBANANA_FALLBACK_MODELS 環境變數自訂，用逗號分隔
DEFAULT_FALLBACK_MODELS = [
    "gemini-2.5-flash-image",  # 穩定版本
    "gemini-2.0-flash-exp-image-generation",  # 實驗版本
]


def get_timeout() -> float:
    """取得 API 超時設定（秒）"""
    timeout_str = os.getenv("NANOBANANA_TIMEOUT")
    if timeout_str:
        try:
            return float(timeout_str)
        except ValueError:
            logger.warning(f"Invalid NANOBANANA_TIMEOUT value: {timeout_str}, using default {DEFAULT_TIMEOUT}")
    return DEFAULT_TIMEOUT


def debug(*args: Any) -> None:
    """Debug 輸出（僅在 NANOBANANA_DEBUG 環境變數設定時輸出）"""
    if os.getenv("NANOBANANA_DEBUG"):
        logger.debug(" ".join(str(a) for a in args))


def validate_authentication() -> AuthConfig:
    """驗證認證設定"""
    # 優先順序：NANOBANANA_GEMINI_API_KEY > NANOBANANA_GOOGLE_API_KEY > GEMINI_API_KEY > GOOGLE_API_KEY
    for env_var, key_type in [
        ("NANOBANANA_GEMINI_API_KEY", "GEMINI_API_KEY"),
        ("NANOBANANA_GOOGLE_API_KEY", "GOOGLE_API_KEY"),
        ("GEMINI_API_KEY", "GEMINI_API_KEY"),
        ("GOOGLE_API_KEY", "GOOGLE_API_KEY"),
    ]:
        api_key = os.getenv(env_var)
        if api_key:
            debug(f"✓ Found {env_var} environment variable")
            return AuthConfig(api_key=api_key, key_type=key_type)  # type: ignore

    raise ValueError(
        "ERROR: No valid API key found. Please set NANOBANANA_GEMINI_API_KEY, "
        "NANOBANANA_GOOGLE_API_KEY, GEMINI_API_KEY, or GOOGLE_API_KEY environment variable.\n"
        "For more details on authentication, visit: "
        "https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/authentication.md"
    )


class ImageGenerator:
    """Gemini 圖片生成器"""

    def __init__(self, auth_config: AuthConfig | None = None):
        if auth_config is None:
            auth_config = validate_authentication()

        self.api_key = auth_config.api_key
        self.model_name = os.getenv("NANOBANANA_MODEL", DEFAULT_MODEL)

        # 初始化 fallback 模型列表
        fallback_env = os.getenv("NANOBANANA_FALLBACK_MODELS")
        if fallback_env:
            self.fallback_models = [m.strip() for m in fallback_env.split(",") if m.strip()]
        else:
            self.fallback_models = DEFAULT_FALLBACK_MODELS.copy()

        # 確保主要模型在 fallback 列表的最前面
        if self.model_name not in self.fallback_models:
            self.fallback_models.insert(0, self.model_name)
        elif self.fallback_models[0] != self.model_name:
            self.fallback_models.remove(self.model_name)
            self.fallback_models.insert(0, self.model_name)

        # 超時設定
        self.timeout = get_timeout()

        debug(f"DEBUG - Primary model: {self.model_name}")
        debug(f"DEBUG - Fallback chain: {' -> '.join(self.fallback_models)}")
        debug(f"DEBUG - Timeout: {self.timeout}s")

    def _build_request_body(
        self,
        prompt: str,
        model_name: str,
        resolution: ImageResolution | None = None,
        aspect_ratio: str | None = None,
        input_image_base64: str | None = None,
        input_image_mime_type: str | None = None,
        seed: int | None = None,
        reference_images_data: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """建立 API 請求 body"""
        # 建立 parts
        parts: list[dict[str, Any]] = [{"text": prompt}]

        # 加入輸入圖片（用於編輯）
        if input_image_base64 and input_image_mime_type:
            parts.append({
                "inlineData": {
                    "mimeType": input_image_mime_type,
                    "data": input_image_base64,
                }
            })

        # 加入參考圖片
        if reference_images_data:
            for ref_image in reference_images_data:
                parts.append({
                    "inlineData": {
                        "mimeType": ref_image["mimeType"],
                        "data": ref_image["data"],
                    }
                })

        # 建立 generationConfig
        # gemini-2.5-flash-image: 只支援 aspectRatio
        # gemini-3-pro-image-preview: 支援 aspectRatio 和 imageSize (1K/2K/4K)
        is_gemini3 = "gemini-3" in model_name

        image_config: dict[str, Any] = {}
        if aspect_ratio:
            image_config["aspectRatio"] = aspect_ratio
        if is_gemini3 and resolution:
            image_config["imageSize"] = resolution

        generation_config: dict[str, Any] = {
            "responseModalities": ["Image"],
        }
        if image_config:
            generation_config["imageConfig"] = image_config
        if seed is not None:
            generation_config["seed"] = seed

        return {
            "contents": [
                {
                    "role": "user",
                    "parts": parts,
                }
            ],
            "generationConfig": generation_config,
        }

    async def _call_gemini_api(
        self,
        prompt: str,
        resolution: ImageResolution | None = None,
        aspect_ratio: str | None = None,
        input_image_base64: str | None = None,
        input_image_mime_type: str | None = None,
        seed: int | None = None,
        reference_images_data: list[dict[str, str]] | None = None,
    ) -> tuple[dict[str, Any], str, bool]:
        """呼叫 Gemini REST API（帶 fallback 機制）

        Returns:
            tuple: (response_data, model_used, used_fallback)
        """
        last_error: Exception | None = None
        primary_model = self.fallback_models[0]

        for model_name in self.fallback_models:
            url = f"{API_BASE_URL}/{model_name}:generateContent?key={self.api_key}"
            request_body = self._build_request_body(
                prompt=prompt,
                model_name=model_name,
                resolution=resolution,
                aspect_ratio=aspect_ratio,
                input_image_base64=input_image_base64,
                input_image_mime_type=input_image_mime_type,
                seed=seed,
                reference_images_data=reference_images_data,
            )

            debug(f"DEBUG - Trying model: {model_name}")
            debug(f"DEBUG - REST API URL: {url.replace(self.api_key, '[REDACTED]')}")

            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, json=request_body)

                    if response.status_code != 200:
                        error_data = response.json()
                        error_message = error_data.get("error", {}).get("message", response.text)
                        last_error = RuntimeError(f"API Error {response.status_code}: {error_message}")
                        logger.warning(f"Model {model_name} failed: {error_message}")
                        continue

                    result = response.json()

                    # 檢查是否有有效的圖片資料
                    candidates = result.get("candidates", [])
                    if candidates:
                        content = candidates[0].get("content", {})
                        parts = content.get("parts", [])
                        has_image = any("inlineData" in part for part in parts)
                        if has_image:
                            used_fallback = model_name != primary_model
                            if used_fallback:
                                logger.info(f"Fallback 成功：使用 {model_name} 生成圖片（原本：{primary_model}）")
                            return result, model_name, used_fallback

                    # 沒有圖片資料，嘗試下一個模型
                    last_error = RuntimeError("No image data in response")
                    logger.warning(f"Model {model_name} returned no image data")
                    continue

            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(f"Model {model_name} timeout: {e}")
                continue
            except httpx.RequestError as e:
                last_error = e
                logger.warning(f"Model {model_name} request error: {e}")
                continue

        # 所有模型都失敗
        raise RuntimeError(
            f"All models failed. Last error: {last_error}"
        ) from last_error

    def _extract_image_from_response(self, response: dict[str, Any]) -> tuple[bytes, str] | None:
        """從 API 回應中提取圖片"""
        candidates = response.get("candidates", [])
        if not candidates:
            return None

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])

        for part in parts:
            if "inlineData" in part:
                inline_data = part["inlineData"]
                mime_type = inline_data.get("mimeType", "image/jpeg")
                data = inline_data.get("data", "")
                if data:
                    return base64.b64decode(data), mime_type

            # Fallback: 檢查 text 欄位是否為 base64 圖片
            if "text" in part:
                text = part["text"]
                if len(text) > 1000 and self._is_valid_base64(text):
                    return base64.b64decode(text), "image/jpeg"

        return None

    def _is_valid_base64(self, data: str) -> bool:
        """檢查是否為有效的 base64"""
        import re
        if not data:
            return False
        return bool(re.match(r"^[A-Za-z0-9+/]*={0,2}$", data))

    def _convert_image_format(
        self, buffer: bytes, source_format: str, target_format: str
    ) -> bytes:
        """轉換圖片格式"""
        if source_format == target_format:
            return buffer

        img = Image.open(io.BytesIO(buffer))

        # 處理透明度
        if target_format == "jpeg" and img.mode in ("RGBA", "LA", "P"):
            # 將透明背景轉為白色
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = background

        output = io.BytesIO()
        save_format = "JPEG" if target_format == "jpeg" else "PNG"
        img.save(output, format=save_format, quality=92 if save_format == "JPEG" else None)
        return output.getvalue()

    def _build_batch_prompts(self, request: ImageGenerationRequest) -> list[str]:
        """建立批次 prompt"""
        prompts: list[str] = []
        base_prompt = request.prompt

        # 處理風格
        if request.styles:
            for style in request.styles:
                prompts.append(f"{base_prompt}, {style} style")

        # 處理變化
        if request.variations:
            base_prompts = prompts if prompts else [base_prompt]
            variation_prompts: list[str] = []

            variation_map = {
                "lighting": ["dramatic lighting", "soft lighting"],
                "angle": ["from above", "close-up view"],
                "color-palette": ["warm color palette", "cool color palette"],
                "composition": ["centered composition", "rule of thirds composition"],
                "mood": ["cheerful mood", "dramatic mood"],
                "season": ["in spring", "in winter"],
                "time-of-day": ["at sunrise", "at sunset"],
            }

            for base_p in base_prompts:
                for variation in request.variations:
                    if variation in variation_map:
                        for var in variation_map[variation]:
                            variation_prompts.append(f"{base_p}, {var}")

            if variation_prompts:
                prompts = variation_prompts

        # 如果沒有風格/變化但 output_count > 1，建立簡單變化
        if not prompts and request.output_count > 1:
            prompts = [base_prompt] * request.output_count

        # 限制數量
        if request.output_count and len(prompts) > request.output_count:
            prompts = prompts[: request.output_count]

        return prompts if prompts else [base_prompt]

    async def _generate_single_image(
        self,
        prompt: str,
        index: int,
        request: ImageGenerationRequest,
        output_dir: str,
        force_suffix: bool,
        reference_images_data: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """生成單張圖片"""
        debug(f"DEBUG - Generating variation {index + 1}: {prompt}")

        try:
            response, model_used, used_fallback = await self._call_gemini_api(
                prompt=prompt,
                resolution=request.resolution,
                aspect_ratio=request.aspect_ratio,
                seed=request.seed,
                reference_images_data=reference_images_data,
            )

            result = self._extract_image_from_response(response)
            if not result:
                return {"success": False, "error": "No image data found in API response"}

            image_data, mime_type = result

            # 決定檔案格式
            target_format = request.file_format
            source_format = "png" if "png" in mime_type else "jpeg"

            # 轉換格式（如果需要）
            if source_format != target_format:
                image_data = self._convert_image_format(image_data, source_format, target_format)

            # 生成檔名
            filename = generate_filename(
                prompt=request.prompt if not (request.styles or request.variations) else prompt,
                file_format=target_format,
                index=index,
                custom_filename=request.filename,
                force_suffix=force_suffix,
                suffix=request.filename_suffixes[index] if request.filename_suffixes and index < len(request.filename_suffixes) else None,
            )

            # 儲存
            file_path = save_image_buffer(image_data, output_dir, filename)  # type: ignore
            debug(f"DEBUG - Image saved to: {file_path}")

            return {
                "success": True,
                "file_path": file_path,
                "model_used": model_used,
                "used_fallback": used_fallback,
            }

        except Exception as e:
            error_msg = str(e)
            debug(f"DEBUG - Error generating variation {index + 1}: {error_msg}")
            return {"success": False, "error": error_msg}

    async def generate_text_to_image(
        self, request: ImageGenerationRequest
    ) -> ImageGenerationResponse:
        """文字生成圖片"""
        try:
            output_dir = get_output_directory()
            prompts = self._build_batch_prompts(request)
            force_suffix = bool(request.filename) and len(prompts) > 1

            # 處理參考圖片
            reference_images_data: list[dict[str, str]] | None = None
            if request.reference_images:
                if len(request.reference_images) > 14:
                    return ImageGenerationResponse(
                        success=False,
                        message="Too many reference images provided",
                        error=f"Maximum 14 reference images allowed, but {len(request.reference_images)} were provided",
                    )

                reference_images_data = []
                for ref_path in request.reference_images:
                    found, file_path, searched = find_input_file(ref_path)
                    if not found:
                        return ImageGenerationResponse(
                            success=False,
                            message=f"Reference image not found: {ref_path}",
                            error=f"Searched in: {', '.join(searched)}",
                        )

                    image_base64 = read_image_as_base64(file_path)  # type: ignore
                    ext = file_path.lower().split(".")[-1]  # type: ignore
                    mime_type = "image/png" if ext == "png" else "image/jpeg"
                    reference_images_data.append({"data": image_base64, "mimeType": mime_type})

            # 決定並行數量
            parallel_count = min(max(1, request.parallel), 8)
            debug(f"DEBUG - Generating {len(prompts)} image(s) with parallelism of {parallel_count}")

            generated_files: list[str] = []
            first_error: str | None = None
            model_used: str | None = None
            used_fallback: bool = False

            # 批次處理
            for i in range(0, len(prompts), parallel_count):
                batch = prompts[i : i + parallel_count]
                tasks = [
                    self._generate_single_image(
                        prompt=prompt,
                        index=i + j,
                        request=request,
                        output_dir=str(output_dir),
                        force_suffix=force_suffix,
                        reference_images_data=reference_images_data,
                    )
                    for j, prompt in enumerate(batch)
                ]

                results = await asyncio.gather(*tasks)

                for result in results:
                    if result["success"] and result.get("file_path"):
                        generated_files.append(result["file_path"])
                        # 記錄 fallback 資訊（取第一個成功的結果）
                        if model_used is None:
                            model_used = result.get("model_used")
                            used_fallback = result.get("used_fallback", False)
                    elif result.get("error") and not first_error:
                        first_error = result["error"]

            if not generated_files:
                return ImageGenerationResponse(
                    success=False,
                    message="Failed to generate any images",
                    error=first_error or "No image data found in API responses",
                )

            # 處理預覽
            if request.preview and not request.no_preview:
                await self._handle_preview(generated_files)

            # 建立回應訊息
            message = f"Successfully generated {len(generated_files)} image variation(s)"
            if used_fallback:
                message += f" (使用備用模型: {model_used}，原本: {self.model_name})"

            return ImageGenerationResponse(
                success=True,
                message=message,
                generated_files=generated_files,
                model_used=model_used,
                used_fallback=used_fallback,
                primary_model=self.model_name if used_fallback else None,
            )

        except Exception as e:
            debug(f"DEBUG - Error in generateTextToImage: {e}")
            return ImageGenerationResponse(
                success=False,
                message="Failed to generate image",
                error=str(e),
            )

    async def edit_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """編輯圖片"""
        try:
            if not request.input_image:
                return ImageGenerationResponse(
                    success=False,
                    message="Input image file is required for editing",
                    error="Missing input_image parameter",
                )

            found, file_path, searched = find_input_file(request.input_image)
            if not found:
                return ImageGenerationResponse(
                    success=False,
                    message=f"Input image not found: {request.input_image}",
                    error=f"Searched in: {', '.join(searched)}",
                )

            output_dir = get_output_directory()
            image_base64 = read_image_as_base64(file_path)  # type: ignore
            ext = file_path.lower().split(".")[-1]  # type: ignore
            mime_type = "image/png" if ext == "png" else "image/jpeg"

            response, model_used, used_fallback = await self._call_gemini_api(
                prompt=request.prompt,
                resolution=request.resolution,
                aspect_ratio=request.aspect_ratio,
                input_image_base64=image_base64,
                input_image_mime_type=mime_type,
                seed=request.seed,
            )

            result = self._extract_image_from_response(response)
            if not result:
                return ImageGenerationResponse(
                    success=False,
                    message=f"Failed to {request.mode} image",
                    error="No image data in response",
                )

            image_data, resp_mime_type = result

            # 轉換格式
            target_format = request.file_format
            source_format = "png" if "png" in resp_mime_type else "jpeg"
            if source_format != target_format:
                image_data = self._convert_image_format(image_data, source_format, target_format)

            # 儲存
            filename = generate_filename(
                prompt=f"{request.mode}_{request.prompt}",
                file_format=target_format,
                custom_filename=request.filename,
            )
            file_path = save_image_buffer(image_data, str(output_dir), filename)

            # 處理預覽
            if request.preview and not request.no_preview:
                await self._handle_preview([file_path])

            # 建立回應訊息
            message = f"Successfully {request.mode}d image"
            if used_fallback:
                message += f" (使用備用模型: {model_used}，原本: {self.model_name})"

            return ImageGenerationResponse(
                success=True,
                message=message,
                generated_files=[file_path],
                model_used=model_used,
                used_fallback=used_fallback,
                primary_model=self.model_name if used_fallback else None,
            )

        except Exception as e:
            debug(f"DEBUG - Error in {request.mode}Image: {e}")
            return ImageGenerationResponse(
                success=False,
                message=f"Failed to {request.mode} image",
                error=str(e),
            )

    async def generate_story_sequence(
        self,
        request: ImageGenerationRequest,
        story_type: str = "story",
        style: str = "consistent",
        transition: str = "smooth",
    ) -> ImageGenerationResponse:
        """生成故事序列"""
        try:
            output_dir = get_output_directory()
            steps = request.output_count or 4
            force_suffix = bool(request.filename) and steps > 1

            # 處理參考圖片
            reference_images_data: list[dict[str, str]] | None = None
            if request.reference_images:
                if len(request.reference_images) > 14:
                    return ImageGenerationResponse(
                        success=False,
                        message="Too many reference images provided",
                        error=f"Maximum 14 reference images allowed",
                    )

                reference_images_data = []
                for ref_path in request.reference_images:
                    found, file_path, searched = find_input_file(ref_path)
                    if not found:
                        return ImageGenerationResponse(
                            success=False,
                            message=f"Reference image not found: {ref_path}",
                            error=f"Searched in: {', '.join(searched)}",
                        )
                    image_base64 = read_image_as_base64(file_path)  # type: ignore
                    ext = file_path.lower().split(".")[-1]  # type: ignore
                    mime_type = "image/png" if ext == "png" else "image/jpeg"
                    reference_images_data.append({"data": image_base64, "mimeType": mime_type})

            parallel_count = min(max(1, request.parallel), 8)
            debug(f"DEBUG - Generating {steps}-step {story_type} sequence with parallelism of {parallel_count}")

            generated_files: list[str | None] = [None] * steps
            first_error: str | None = None

            async def generate_step(step_index: int) -> dict[str, Any]:
                step_number = step_index + 1
                step_prompt = f"{request.prompt}, step {step_number} of {steps}"

                # 根據類型加入上下文
                type_context = {
                    "story": f", narrative sequence, {style} art style",
                    "process": ", procedural step, instructional illustration",
                    "tutorial": ", tutorial step, educational diagram",
                    "timeline": ", chronological progression, timeline visualization",
                }
                step_prompt += type_context.get(story_type, "")

                # 加入過渡效果
                if step_index > 0:
                    step_prompt += f", {transition} transition from previous step"

                try:
                    response, model_used, used_fallback = await self._call_gemini_api(
                        prompt=step_prompt,
                        resolution=request.resolution,
                        aspect_ratio=request.aspect_ratio,
                        seed=request.seed,
                        reference_images_data=reference_images_data,
                    )

                    result = self._extract_image_from_response(response)
                    if not result:
                        return {"success": False, "error": "No image data found"}

                    image_data, mime_type = result
                    target_format = request.file_format
                    source_format = "png" if "png" in mime_type else "jpeg"

                    if source_format != target_format:
                        image_data = self._convert_image_format(image_data, source_format, target_format)

                    filename = generate_filename(
                        prompt=f"{story_type}_step{step_number}_{request.prompt}",
                        file_format=target_format,
                        index=step_index if request.filename else 0,
                        custom_filename=request.filename,
                        force_suffix=force_suffix,
                    )

                    file_path = save_image_buffer(image_data, str(output_dir), filename)
                    return {
                        "success": True,
                        "file_path": file_path,
                        "index": step_index,
                        "model_used": model_used,
                        "used_fallback": used_fallback,
                    }

                except Exception as e:
                    return {"success": False, "error": str(e), "index": step_index}

            model_used: str | None = None
            used_fallback: bool = False

            # 批次處理
            for i in range(0, steps, parallel_count):
                batch_indices = list(range(i, min(i + parallel_count, steps)))
                tasks = [generate_step(idx) for idx in batch_indices]
                results = await asyncio.gather(*tasks)

                for result in results:
                    idx = result.get("index", 0)
                    if result["success"] and result.get("file_path"):
                        generated_files[idx] = result["file_path"]
                        # 記錄 fallback 資訊（取第一個成功的結果）
                        if model_used is None:
                            model_used = result.get("model_used")
                            used_fallback = result.get("used_fallback", False)
                    elif result.get("error") and not first_error:
                        first_error = result["error"]

            completed_files = [f for f in generated_files if f is not None]

            if not completed_files:
                return ImageGenerationResponse(
                    success=False,
                    message="Failed to generate any story sequence images",
                    error=first_error or "No image data found",
                )

            # 處理預覽
            if request.preview and not request.no_preview:
                await self._handle_preview(completed_files)

            was_complete = len(completed_files) == steps
            message = (
                f"Successfully generated complete {steps}-step {story_type} sequence"
                if was_complete
                else f"Generated {len(completed_files)} out of {steps} requested {story_type} steps"
            )
            if used_fallback:
                message += f" (使用備用模型: {model_used}，原本: {self.model_name})"

            return ImageGenerationResponse(
                success=True,
                message=message,
                generated_files=completed_files,
                model_used=model_used,
                used_fallback=used_fallback,
                primary_model=self.model_name if used_fallback else None,
            )

        except Exception as e:
            debug(f"DEBUG - Error in generateStorySequence: {e}")
            return ImageGenerationResponse(
                success=False,
                message=f"Failed to generate {story_type} sequence",
                error=str(e),
            )

    async def _handle_preview(self, files: list[str]) -> None:
        """開啟圖片預覽"""
        system = platform.system()

        for file_path in files:
            try:
                if system == "Darwin":  # macOS
                    subprocess.run(["open", file_path], check=True)
                elif system == "Windows":
                    subprocess.run(["start", "", file_path], shell=True, check=True)
                else:  # Linux
                    subprocess.run(["xdg-open", file_path], check=True)
                debug(f"DEBUG - Opened preview for: {file_path}")
            except Exception as e:
                debug(f"DEBUG - Failed to open preview: {e}")
