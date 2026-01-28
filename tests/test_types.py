"""測試型別定義"""

import pytest
from pydantic import ValidationError

from nanobanana_py.types import (
    AuthConfig,
    EditImageArgs,
    GenerateDiagramArgs,
    GenerateIconArgs,
    GenerateImageArgs,
    GeneratePatternArgs,
    GenerateStoryArgs,
    ImageGenerationRequest,
    ImageGenerationResponse,
    RestoreImageArgs,
)


class TestImageGenerationRequest:
    """測試 ImageGenerationRequest"""

    def test_minimal_request(self):
        """最小請求只需要 prompt"""
        req = ImageGenerationRequest(prompt="test image")
        assert req.prompt == "test image"
        assert req.output_count == 1
        assert req.resolution == "1K"
        assert req.preview is False
        assert req.no_preview is False
        assert req.parallel == 2

    def test_full_request(self):
        """完整請求所有參數"""
        req = ImageGenerationRequest(
            prompt="test image",
            input_image="input.jpg",
            reference_images=["ref1.jpg", "ref2.jpg"],
            output_count=4,
            mode="edit",
            styles=["watercolor", "sketch"],
            variations=["lighting", "mood"],
            format="grid",
            file_format="png",
            seed=12345,
            resolution="2K",
            aspect_ratio="16:9",
            parallel=4,
            preview=True,
            no_preview=False,
            filename="output",
        )
        assert req.output_count == 4
        assert req.mode == "edit"
        assert req.styles == ["watercolor", "sketch"]
        assert req.resolution == "2K"
        assert req.parallel == 4

    def test_invalid_resolution(self):
        """無效的解析度應該報錯"""
        with pytest.raises(ValidationError):
            ImageGenerationRequest(prompt="test", resolution="5K")  # type: ignore

    def test_invalid_format(self):
        """無效的格式應該報錯"""
        with pytest.raises(ValidationError):
            ImageGenerationRequest(prompt="test", format="invalid")  # type: ignore


class TestImageGenerationResponse:
    """測試 ImageGenerationResponse"""

    def test_success_response(self):
        """成功回應"""
        resp = ImageGenerationResponse(
            success=True,
            message="Generated 1 image",
            generated_files=["output.jpg"],
        )
        assert resp.success is True
        assert resp.error is None
        assert resp.used_fallback is False

    def test_error_response(self):
        """錯誤回應"""
        resp = ImageGenerationResponse(
            success=False,
            message="Generation failed",
            error="API timeout",
        )
        assert resp.success is False
        assert resp.error == "API timeout"

    def test_fallback_response(self):
        """Fallback 回應"""
        resp = ImageGenerationResponse(
            success=True,
            message="Generated with fallback",
            generated_files=["output.jpg"],
            model_used="gemini-2.5-flash-image",
            used_fallback=True,
            primary_model="gemini-3-pro-image-preview",
        )
        assert resp.used_fallback is True
        assert resp.model_used == "gemini-2.5-flash-image"
        assert resp.primary_model == "gemini-3-pro-image-preview"


class TestAuthConfig:
    """測試 AuthConfig"""

    def test_gemini_key(self):
        """Gemini API key"""
        config = AuthConfig(api_key="test-key")
        assert config.api_key == "test-key"
        assert config.key_type == "GEMINI_API_KEY"

    def test_google_key(self):
        """Google API key"""
        config = AuthConfig(api_key="test-key", key_type="GOOGLE_API_KEY")
        assert config.key_type == "GOOGLE_API_KEY"


class TestGenerateImageArgs:
    """測試 GenerateImageArgs"""

    def test_defaults(self):
        """預設值"""
        args = GenerateImageArgs(prompt="test")
        assert args.output_count == 1
        assert args.format == "separate"
        assert args.resolution == "1K"
        assert args.preview is False
        assert args.no_preview is False
        assert args.parallel == 2

    def test_output_count_validation(self):
        """output_count 驗證（1-8）"""
        # 有效範圍
        args = GenerateImageArgs(prompt="test", output_count=8)
        assert args.output_count == 8

        # 超出範圍
        with pytest.raises(ValidationError):
            GenerateImageArgs(prompt="test", output_count=9)

        with pytest.raises(ValidationError):
            GenerateImageArgs(prompt="test", output_count=0)

    def test_parallel_validation(self):
        """parallel 驗證（1-8）"""
        args = GenerateImageArgs(prompt="test", parallel=8)
        assert args.parallel == 8

        with pytest.raises(ValidationError):
            GenerateImageArgs(prompt="test", parallel=9)


class TestEditImageArgs:
    """測試 EditImageArgs"""

    def test_required_fields(self):
        """必填欄位"""
        args = EditImageArgs(prompt="add sunglasses", file="photo.jpg")
        assert args.prompt == "add sunglasses"
        assert args.file == "photo.jpg"

    def test_missing_file(self):
        """缺少 file 應該報錯"""
        with pytest.raises(ValidationError):
            EditImageArgs(prompt="test")  # type: ignore


class TestRestoreImageArgs:
    """測試 RestoreImageArgs"""

    def test_required_fields(self):
        """必填欄位"""
        args = RestoreImageArgs(prompt="remove scratches", file="old_photo.jpg")
        assert args.prompt == "remove scratches"
        assert args.file == "old_photo.jpg"


class TestGenerateIconArgs:
    """測試 GenerateIconArgs"""

    def test_defaults(self):
        """預設值"""
        args = GenerateIconArgs(prompt="coffee cup logo")
        assert args.type == "app-icon"
        assert args.style == "modern"
        assert args.format == "png"
        assert args.background == "transparent"
        assert args.corners == "rounded"


class TestGeneratePatternArgs:
    """測試 GeneratePatternArgs"""

    def test_defaults(self):
        """預設值"""
        args = GeneratePatternArgs(prompt="geometric pattern")
        assert args.size == "256x256"
        assert args.type == "seamless"
        assert args.style == "abstract"
        assert args.density == "medium"
        assert args.colors == "colorful"
        assert args.repeat == "tile"


class TestGenerateStoryArgs:
    """測試 GenerateStoryArgs"""

    def test_defaults(self):
        """預設值"""
        args = GenerateStoryArgs(prompt="seed growing into tree")
        assert args.steps == 4
        assert args.type == "story"
        assert args.style == "consistent"
        assert args.transition == "smooth"

    def test_steps_validation(self):
        """steps 驗證（2-8）"""
        args = GenerateStoryArgs(prompt="test", steps=8)
        assert args.steps == 8

        with pytest.raises(ValidationError):
            GenerateStoryArgs(prompt="test", steps=1)

        with pytest.raises(ValidationError):
            GenerateStoryArgs(prompt="test", steps=9)


class TestGenerateDiagramArgs:
    """測試 GenerateDiagramArgs"""

    def test_defaults(self):
        """預設值"""
        args = GenerateDiagramArgs(prompt="login flow")
        assert args.type == "flowchart"
        assert args.style == "professional"
        assert args.layout == "hierarchical"
        assert args.complexity == "detailed"
        assert args.colors == "accent"
        assert args.annotations == "detailed"
