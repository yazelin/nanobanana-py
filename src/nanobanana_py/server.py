"""
nanobanana-py MCP Server

使用 fastmcp 框架實作的 Gemini 圖片生成 MCP 服務。
完整複製 nanobanana (TypeScript) 的所有功能。
"""

import json
import logging
from typing import Any

from fastmcp import FastMCP

from .icon_processor import process_icon_file
from .image_generator import ImageGenerator, validate_authentication
from .types import (
    EditImageArgs,
    GenerateDiagramArgs,
    GenerateIconArgs,
    GenerateImageArgs,
    GeneratePatternArgs,
    GenerateStoryArgs,
    ImageGenerationRequest,
    RestoreImageArgs,
)

# 設定 logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nanobanana")

# 建立 MCP Server
mcp = FastMCP(
    "nanobanana-py",
    instructions="Python MCP server for AI-powered image generation using Google Gemini models",
)

# 全域變數
_generator: ImageGenerator | None = None
_init_error: str | None = None


def get_generator() -> ImageGenerator:
    """取得或建立 ImageGenerator 實例"""
    global _generator, _init_error

    if _init_error:
        raise RuntimeError(_init_error)

    if _generator is None:
        try:
            auth_config = validate_authentication()
            _generator = ImageGenerator(auth_config)
        except Exception as e:
            _init_error = str(e)
            raise

    return _generator


def format_response(data: dict[str, Any]) -> str:
    """格式化回應為 JSON"""
    return json.dumps(data, indent=2, ensure_ascii=False)


# ============================================================
# Tool: generate_image
# ============================================================
@mcp.tool()
async def generate_image(
    prompt: str,
    files: list[str] | None = None,
    filename: str | None = None,
    output_count: int = 1,
    styles: list[str] | None = None,
    variations: list[str] | None = None,
    format: str = "separate",
    seed: int | None = None,
    preview: bool = False,
    resolution: str = "1K",
) -> str:
    """
    Generate single or multiple images from text prompts with style and variation options.

    Args:
        prompt: The text prompt describing the image to generate
        files: Optional array of reference image file paths (1-13 images)
        filename: Optional output filename
        output_count: Number of variations to generate (1-8, default: 1)
        styles: Array of artistic styles (photorealistic, watercolor, oil-painting, sketch, pixel-art, anime, vintage, modern, abstract, minimalist)
        variations: Array of variation types (lighting, angle, color-palette, composition, mood, season, time-of-day)
        format: Output format: separate files or single grid image (grid, separate)
        seed: Seed for reproducible variations
        preview: Automatically open generated images in default viewer
        resolution: Output image resolution (1K, 2K, 4K)
    """
    try:
        generator = get_generator()

        request = ImageGenerationRequest(
            prompt=prompt,
            reference_images=files,
            filename=filename,
            output_count=output_count,
            styles=styles,
            variations=variations,
            format=format,  # type: ignore
            seed=seed,
            preview=preview,
            resolution=resolution,  # type: ignore
            mode="generate",
        )

        response = await generator.generate_text_to_image(request)

        return format_response({
            "success": response.success,
            "tool": "generate_image",
            "message": response.message,
            "generatedFiles": response.generated_files,
            **({"error": response.error} if response.error else {}),
        })

    except Exception as e:
        return format_response({
            "success": False,
            "tool": "generate_image",
            "message": "Image generation failed",
            "error": str(e),
        })


# ============================================================
# Tool: edit_image
# ============================================================
@mcp.tool()
async def edit_image(
    prompt: str,
    file: str,
    filename: str | None = None,
    resolution: str = "1K",
    preview: bool = False,
) -> str:
    """
    Edit an existing image based on a text prompt.

    Args:
        prompt: The text prompt describing the edits to make
        file: The filename of the input image to edit
        filename: Optional output filename for the edited image
        resolution: Output image resolution (1K, 2K, 4K)
        preview: Automatically open generated images in default viewer
    """
    try:
        generator = get_generator()

        request = ImageGenerationRequest(
            prompt=prompt,
            input_image=file,
            filename=filename,
            resolution=resolution,  # type: ignore
            preview=preview,
            mode="edit",
        )

        response = await generator.edit_image(request)

        return format_response({
            "success": response.success,
            "tool": "edit_image",
            "message": response.message,
            "generatedFiles": response.generated_files,
            **({"error": response.error} if response.error else {}),
        })

    except Exception as e:
        return format_response({
            "success": False,
            "tool": "edit_image",
            "message": "Image editing failed",
            "error": str(e),
        })


# ============================================================
# Tool: restore_image
# ============================================================
@mcp.tool()
async def restore_image(
    prompt: str,
    file: str,
    filename: str | None = None,
    resolution: str = "1K",
    preview: bool = False,
) -> str:
    """
    Restore or enhance an existing image.

    Args:
        prompt: The text prompt describing the restoration to perform
        file: The filename of the input image to restore
        filename: Optional output filename for the restored image
        resolution: Output image resolution (1K, 2K, 4K)
        preview: Automatically open generated images in default viewer
    """
    try:
        generator = get_generator()

        request = ImageGenerationRequest(
            prompt=prompt,
            input_image=file,
            filename=filename,
            resolution=resolution,  # type: ignore
            preview=preview,
            mode="restore",
        )

        response = await generator.edit_image(request)

        return format_response({
            "success": response.success,
            "tool": "restore_image",
            "message": response.message,
            "generatedFiles": response.generated_files,
            **({"error": response.error} if response.error else {}),
        })

    except Exception as e:
        return format_response({
            "success": False,
            "tool": "restore_image",
            "message": "Image restoration failed",
            "error": str(e),
        })


# ============================================================
# Tool: generate_icon
# ============================================================
@mcp.tool()
async def generate_icon(
    prompt: str,
    files: list[str] | None = None,
    filename: str | None = None,
    sizes: list[int] | None = None,
    type: str = "app-icon",
    style: str = "modern",
    format: str = "png",
    background: str = "transparent",
    corners: str = "rounded",
    resolution: str = "1K",
    preview: bool = False,
) -> str:
    """
    Generate app icons, favicons, and UI elements in multiple sizes and formats.

    Args:
        prompt: Description of the icon or UI element to generate
        files: Optional array of reference image file paths (1-14 images)
        filename: Optional output filename
        sizes: Array of icon sizes in pixels (16, 32, 64, 128, 256, 512, 1024)
        type: Type of icon to generate (app-icon, favicon, ui-element)
        style: Visual style of the icon (flat, skeuomorphic, minimal, modern)
        format: Output format (png, jpeg)
        background: Background type (transparent, white, black, or color name)
        corners: Corner style for app icons (rounded, sharp)
        resolution: Output image resolution (1K, 2K, 4K)
        preview: Automatically open generated images in default viewer
    """
    try:
        generator = get_generator()

        # 建立 icon prompt
        icon_prompt = f"{prompt}, {style} style {type}"
        if type == "app-icon":
            icon_prompt += f", {corners} corners"
        if background != "transparent":
            icon_prompt += f", {background} background"
        icon_prompt += ", clean design, high quality, professional"

        # 決定輸出格式
        transparent_bg = background == "transparent"
        output_format = "png" if transparent_bg else format

        # 決定生成數量
        icon_sizes = sizes or [1024]
        output_count = len(icon_sizes)

        request = ImageGenerationRequest(
            prompt=icon_prompt,
            reference_images=files,
            filename=filename,
            output_count=output_count,
            file_format=output_format,  # type: ignore
            aspect_ratio="1:1",  # type: ignore
            resolution=resolution,  # type: ignore
            preview=preview,
            mode="generate",
        )

        response = await generator.generate_text_to_image(request)

        if response.success and response.generated_files:
            # 後處理：裁切和縮放
            original_files = response.generated_files.copy()
            processed_files: list[str] = []

            for i, input_path in enumerate(original_files):
                target_size = icon_sizes[i] if i < len(icon_sizes) else icon_sizes[0]
                output_path = process_icon_file(
                    input_path,
                    size=target_size,
                    transparent_background=transparent_bg,
                    output_format=output_format,
                    overwrite=False,
                )
                processed_files.append(output_path)

            response.generated_files = original_files + processed_files
            response.message += " (original images first, then cropped/resized icon outputs)"

        return format_response({
            "success": response.success,
            "tool": "generate_icon",
            "message": response.message,
            "generatedFiles": response.generated_files,
            **({"error": response.error} if response.error else {}),
        })

    except Exception as e:
        return format_response({
            "success": False,
            "tool": "generate_icon",
            "message": "Icon generation failed",
            "error": str(e),
        })


# ============================================================
# Tool: generate_pattern
# ============================================================
@mcp.tool()
async def generate_pattern(
    prompt: str,
    files: list[str] | None = None,
    filename: str | None = None,
    size: str = "256x256",
    type: str = "seamless",
    style: str = "abstract",
    density: str = "medium",
    colors: str = "colorful",
    repeat: str = "tile",
    resolution: str = "1K",
    preview: bool = False,
) -> str:
    """
    Generate seamless patterns and textures for backgrounds and design elements.

    Args:
        prompt: Description of the pattern or texture to generate
        files: Optional array of reference image file paths (1-14 images)
        filename: Optional output filename for the generated pattern
        size: Pattern tile size (e.g., "256x256", "512x512")
        type: Type of pattern to generate (seamless, texture, wallpaper)
        style: Pattern style (geometric, organic, abstract, floral, tech)
        density: Element density in the pattern (sparse, medium, dense)
        colors: Color scheme (mono, duotone, colorful)
        repeat: Tiling method for seamless patterns (tile, mirror)
        resolution: Output image resolution (1K, 2K, 4K)
        preview: Automatically open generated images in default viewer
    """
    try:
        generator = get_generator()

        # 建立 pattern prompt
        pattern_prompt = f"{prompt}, {style} style {type} pattern, {density} density, {colors} colors"
        if type == "seamless":
            pattern_prompt += ", tileable, repeating pattern"
        pattern_prompt += f", {size} tile size, high quality"

        request = ImageGenerationRequest(
            prompt=pattern_prompt,
            reference_images=files,
            filename=filename,
            output_count=1,
            resolution=resolution,  # type: ignore
            preview=preview,
            mode="generate",
        )

        response = await generator.generate_text_to_image(request)

        return format_response({
            "success": response.success,
            "tool": "generate_pattern",
            "message": response.message,
            "generatedFiles": response.generated_files,
            **({"error": response.error} if response.error else {}),
        })

    except Exception as e:
        return format_response({
            "success": False,
            "tool": "generate_pattern",
            "message": "Pattern generation failed",
            "error": str(e),
        })


# ============================================================
# Tool: generate_story
# ============================================================
@mcp.tool()
async def generate_story(
    prompt: str,
    files: list[str] | None = None,
    filename: str | None = None,
    steps: int = 4,
    type: str = "story",
    style: str = "consistent",
    layout: str = "separate",
    transition: str = "smooth",
    format: str = "individual",
    resolution: str = "1K",
    preview: bool = False,
) -> str:
    """
    Generate a sequence of related images that tell a visual story or show a process.

    Args:
        prompt: Description of the story or process to visualize
        files: Optional array of reference image file paths (1-14 images)
        filename: Optional output filename
        steps: Number of sequential images to generate (2-8)
        type: Type of sequence to generate (story, process, tutorial, timeline)
        style: Visual consistency across frames (consistent, evolving)
        layout: Output layout format (separate, grid, comic)
        transition: Transition style between steps (smooth, dramatic, fade)
        format: Output format (storyboard, individual)
        resolution: Output image resolution (1K, 2K, 4K)
        preview: Automatically open generated images in default viewer
    """
    try:
        generator = get_generator()

        request = ImageGenerationRequest(
            prompt=prompt,
            reference_images=files,
            filename=filename,
            output_count=steps,
            resolution=resolution,  # type: ignore
            preview=preview,
            mode="generate",
        )

        response = await generator.generate_story_sequence(
            request,
            story_type=type,
            style=style,
            transition=transition,
        )

        return format_response({
            "success": response.success,
            "tool": "generate_story",
            "message": response.message,
            "generatedFiles": response.generated_files,
            **({"error": response.error} if response.error else {}),
        })

    except Exception as e:
        return format_response({
            "success": False,
            "tool": "generate_story",
            "message": "Story generation failed",
            "error": str(e),
        })


# ============================================================
# Tool: generate_diagram
# ============================================================
@mcp.tool()
async def generate_diagram(
    prompt: str,
    files: list[str] | None = None,
    filename: str | None = None,
    type: str = "flowchart",
    style: str = "professional",
    layout: str = "hierarchical",
    complexity: str = "detailed",
    colors: str = "accent",
    annotations: str = "detailed",
    resolution: str = "1K",
    preview: bool = False,
) -> str:
    """
    Generate technical diagrams, flowcharts, and architectural mockups.

    Args:
        prompt: Description of the diagram content and structure
        files: Optional array of reference image file paths (1-14 images)
        filename: Optional output filename for the generated diagram
        type: Type of diagram to generate (flowchart, architecture, network, database, wireframe, mindmap, sequence)
        style: Visual style of the diagram (professional, clean, hand-drawn, technical)
        layout: Layout orientation (horizontal, vertical, hierarchical, circular)
        complexity: Level of detail in the diagram (simple, detailed, comprehensive)
        colors: Color scheme (mono, accent, categorical)
        annotations: Label and annotation level (minimal, detailed)
        resolution: Output image resolution (1K, 2K, 4K)
        preview: Automatically open generated images in default viewer
    """
    try:
        generator = get_generator()

        # 建立 diagram prompt
        diagram_prompt = f"{prompt}, {type} diagram, {style} style, {layout} layout"
        diagram_prompt += f", {complexity} level of detail, {colors} color scheme"
        diagram_prompt += f", {annotations} annotations and labels"
        diagram_prompt += ", clean technical illustration, clear visual hierarchy"

        request = ImageGenerationRequest(
            prompt=diagram_prompt,
            reference_images=files,
            filename=filename,
            output_count=1,
            resolution=resolution,  # type: ignore
            preview=preview,
            mode="generate",
        )

        response = await generator.generate_text_to_image(request)

        return format_response({
            "success": response.success,
            "tool": "generate_diagram",
            "message": response.message,
            "generatedFiles": response.generated_files,
            **({"error": response.error} if response.error else {}),
        })

    except Exception as e:
        return format_response({
            "success": False,
            "tool": "generate_diagram",
            "message": "Diagram generation failed",
            "error": str(e),
        })


def main() -> None:
    """啟動 MCP Server"""
    mcp.run()


if __name__ == "__main__":
    main()
