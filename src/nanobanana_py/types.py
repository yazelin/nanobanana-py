"""型別定義"""

from typing import Literal

from pydantic import BaseModel, Field

# 解析度類型
ImageResolution = Literal["1K", "2K", "4K"]

# 長寬比類型
AspectRatio = Literal[
    "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"
]

# 圖片格式
ImageFormat = Literal["png", "jpeg"]

# 輸出格式
OutputFormat = Literal["grid", "separate"]


class ImageGenerationRequest(BaseModel):
    """圖片生成請求"""

    prompt: str
    input_image: str | None = None
    reference_images: list[str] | None = None
    output_count: int = 1
    mode: Literal["generate", "edit", "restore"] = "generate"
    styles: list[str] | None = None
    variations: list[str] | None = None
    format: OutputFormat = "separate"
    file_format: ImageFormat = "jpeg"
    seed: int | None = None
    resolution: ImageResolution = "1K"
    aspect_ratio: AspectRatio | None = None
    parallel: int = 2
    preview: bool = False
    no_preview: bool = False
    filename: str | None = None
    filename_suffixes: list[str] | None = None


class ImageGenerationResponse(BaseModel):
    """圖片生成回應"""

    success: bool
    message: str
    generated_files: list[str] = Field(default_factory=list)
    error: str | None = None
    # Fallback 資訊
    model_used: str | None = None  # 實際使用的模型
    used_fallback: bool = False  # 是否使用了 fallback 模型
    primary_model: str | None = None  # 原本設定的主要模型（當 used_fallback=True 時）


class AuthConfig(BaseModel):
    """認證設定"""

    api_key: str
    key_type: Literal["GEMINI_API_KEY", "GOOGLE_API_KEY"] = "GEMINI_API_KEY"


# Tool 參數模型
class GenerateImageArgs(BaseModel):
    """generate_image 工具參數"""

    prompt: str = Field(description="圖片描述")
    files: list[str] | None = Field(default=None, description="參考圖片路徑（1-13 張）")
    filename: str | None = Field(default=None, description="輸出檔名")
    output_count: int = Field(default=1, ge=1, le=8, description="生成數量（1-8）")
    styles: list[str] | None = Field(
        default=None,
        description="風格：photorealistic, watercolor, oil-painting, sketch, pixel-art, anime, vintage, modern, abstract, minimalist",
    )
    variations: list[str] | None = Field(
        default=None,
        description="變化：lighting, angle, color-palette, composition, mood, season, time-of-day",
    )
    format: OutputFormat = Field(default="separate", description="輸出格式：grid 或 separate")
    seed: int | None = Field(default=None, description="隨機種子")
    preview: bool = Field(default=False, description="自動預覽")
    resolution: ImageResolution = Field(default="1K", description="解析度：1K, 2K, 4K")


class EditImageArgs(BaseModel):
    """edit_image 工具參數"""

    prompt: str = Field(description="編輯描述")
    file: str = Field(description="輸入圖片路徑")
    filename: str | None = Field(default=None, description="輸出檔名")
    resolution: ImageResolution = Field(default="1K", description="解析度")
    preview: bool = Field(default=False, description="自動預覽")


class RestoreImageArgs(BaseModel):
    """restore_image 工具參數"""

    prompt: str = Field(description="修復描述")
    file: str = Field(description="輸入圖片路徑")
    filename: str | None = Field(default=None, description="輸出檔名")
    resolution: ImageResolution = Field(default="1K", description="解析度")
    preview: bool = Field(default=False, description="自動預覽")


class GenerateIconArgs(BaseModel):
    """generate_icon 工具參數"""

    prompt: str = Field(description="圖示描述")
    files: list[str] | None = Field(default=None, description="參考圖片路徑（1-14 張）")
    filename: str | None = Field(default=None, description="輸出檔名")
    sizes: list[int] | None = Field(
        default=None, description="尺寸（16, 32, 64, 128, 256, 512, 1024）"
    )
    type: Literal["app-icon", "favicon", "ui-element"] = Field(
        default="app-icon", description="類型"
    )
    style: Literal["flat", "skeuomorphic", "minimal", "modern"] = Field(
        default="modern", description="風格"
    )
    format: ImageFormat = Field(default="png", description="格式")
    background: str = Field(default="transparent", description="背景")
    corners: Literal["rounded", "sharp"] = Field(default="rounded", description="圓角")
    resolution: ImageResolution = Field(default="1K", description="解析度")
    preview: bool = Field(default=False, description="自動預覽")


class GeneratePatternArgs(BaseModel):
    """generate_pattern 工具參數"""

    prompt: str = Field(description="圖案描述")
    files: list[str] | None = Field(default=None, description="參考圖片路徑（1-14 張）")
    filename: str | None = Field(default=None, description="輸出檔名")
    size: str = Field(default="256x256", description="尺寸")
    type: Literal["seamless", "texture", "wallpaper"] = Field(
        default="seamless", description="類型"
    )
    style: Literal["geometric", "organic", "abstract", "floral", "tech"] = Field(
        default="abstract", description="風格"
    )
    density: Literal["sparse", "medium", "dense"] = Field(default="medium", description="密度")
    colors: Literal["mono", "duotone", "colorful"] = Field(default="colorful", description="色彩")
    repeat: Literal["tile", "mirror"] = Field(default="tile", description="重複方式")
    resolution: ImageResolution = Field(default="1K", description="解析度")
    preview: bool = Field(default=False, description="自動預覽")


class GenerateStoryArgs(BaseModel):
    """generate_story 工具參數"""

    prompt: str = Field(description="故事描述")
    files: list[str] | None = Field(default=None, description="參考圖片路徑（1-14 張）")
    filename: str | None = Field(default=None, description="輸出檔名")
    steps: int = Field(default=4, ge=2, le=8, description="步驟數（2-8）")
    type: Literal["story", "process", "tutorial", "timeline"] = Field(
        default="story", description="類型"
    )
    style: Literal["consistent", "evolving"] = Field(default="consistent", description="風格一致性")
    layout: Literal["separate", "grid", "comic"] = Field(default="separate", description="版面")
    transition: Literal["smooth", "dramatic", "fade"] = Field(
        default="smooth", description="過渡效果"
    )
    format: Literal["storyboard", "individual"] = Field(default="individual", description="格式")
    resolution: ImageResolution = Field(default="1K", description="解析度")
    preview: bool = Field(default=False, description="自動預覽")


class GenerateDiagramArgs(BaseModel):
    """generate_diagram 工具參數"""

    prompt: str = Field(description="圖表描述")
    files: list[str] | None = Field(default=None, description="參考圖片路徑（1-14 張）")
    filename: str | None = Field(default=None, description="輸出檔名")
    type: Literal[
        "flowchart", "architecture", "network", "database", "wireframe", "mindmap", "sequence"
    ] = Field(default="flowchart", description="類型")
    style: Literal["professional", "clean", "hand-drawn", "technical"] = Field(
        default="professional", description="風格"
    )
    layout: Literal["horizontal", "vertical", "hierarchical", "circular"] = Field(
        default="hierarchical", description="版面"
    )
    complexity: Literal["simple", "detailed", "comprehensive"] = Field(
        default="detailed", description="複雜度"
    )
    colors: Literal["mono", "accent", "categorical"] = Field(default="accent", description="色彩")
    annotations: Literal["minimal", "detailed"] = Field(default="detailed", description="標註")
    resolution: ImageResolution = Field(default="1K", description="解析度")
    preview: bool = Field(default=False, description="自動預覽")
