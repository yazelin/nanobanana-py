"""測試檔案處理模組"""

import os
from pathlib import Path

import pytest

from nanobanana_py.file_handler import (
    find_input_file,
    generate_filename,
    get_mime_type,
    get_output_directory,
)


class TestGetOutputDirectory:
    """測試 get_output_directory"""

    def test_default_directory(self, monkeypatch, temp_dir):
        """預設使用當前目錄"""
        monkeypatch.delenv("NANOBANANA_OUTPUT_DIR", raising=False)
        monkeypatch.chdir(temp_dir)
        result = get_output_directory()
        assert result == temp_dir

    def test_custom_directory(self, monkeypatch, temp_dir):
        """使用環境變數指定的目錄"""
        custom_dir = temp_dir / "custom_output"
        monkeypatch.setenv("NANOBANANA_OUTPUT_DIR", str(custom_dir))
        result = get_output_directory()
        assert result == custom_dir
        assert custom_dir.exists()  # 應該自動建立


class TestGenerateFilename:
    """測試 generate_filename"""

    def test_basic_prompt(self):
        """基本 prompt 轉檔名"""
        filename = generate_filename("sunset over mountains")
        assert filename.startswith("sunset_over_mountains_")
        assert filename.endswith(".jpg")

    def test_custom_filename(self):
        """自訂檔名"""
        filename = generate_filename("test", custom_filename="my_image")
        assert filename == "my_image.jpg"

    def test_custom_filename_with_index(self):
        """自訂檔名 + 索引"""
        filename = generate_filename("test", custom_filename="my_image", index=2)
        assert filename == "my_image_3.jpg"  # index 從 0 開始，顯示從 1 開始

    def test_png_format(self):
        """PNG 格式"""
        filename = generate_filename("test", file_format="png")
        assert filename.endswith(".png")

    def test_jpeg_format(self):
        """JPEG 格式"""
        filename = generate_filename("test", file_format="jpeg")
        assert filename.endswith(".jpg")

    def test_long_prompt_truncation(self):
        """長 prompt 截斷"""
        long_prompt = "a" * 100
        filename = generate_filename(long_prompt)
        # 檔名部分（不含時間戳和 hash）應該被截斷
        base_part = filename.split("_")[0]
        assert len(base_part) <= 50

    def test_special_characters_removed(self):
        """移除特殊字元"""
        filename = generate_filename("test! @#$% image")
        assert "!" not in filename
        assert "@" not in filename
        assert "#" not in filename

    def test_custom_suffix(self):
        """自訂後綴"""
        filename = generate_filename("test", custom_filename="icon", suffix="64x64")
        assert filename == "icon_64x64.jpg"


class TestFindInputFile:
    """測試 find_input_file"""

    def test_absolute_path_exists(self, temp_image):
        """絕對路徑存在"""
        found, path, searched = find_input_file(str(temp_image))
        assert found is True
        assert path == str(temp_image)

    def test_absolute_path_not_exists(self, temp_dir):
        """絕對路徑不存在"""
        fake_path = str(temp_dir / "nonexistent.jpg")
        found, path, searched = find_input_file(fake_path)
        assert found is False
        assert path is None
        assert fake_path in searched

    def test_relative_path_in_cwd(self, temp_image, monkeypatch):
        """相對路徑在當前目錄"""
        monkeypatch.chdir(temp_image.parent)
        found, path, searched = find_input_file(temp_image.name)
        assert found is True
        assert path is not None

    def test_relative_path_not_found(self, temp_dir, monkeypatch):
        """相對路徑找不到"""
        monkeypatch.chdir(temp_dir)
        found, path, searched = find_input_file("nonexistent.jpg")
        assert found is False
        assert path is None
        assert len(searched) > 0  # 有搜尋過的路徑


class TestGetMimeType:
    """測試 get_mime_type"""

    def test_png(self):
        assert get_mime_type("image.png") == "image/png"

    def test_jpg(self):
        assert get_mime_type("image.jpg") == "image/jpeg"

    def test_jpeg(self):
        assert get_mime_type("image.jpeg") == "image/jpeg"

    def test_gif(self):
        assert get_mime_type("image.gif") == "image/gif"

    def test_webp(self):
        assert get_mime_type("image.webp") == "image/webp"

    def test_unknown_defaults_to_jpeg(self):
        assert get_mime_type("image.bmp") == "image/jpeg"

    def test_case_insensitive(self):
        assert get_mime_type("image.PNG") == "image/png"
        assert get_mime_type("image.JPG") == "image/jpeg"
