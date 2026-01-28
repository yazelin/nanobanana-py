"""測試圖示處理模組"""

import pytest
from PIL import Image

from nanobanana_py.icon_processor import process_icon_file


def create_solid_image(width: int, height: int, color: tuple[int, int, int, int]) -> Image.Image:
    """建立純色圖片"""
    img = Image.new("RGBA", (width, height), color)
    return img


def fill_circle(
    img: Image.Image,
    center_x: int,
    center_y: int,
    radius: int,
    color: tuple[int, int, int, int],
) -> None:
    """填充圓形"""
    r2 = radius * radius
    for y in range(center_y - radius, center_y + radius + 1):
        for x in range(center_x - radius, center_x + radius + 1):
            dx = x - center_x
            dy = y - center_y
            if dx * dx + dy * dy <= r2:
                if 0 <= x < img.width and 0 <= y < img.height:
                    img.putpixel((x, y), color)


class TestProcessIconFile:
    """測試 process_icon_file"""

    def test_preserves_original_and_writes_output(self, temp_dir):
        """保留原檔並寫入處理後的檔案"""
        bg = (12, 24, 36, 255)
        fg = (240, 20, 20, 255)

        img = create_solid_image(140, 140, bg)
        fill_circle(img, 70, 70, 45, fg)

        input_path = temp_dir / "input.jpg"
        img.convert("RGB").save(input_path)

        output_path = process_icon_file(
            str(input_path),
            size=32,
            transparent_background=True,
            output_format="png",
            overwrite=False,
        )

        # 原檔應該存在
        assert input_path.exists()

        # 輸出檔案應該存在（格式：{name}_32x32.png）
        assert output_path.endswith("_32x32.png")
        output_img = Image.open(output_path)
        assert output_img.width == 32
        assert output_img.height == 32

    def test_different_sizes(self, temp_dir):
        """測試不同尺寸"""
        img = create_solid_image(100, 100, (255, 0, 0, 255))
        input_path = temp_dir / "input.png"
        img.save(input_path)

        for size in [16, 32, 64, 128]:
            output_path = process_icon_file(str(input_path), size=size)
            output_img = Image.open(output_path)
            assert output_img.width == size
            assert output_img.height == size

    def test_jpeg_output(self, temp_dir):
        """測試 JPEG 輸出"""
        img = create_solid_image(100, 100, (255, 0, 0, 255))
        input_path = temp_dir / "input.png"
        img.save(input_path)

        output_path = process_icon_file(
            str(input_path),
            size=64,
            output_format="jpeg",
        )

        assert output_path.endswith(".jpg")
