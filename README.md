# nanobanana-py

Python MCP server for AI-powered image generation using Google Gemini models.

A complete port of [nanobanana](https://github.com/doggy8088/nanobanana) (TypeScript) to Python.

## Features

- **7 Image Generation Tools**:
  - `generate_image` - Text to image with styles and variations
  - `edit_image` - Edit existing images
  - `restore_image` - Restore/enhance images
  - `generate_icon` - App icons, favicons, UI elements
  - `generate_pattern` - Seamless patterns and textures
  - `generate_story` - Sequential story images
  - `generate_diagram` - Technical diagrams and flowcharts

- **Dual Model Support**: Flash (fast) and Pro (high quality)
- **Batch Generation**: Generate multiple variations in parallel
- **Reference Images**: Use existing images as references
- **Multiple Resolutions**: 1K, 2K, 4K output options

## Installation

### Via uvx (Recommended)

```bash
uvx nanobanana-py
```

### Via pip

```bash
pip install nanobanana-py
```

### Via pipx

```bash
pipx install nanobanana-py
```

## Configuration

### Environment Variable

Get your API key from [Google AI Studio](https://aistudio.google.com/apikey).

```bash
export NANOBANANA_GEMINI_API_KEY="your-api-key-here"
```

### Optional Environment Variables

```bash
# Use a different model (default: gemini-2.5-flash-image)
export NANOBANANA_MODEL="gemini-3-pro-image-preview"

# Set custom output directory
export NANOBANANA_OUTPUT_DIR="/path/to/output"

# Enable debug logging
export NANOBANANA_DEBUG="1"
```

### Claude Code Integration

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "nanobanana": {
      "command": "uvx",
      "args": ["nanobanana-py"],
      "env": {
        "NANOBANANA_GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Or with local installation:

```json
{
  "mcpServers": {
    "nanobanana": {
      "command": "nanobanana-py"
    }
  }
}
```

## Tools

### generate_image

Generate single or multiple images from text prompts.

**Parameters:**
- `prompt` (required): Image description
- `files`: Reference image paths (1-13)
- `filename`: Output filename
- `output_count`: Number of variations (1-8)
- `styles`: Artistic styles (photorealistic, watercolor, sketch, etc.)
- `variations`: Variation types (lighting, angle, mood, etc.)
- `format`: Output format (grid, separate)
- `seed`: Seed for reproducibility
- `resolution`: 1K, 2K, or 4K
- `preview`: Auto-open in viewer

### edit_image

Edit an existing image based on a text prompt.

**Parameters:**
- `prompt` (required): Edit description
- `file` (required): Input image path
- `filename`: Output filename
- `resolution`: 1K, 2K, or 4K
- `preview`: Auto-open in viewer

### restore_image

Restore or enhance an existing image.

**Parameters:**
- `prompt` (required): Restoration description
- `file` (required): Input image path
- `filename`: Output filename
- `resolution`: 1K, 2K, or 4K
- `preview`: Auto-open in viewer

### generate_icon

Generate app icons in multiple sizes.

**Parameters:**
- `prompt` (required): Icon description
- `sizes`: Icon sizes (16, 32, 64, 128, 256, 512, 1024)
- `type`: app-icon, favicon, ui-element
- `style`: flat, skeuomorphic, minimal, modern
- `format`: png, jpeg
- `background`: transparent, white, black
- `corners`: rounded, sharp

### generate_pattern

Generate seamless patterns and textures.

**Parameters:**
- `prompt` (required): Pattern description
- `size`: Tile size (e.g., "256x256")
- `type`: seamless, texture, wallpaper
- `style`: geometric, organic, abstract, floral, tech
- `density`: sparse, medium, dense
- `colors`: mono, duotone, colorful
- `repeat`: tile, mirror

### generate_story

Generate a sequence of related images.

**Parameters:**
- `prompt` (required): Story description
- `steps`: Number of images (2-8)
- `type`: story, process, tutorial, timeline
- `style`: consistent, evolving
- `transition`: smooth, dramatic, fade

### generate_diagram

Generate technical diagrams and flowcharts.

**Parameters:**
- `prompt` (required): Diagram description
- `type`: flowchart, architecture, network, database, wireframe, mindmap, sequence
- `style`: professional, clean, hand-drawn, technical
- `layout`: horizontal, vertical, hierarchical, circular
- `complexity`: simple, detailed, comprehensive

## Development

```bash
# Clone the repository
git clone https://github.com/aspect-apps/nanobanana-py.git
cd nanobanana-py

# Install dependencies
uv sync

# Install with dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Format code
uv run ruff format src/
uv run ruff check src/ --fix
```

## License

MIT

## Credits

- Original [nanobanana](https://github.com/doggy8088/nanobanana) by Will 保哥
- Built with [FastMCP](https://github.com/jlowin/fastmcp)
