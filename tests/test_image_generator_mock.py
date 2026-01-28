"""測試圖片生成器"""

import pytest

from nanobanana_py.image_generator import ImageGenerator
from nanobanana_py.types import AuthConfig, ImageGenerationRequest


@pytest.fixture
def auth_config():
    """測試用的認證設定"""
    return AuthConfig(api_key="test-api-key-12345")


@pytest.fixture
def generator(auth_config):
    """建立 ImageGenerator 實例"""
    return ImageGenerator(auth_config)


class TestImageGeneratorInit:
    """測試 ImageGenerator 初始化"""

    def test_init_with_auth_config(self, auth_config):
        """使用 AuthConfig 初始化"""
        generator = ImageGenerator(auth_config)
        assert generator.api_key == "test-api-key-12345"

    def test_default_model(self, generator):
        """預設模型"""
        assert "gemini" in generator.model_name.lower()

    def test_model_name_from_env(self, monkeypatch, auth_config):
        """從環境變數取得模型名稱"""
        monkeypatch.setenv("NANOBANANA_MODEL", "gemini-3-pro-image-preview")
        generator = ImageGenerator(auth_config)
        assert generator.model_name == "gemini-3-pro-image-preview"


class TestRequestBuilding:
    """測試請求建構"""

    def test_build_batch_prompts_with_styles(self, generator):
        """建構有風格的批次 prompt"""
        request = ImageGenerationRequest(
            prompt="mountain landscape",
            styles=["watercolor", "sketch"],
            output_count=2,
        )
        prompts = generator._build_batch_prompts(request)

        assert len(prompts) == 2
        assert "watercolor" in prompts[0].lower()
        assert "sketch" in prompts[1].lower()

    def test_build_batch_prompts_simple(self, generator):
        """建構簡單的批次 prompt"""
        request = ImageGenerationRequest(
            prompt="a cute cat",
            output_count=3,
        )
        prompts = generator._build_batch_prompts(request)

        assert len(prompts) == 3
        # 所有 prompt 應該相同
        assert all(p == prompts[0] for p in prompts)

    def test_build_batch_prompts_with_seed(self, generator):
        """有 seed 的批次 prompt"""
        request = ImageGenerationRequest(
            prompt="sunset",
            output_count=2,
            seed=12345,
        )
        prompts = generator._build_batch_prompts(request)

        assert len(prompts) == 2

    def test_build_request_body(self, generator):
        """建構請求 body"""
        body = generator._build_request_body("a cute cat", model_name="gemini-2.5-flash-image", resolution="1K")

        assert "contents" in body
        assert body["contents"][0]["parts"][0]["text"] == "a cute cat"
        assert "generationConfig" in body


class TestImageExtraction:
    """測試圖片擷取"""

    def test_extract_image_from_valid_response(self, generator):
        """從有效回應擷取圖片"""
        response = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "inlineData": {
                                    "mimeType": "image/jpeg",
                                    "data": "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAABAAEBAREA/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQEAAD8AVN//2Q==",
                                }
                            }
                        ]
                    }
                }
            ]
        }
        result = generator._extract_image_from_response(response)

        assert result is not None
        data, mime_type = result
        assert isinstance(data, bytes)
        assert mime_type == "image/jpeg"

    def test_extract_image_from_invalid_response(self, generator):
        """從無效回應擷取圖片"""
        response = {"error": "Something went wrong"}
        result = generator._extract_image_from_response(response)

        assert result is None

    def test_extract_image_from_empty_response(self, generator):
        """從空回應擷取圖片"""
        response = {"candidates": []}
        result = generator._extract_image_from_response(response)

        assert result is None


class TestBase64Validation:
    """測試 Base64 驗證"""

    def test_valid_base64(self, generator):
        """有效的 base64"""
        # "hello" 的 base64
        assert generator._is_valid_base64("aGVsbG8=") is True

    def test_invalid_base64(self, generator):
        """無效的 base64"""
        assert generator._is_valid_base64("not valid base64!!!") is False

    def test_empty_base64(self, generator):
        """空的 base64"""
        assert generator._is_valid_base64("") is False
