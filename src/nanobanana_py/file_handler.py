"""檔案處理模組"""

import base64
import hashlib
import os
import re
from datetime import datetime
from pathlib import Path


def get_output_directory() -> Path:
    """取得輸出目錄"""
    # 優先使用環境變數
    output_dir = os.getenv("NANOBANANA_OUTPUT_DIR")
    if output_dir:
        path = Path(output_dir)
    else:
        # 預設使用當前目錄下的 nanobanana-output 子目錄
        path = Path.cwd() / "nanobanana-output"

    path.mkdir(parents=True, exist_ok=True)
    return path


def generate_filename(
    prompt: str,
    file_format: str = "jpeg",
    index: int = 0,
    custom_filename: str | None = None,
    force_suffix: bool = False,
    suffix: str | None = None,
) -> str:
    """
    生成檔名

    Args:
        prompt: 圖片描述
        file_format: 圖片格式（png 或 jpeg）
        index: 索引（用於批次生成）
        custom_filename: 自訂檔名
        force_suffix: 強制加上後綴
        suffix: 自訂後綴
    """
    ext = "jpg" if file_format == "jpeg" else file_format

    if custom_filename:
        # 移除副檔名
        base_name = re.sub(r"\.(png|jpg|jpeg)$", "", custom_filename, flags=re.IGNORECASE)

        if suffix:
            return f"{base_name}_{suffix}.{ext}"
        elif force_suffix or index > 0:
            return f"{base_name}_{index + 1}.{ext}"
        else:
            return f"{base_name}.{ext}"

    # 從 prompt 生成檔名
    # 清理 prompt，只保留字母數字和空格
    clean_prompt = re.sub(r"[^\w\s]", "", prompt)
    clean_prompt = re.sub(r"\s+", "_", clean_prompt.strip())
    clean_prompt = clean_prompt[:50]  # 限制長度

    # 加上時間戳和 hash
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:6]

    if index > 0:
        return f"{clean_prompt}_{timestamp}_{prompt_hash}_{index + 1}.{ext}"
    else:
        return f"{clean_prompt}_{timestamp}_{prompt_hash}.{ext}"


def find_input_file(filename: str) -> tuple[bool, str | None, list[str]]:
    """
    尋找輸入檔案

    Args:
        filename: 檔名或路徑

    Returns:
        (found, file_path, searched_paths)
    """
    searched_paths: list[str] = []

    # 如果是絕對路徑
    if os.path.isabs(filename):
        searched_paths.append(filename)
        if os.path.exists(filename):
            return True, filename, searched_paths
        return False, None, searched_paths

    # 相對路徑：搜尋多個位置
    search_dirs = [
        Path.cwd(),  # 當前目錄
        get_output_directory(),  # 輸出目錄
        Path.home(),  # 家目錄
    ]

    for search_dir in search_dirs:
        file_path = search_dir / filename
        searched_paths.append(str(file_path))
        if file_path.exists():
            return True, str(file_path), searched_paths

    return False, None, searched_paths


def read_image_as_base64(file_path: str) -> str:
    """讀取圖片並轉為 base64"""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def save_image_buffer(buffer: bytes, output_dir: str | Path, filename: str) -> str:
    """
    儲存圖片

    Args:
        buffer: 圖片資料
        output_dir: 輸出目錄
        filename: 檔名

    Returns:
        完整路徑
    """
    output_path = Path(output_dir) if isinstance(output_dir, str) else output_dir
    file_path = output_path / filename
    file_path.write_bytes(buffer)
    return str(file_path)


def get_mime_type(file_path: str) -> str:
    """根據副檔名取得 MIME 類型"""
    ext = Path(file_path).suffix.lower()
    if ext == ".png":
        return "image/png"
    elif ext in (".jpg", ".jpeg"):
        return "image/jpeg"
    elif ext == ".gif":
        return "image/gif"
    elif ext == ".webp":
        return "image/webp"
    else:
        return "image/jpeg"  # 預設
