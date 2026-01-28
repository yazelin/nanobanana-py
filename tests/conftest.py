"""pytest 設定與共用 fixtures"""

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """建立臨時目錄"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_image(temp_dir):
    """建立測試用的假圖片"""
    from PIL import Image

    img_path = temp_dir / "test_image.jpg"
    img = Image.new("RGB", (100, 100), color="red")
    img.save(img_path)
    return img_path


@pytest.fixture
def mock_api_key(monkeypatch):
    """設定假的 API key"""
    monkeypatch.setenv("NANOBANANA_GEMINI_API_KEY", "test-api-key-12345")


@pytest.fixture
def clean_env(monkeypatch):
    """清除所有 nanobanana 相關環境變數"""
    for key in list(os.environ.keys()):
        if key.startswith("NANOBANANA_") or key in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
            monkeypatch.delenv(key, raising=False)
