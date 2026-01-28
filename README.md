# nanobanana-py

Python MCP Server，使用 Google Gemini 模型進行 AI 圖片生成。

完整移植自 [nanobanana](https://github.com/doggy8088/nanobanana)（TypeScript 版）。

## ✨ 功能特色

- **🎨 文字轉圖片生成**：依照描述式提示詞生成高品質圖片
- **✏️ 圖片編修**：用自然語言指令修改既有圖片
- **🔧 圖片修復**：修復並強化老舊或受損照片
- **🏷️ 圖示生成**：生成多尺寸的 App 圖示、Favicon 與 UI 元件
- **🎯 圖樣生成**：生成可無縫拼接的圖樣與背景材質
- **📖 故事序列**：生成可呈現視覺故事或流程的連續圖片
- **📊 技術圖表**：生成流程圖、架構圖與技術示意圖
- **🔄 自動 Fallback**：主模型失敗時自動切換備用模型
- **⚡ 批次生成**：支援平行生成多張圖片

## 📋 前置需求

1. **Python 3.10+**
2. **API Key**：設定下列任一環境變數：
   - `NANOBANANA_GEMINI_API_KEY`（建議）
   - `NANOBANANA_GOOGLE_API_KEY`
   - `GEMINI_API_KEY`（備援）
   - `GOOGLE_API_KEY`（備援）

從 [Google AI Studio](https://aistudio.google.com/apikey) 取得 API Key。

## 🚀 安裝

### 透過 uvx（推薦）

```bash
uvx nanobanana-py
```

### 透過 pip

```bash
pip install nanobanana-py
```

### 透過 pipx

```bash
pipx install nanobanana-py
```

## ⚙️ 設定

### 環境變數

```bash
# API Key（必要）
export NANOBANANA_GEMINI_API_KEY="your-api-key-here"

# 使用不同模型（預設：gemini-2.5-flash-image）
export NANOBANANA_MODEL="gemini-3-pro-image-preview"

# Fallback 模型（逗號分隔，主模型失敗時依序嘗試）
export NANOBANANA_FALLBACK_MODELS="gemini-2.5-flash-image,gemini-2.0-flash-exp-image-generation"

# API 超時秒數（預設：60）
export NANOBANANA_TIMEOUT="90"

# 自訂輸出目錄（預設：當前目錄）
export NANOBANANA_OUTPUT_DIR="/path/to/output"

# 啟用除錯日誌
export NANOBANANA_DEBUG="1"
```

### 🍌 模型選擇

此工具支援兩種模型：

| 模型 | 說明 | 特性 |
|------|------|------|
| `gemini-2.5-flash-image` | 預設模型 | 快速、穩定 |
| `gemini-3-pro-image-preview` | Pro 模型 | 高品質、支援 2K/4K |

### 🔄 自動 Fallback 機制

當主模型失敗（超時、過載或錯誤）時，會自動切換到備用模型。回應中會包含 fallback 資訊：

```json
{
  "success": true,
  "message": "Successfully generated 1 image (使用備用模型: gemini-2.5-flash-image，原本: gemini-3-pro-image-preview)",
  "modelUsed": "gemini-2.5-flash-image",
  "usedFallback": true,
  "primaryModel": "gemini-3-pro-image-preview"
}
```

### Claude Code 整合

在 `.mcp.json` 中加入：

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

## 💡 使用方式

### 🎨 generate_image - 生成圖片

從文字描述生成單張或多張圖片。

**參數：**

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `prompt` | string | （必填） | 圖片描述 |
| `files` | array | - | 參考圖片路徑（1-13 張） |
| `filename` | string | - | 輸出檔名 |
| `output_count` | int | 1 | 生成數量（1-8） |
| `styles` | array | - | 藝術風格 |
| `variations` | array | - | 變化類型 |
| `format` | string | "separate" | 輸出格式（grid / separate） |
| `seed` | int | - | 隨機種子（用於重現結果） |
| `resolution` | string | "1K" | 解析度（1K / 2K / 4K） |
| `preview` | bool | false | 自動預覽 |
| `no_preview` | bool | false | 強制禁用預覽 |
| `parallel` | int | 2 | 平行生成數量（1-8） |

**可用風格（styles）：**

- `photorealistic` - 寫實攝影風格
- `watercolor` - 水彩畫風
- `oil-painting` - 油畫技法
- `sketch` - 手繪素描風
- `pixel-art` - 復古像素風
- `anime` - 動漫/漫畫風
- `vintage` - 復古/懷舊美學
- `modern` - 當代/現代風格
- `abstract` - 抽象藝術風
- `minimalist` - 乾淨、極簡設計

**可用變化類型（variations）：**

- `lighting` - 不同光線條件（戲劇化、柔和）
- `angle` - 不同視角（俯視、特寫）
- `color-palette` - 不同配色（暖色、冷色）
- `composition` - 不同構圖（置中、三分法）
- `mood` - 不同情緒氛圍（愉快、戲劇化）
- `season` - 不同季節（春、冬）
- `time-of-day` - 不同時段（日出、日落）

**範例：**

```python
# 單張圖片
generate_image(prompt="一幅水彩畫：雪地森林裡的狐狸")

# 多張變體（含預覽）
generate_image(prompt="群山日落", output_count=3, preview=True)

# 指定輸出檔名
generate_image(prompt="群山日落", output_count=3, filename="sunset_mountains")

# 風格變體
generate_image(
    prompt="山景風光",
    styles=["watercolor", "oil-painting"],
    output_count=4
)

# 指定變化類型
generate_image(
    prompt="咖啡店室內",
    variations=["lighting", "mood"],
    preview=True
)
```

---

### ✏️ edit_image - 編修圖片

用自然語言指令修改既有圖片。

**參數：**

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `prompt` | string | （必填） | 編輯描述 |
| `file` | string | （必填） | 輸入圖片路徑 |
| `filename` | string | - | 輸出檔名 |
| `resolution` | string | "1K" | 解析度（1K / 2K / 4K） |
| `preview` | bool | false | 自動預覽 |
| `no_preview` | bool | false | 強制禁用預覽 |
| `parallel` | int | 2 | 平行生成數量（1-8） |

**範例：**

```python
# 基本編修
edit_image(file="my_photo.png", prompt="幫人物加上太陽眼鏡")

# 指定輸出檔名
edit_image(
    file="my_photo.png",
    prompt="幫人物加上太陽眼鏡",
    filename="with_sunglasses"
)

# 編修並預覽
edit_image(
    file="portrait.jpg",
    prompt="把背景改成海灘",
    preview=True
)
```

---

### 🔧 restore_image - 修復圖片

修復並強化老舊或受損照片。

**參數：**

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `prompt` | string | （必填） | 修復描述 |
| `file` | string | （必填） | 輸入圖片路徑 |
| `filename` | string | - | 輸出檔名 |
| `resolution` | string | "1K" | 解析度（1K / 2K / 4K） |
| `preview` | bool | false | 自動預覽 |
| `no_preview` | bool | false | 強制禁用預覽 |
| `parallel` | int | 2 | 平行生成數量（1-8） |

**範例：**

```python
# 移除刮痕
restore_image(
    file="old_family_photo.jpg",
    prompt="移除刮痕並提升清晰度"
)

# 增強色彩
restore_image(
    file="damaged_photo.png",
    prompt="增強色彩並修補撕裂",
    preview=True
)
```

---

### 🎯 generate_icon - 生成圖示

生成多尺寸的 App 圖示、Favicon 與 UI 元件。

**參數：**

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `prompt` | string | （必填） | 圖示描述 |
| `files` | array | - | 參考圖片路徑（1-14 張） |
| `filename` | string | - | 輸出檔名 |
| `sizes` | array | [1024] | 尺寸（16, 32, 64, 128, 256, 512, 1024） |
| `type` | string | "app-icon" | 類型（app-icon / favicon / ui-element） |
| `style` | string | "modern" | 風格（flat / skeuomorphic / minimal / modern） |
| `format` | string | "png" | 格式（png / jpeg） |
| `background` | string | "transparent" | 背景（transparent / white / black） |
| `corners` | string | "rounded" | 圓角（rounded / sharp） |
| `resolution` | string | "1K" | 解析度（1K / 2K / 4K） |
| `preview` | bool | false | 自動預覽 |
| `no_preview` | bool | false | 強制禁用預覽 |
| `parallel` | int | 2 | 平行生成數量（1-8） |

**範例：**

```python
# 多尺寸 App 圖示
generate_icon(
    prompt="咖啡杯 logo",
    sizes=[64, 128, 256],
    type="app-icon",
    preview=True
)

# Favicon 組合
generate_icon(
    prompt="公司 logo",
    type="favicon",
    sizes=[16, 32, 64]
)

# UI 元件
generate_icon(
    prompt="設定齒輪圖示",
    type="ui-element",
    style="minimal"
)
```

---

### 🎨 generate_pattern - 生成圖樣

生成可無縫拼接的圖樣與背景材質。

**參數：**

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `prompt` | string | （必填） | 圖樣描述 |
| `files` | array | - | 參考圖片路徑（1-14 張） |
| `filename` | string | - | 輸出檔名 |
| `size` | string | "256x256" | 尺寸（128x128, 256x256, 512x512） |
| `type` | string | "seamless" | 類型（seamless / texture / wallpaper） |
| `style` | string | "abstract" | 風格（geometric / organic / abstract / floral / tech） |
| `density` | string | "medium" | 密度（sparse / medium / dense） |
| `colors` | string | "colorful" | 配色（mono / duotone / colorful） |
| `repeat` | string | "tile" | 重複方式（tile / mirror） |
| `resolution` | string | "1K" | 解析度（1K / 2K / 4K） |
| `preview` | bool | false | 自動預覽 |
| `no_preview` | bool | false | 強制禁用預覽 |
| `parallel` | int | 2 | 平行生成數量（1-8） |

**範例：**

```python
# 無縫拼接圖樣
generate_pattern(
    prompt="幾何三角形",
    type="seamless",
    style="geometric",
    preview=True
)

# 背景材質
generate_pattern(
    prompt="木紋材質",
    type="texture",
    colors="mono"
)

# 桌布圖樣
generate_pattern(
    prompt="花卉設計",
    type="wallpaper",
    density="sparse"
)
```

---

### 📖 generate_story - 生成故事序列

生成連續圖片，用於說故事或呈現逐步流程。

**參數：**

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `prompt` | string | （必填） | 故事描述 |
| `files` | array | - | 參考圖片路徑（1-14 張） |
| `filename` | string | - | 輸出檔名 |
| `steps` | int | 4 | 步驟數（2-8） |
| `type` | string | "story" | 類型（story / process / tutorial / timeline） |
| `style` | string | "consistent" | 風格一致性（consistent / evolving） |
| `layout` | string | "separate" | 版面（separate / grid / comic） |
| `transition` | string | "smooth" | 過渡效果（smooth / dramatic / fade） |
| `format` | string | "individual" | 格式（storyboard / individual） |
| `resolution` | string | "1K" | 解析度（1K / 2K / 4K） |
| `preview` | bool | false | 自動預覽 |
| `no_preview` | bool | false | 強制禁用預覽 |
| `parallel` | int | 2 | 平行生成數量（1-8） |

**範例：**

```python
# 視覺故事序列
generate_story(
    prompt="一顆種子長成樹",
    steps=4,
    type="process",
    preview=True
)

# 逐步教學
generate_story(
    prompt="如何煮咖啡",
    steps=6,
    type="tutorial"
)

# 時間軸視覺化
generate_story(
    prompt="智慧型手機的演進",
    steps=5,
    type="timeline"
)
```

---

### 📊 generate_diagram - 生成技術圖表

生成專業的技術圖表、流程圖與架構示意。

**參數：**

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `prompt` | string | （必填） | 圖表描述 |
| `files` | array | - | 參考圖片路徑（1-14 張） |
| `filename` | string | - | 輸出檔名 |
| `type` | string | "flowchart" | 類型（見下方） |
| `style` | string | "professional" | 風格（professional / clean / hand-drawn / technical） |
| `layout` | string | "hierarchical" | 版面（horizontal / vertical / hierarchical / circular） |
| `complexity` | string | "detailed" | 複雜度（simple / detailed / comprehensive） |
| `colors` | string | "accent" | 配色（mono / accent / categorical） |
| `annotations` | string | "detailed" | 標註（minimal / detailed） |
| `resolution` | string | "1K" | 解析度（1K / 2K / 4K） |
| `preview` | bool | false | 自動預覽 |
| `no_preview` | bool | false | 強制禁用預覽 |
| `parallel` | int | 2 | 平行生成數量（1-8） |

**圖表類型（type）：**

| 類型 | 說明 |
|------|------|
| `flowchart` | 流程、決策樹、工作流程 |
| `architecture` | 系統架構、微服務、基礎設施 |
| `network` | 網路拓樸、伺服器配置 |
| `database` | 資料庫結構、實體關係 |
| `wireframe` | UI/UX 線框稿、頁面配置 |
| `mindmap` | 心智圖、概念層級 |
| `sequence` | 時序圖、API 互動 |

**範例：**

```python
# 系統流程圖
generate_diagram(
    prompt="使用者登入流程",
    type="flowchart",
    style="professional",
    preview=True
)

# 系統架構圖
generate_diagram(
    prompt="微服務架構",
    type="architecture",
    complexity="detailed"
)

# 資料庫結構
generate_diagram(
    prompt="電商資料庫設計",
    type="database",
    layout="hierarchical"
)
```

---

## 📁 檔案管理

### 智慧檔名生成

圖片會依據提示詞以友善檔名儲存：

- `"sunset over mountains"` → `sunset_over_mountains_20240101_123456_abc123.jpg`
- `"abstract art piece"` → `abstract_art_piece_20240101_123456_def456.jpg`

### 自訂檔名

使用 `filename` 參數可指定輸出檔名：

- 單張：`filename="mountain_view"` → `mountain_view.jpg`
- 多張：`filename="mountain_view"` + `output_count=3` → `mountain_view_1.jpg`, `mountain_view_2.jpg`, `mountain_view_3.jpg`

### 檔案搜尋位置

進行編修/修復時，會在以下位置搜尋輸入圖片：

1. 目前工作目錄
2. 輸出目錄（`NANOBANANA_OUTPUT_DIR`）
3. 使用者家目錄

### 輸出目錄

生成圖片會儲存到：

1. `NANOBANANA_OUTPUT_DIR` 環境變數指定的目錄（如有設定）
2. 目前工作目錄（預設）

---

## 🛠️ 開發

```bash
# Clone 儲存庫
git clone https://github.com/aspect-apps/nanobanana-py.git
cd nanobanana-py

# 安裝依賴
uv sync

# 安裝開發依賴
uv sync --extra dev

# 執行測試
uv run pytest

# 格式化程式碼
uv run ruff format src/
uv run ruff check src/ --fix
```

---

## 🐛 疑難排解

### 常見問題

1. **「No API key found」**

   請設定 `NANOBANANA_GEMINI_API_KEY` 環境變數：

   ```bash
   export NANOBANANA_GEMINI_API_KEY="your-api-key-here"
   ```

2. **「Model timeout」或「Model overloaded」**

   - 稍後再試，或
   - 設定 `NANOBANANA_MODEL` 使用其他模型
   - 自動 fallback 機制會嘗試切換備用模型

3. **「Image not found」**

   確認輸入檔案位於支援的搜尋目錄（見「檔案搜尋位置」）

4. **圖片生成到錯誤目錄**

   設定 `NANOBANANA_OUTPUT_DIR` 環境變數指定輸出目錄：

   ```bash
   export NANOBANANA_OUTPUT_DIR="/path/to/output"
   ```

### 除錯模式

啟用除錯日誌以診斷問題：

```bash
export NANOBANANA_DEBUG="1"
```

---

## 📄 授權

MIT

## 🤝 致謝

- 原版 [nanobanana](https://github.com/doggy8088/nanobanana) by Will 保哥
- 使用 [FastMCP](https://github.com/jlowin/fastmcp) 框架
