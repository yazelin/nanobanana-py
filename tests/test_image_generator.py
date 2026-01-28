"""測試圖片生成器模組"""

import pytest

from nanobanana_py.image_generator import (
    get_timeout,
    validate_authentication,
)


class TestValidateAuthentication:
    """測試認證驗證"""

    def test_nanobanana_gemini_api_key(self, monkeypatch, clean_env):
        """NANOBANANA_GEMINI_API_KEY 優先"""
        monkeypatch.setenv("NANOBANANA_GEMINI_API_KEY", "nb-gemini-key")
        monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")

        config = validate_authentication()
        assert config.api_key == "nb-gemini-key"
        assert config.key_type == "GEMINI_API_KEY"

    def test_nanobanana_google_api_key(self, monkeypatch, clean_env):
        """NANOBANANA_GOOGLE_API_KEY 第二優先"""
        monkeypatch.setenv("NANOBANANA_GOOGLE_API_KEY", "nb-google-key")
        monkeypatch.setenv("GOOGLE_API_KEY", "google-key")

        config = validate_authentication()
        assert config.api_key == "nb-google-key"
        assert config.key_type == "GOOGLE_API_KEY"

    def test_gemini_api_key_fallback(self, monkeypatch, clean_env):
        """GEMINI_API_KEY 備援"""
        monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")

        config = validate_authentication()
        assert config.api_key == "gemini-key"
        assert config.key_type == "GEMINI_API_KEY"

    def test_google_api_key_fallback(self, monkeypatch, clean_env):
        """GOOGLE_API_KEY 最後備援"""
        monkeypatch.setenv("GOOGLE_API_KEY", "google-key")

        config = validate_authentication()
        assert config.api_key == "google-key"
        assert config.key_type == "GOOGLE_API_KEY"

    def test_no_api_key_raises_error(self, clean_env):
        """沒有 API key 應該報錯"""
        with pytest.raises(ValueError, match="No valid API key found"):
            validate_authentication()


class TestGetTimeout:
    """測試超時取得"""

    def test_default_timeout(self, monkeypatch, clean_env):
        """預設超時"""
        timeout = get_timeout()
        assert timeout == 60.0

    def test_custom_timeout(self, monkeypatch, clean_env):
        """自訂超時"""
        monkeypatch.setenv("NANOBANANA_TIMEOUT", "120")
        timeout = get_timeout()
        assert timeout == 120.0

    def test_invalid_timeout_uses_default(self, monkeypatch, clean_env):
        """無效超時使用預設值"""
        monkeypatch.setenv("NANOBANANA_TIMEOUT", "invalid")
        timeout = get_timeout()
        assert timeout == 60.0
