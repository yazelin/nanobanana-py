"""圖示處理模組"""

import io
from pathlib import Path

from PIL import Image


def process_icon_file(
    input_path: str,
    size: int = 1024,
    transparent_background: bool = True,
    output_format: str = "png",
    overwrite: bool = False,
) -> str:
    """
    處理圖示檔案（裁切、縮放）

    Args:
        input_path: 輸入圖片路徑
        size: 目標尺寸
        transparent_background: 是否保持透明背景
        output_format: 輸出格式（png 或 jpeg）
        overwrite: 是否覆蓋原檔案

    Returns:
        輸出檔案路徑
    """
    input_path = Path(input_path)

    # 開啟圖片
    img = Image.open(input_path)

    # 計算裁切區域（正方形）
    width, height = img.size
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim

    # 裁切為正方形
    img = img.crop((left, top, right, bottom))

    # 縮放到目標尺寸
    img = img.resize((size, size), Image.Resampling.LANCZOS)

    # 處理透明度
    if output_format == "jpeg":
        # JPEG 不支援透明，轉為 RGB
        if img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            if img.mode == "RGBA":
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img)
            img = background
    elif transparent_background and img.mode != "RGBA":
        img = img.convert("RGBA")

    # 決定輸出路徑
    ext = "jpg" if output_format == "jpeg" else "png"
    if overwrite:
        output_path = input_path.with_suffix(f".{ext}")
    else:
        output_path = input_path.parent / f"{input_path.stem}_{size}x{size}.{ext}"

    # 儲存
    save_format = "JPEG" if output_format == "jpeg" else "PNG"
    img.save(output_path, format=save_format, quality=92 if save_format == "JPEG" else None)

    return str(output_path)


def create_favicon_set(
    input_path: str,
    sizes: list[int] | None = None,
    output_dir: str | None = None,
) -> list[str]:
    """
    建立 favicon 組合

    Args:
        input_path: 輸入圖片路徑
        sizes: 尺寸列表（預設：16, 32, 48, 64, 128, 256）
        output_dir: 輸出目錄

    Returns:
        輸出檔案路徑列表
    """
    if sizes is None:
        sizes = [16, 32, 48, 64, 128, 256]

    input_path = Path(input_path)
    output_dir_path = Path(output_dir) if output_dir else input_path.parent

    output_files: list[str] = []

    for size in sizes:
        output_path = output_dir_path / f"favicon-{size}x{size}.png"

        img = Image.open(input_path)

        # 裁切為正方形
        width, height = img.size
        min_dim = min(width, height)
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        img = img.crop((left, top, left + min_dim, top + min_dim))

        # 縮放
        img = img.resize((size, size), Image.Resampling.LANCZOS)

        # 確保 RGBA
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        img.save(output_path, format="PNG")
        output_files.append(str(output_path))

    return output_files
