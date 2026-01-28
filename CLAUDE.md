# nanobanana-py 開發指南

## 語言
- 使用繁體中文回應
- 程式碼註解使用繁體中文

## 專案結構

```
nanobanana-py/
├── src/nanobanana_py/
│   ├── __init__.py
│   ├── server.py          # MCP Server 主程式（工具定義）
│   ├── image_generator.py # 圖片生成核心邏輯
│   ├── icon_processor.py  # Icon 後處理
│   ├── file_handler.py    # 檔案處理
│   └── types.py           # Pydantic 型別定義
├── pyproject.toml         # 套件設定
└── README.md
```

## 本地開發測試

```bash
# 進入專案目錄
cd ~/SDD/nanobanana-py

# 載入環境變數並執行
bash -c "set -a && source /home/ct/SDD/ching-tech-os/.env && set +a && uv run nanobanana-py"

# 或執行測試腳本
bash -c "set -a && source /home/ct/SDD/ching-tech-os/.env && set +a && uv run python /tmp/test_script.py"
```

## 環境變數

| 變數 | 說明 | 預設值 |
|-----|------|-------|
| `NANOBANANA_GEMINI_API_KEY` | Gemini API Key | (必填) |
| `NANOBANANA_MODEL` | 主要模型 | `gemini-2.5-flash-image` |
| `NANOBANANA_FALLBACK_MODELS` | 備用模型列表（逗號分隔） | `gemini-2.5-flash-image,gemini-2.0-flash-exp-image-generation` |
| `NANOBANANA_TIMEOUT` | API 超時秒數 | `60` |
| `NANOBANANA_OUTPUT_DIR` | 輸出目錄 | 當前目錄 |
| `NANOBANANA_DEBUG` | 啟用 debug 輸出 | (空) |

## MCP 配置

### 使用 PyPI 版本（正式環境）

```json
{
  "mcpServers": {
    "nanobanana": {
      "command": "bash",
      "args": [
        "-c",
        "set -a && source /home/ct/SDD/ching-tech-os/.env && set +a && uvx nanobanana-py"
      ]
    }
  }
}
```

### 使用本地版本（開發測試）

```json
{
  "mcpServers": {
    "nanobanana": {
      "command": "bash",
      "args": [
        "-c",
        "set -a && source /home/ct/SDD/ching-tech-os/.env && set +a && cd /home/ct/SDD/nanobanana-py && uv run nanobanana-py"
      ]
    }
  }
}
```

## 測試

修改程式碼後，必須確保所有測試通過：

```bash
cd ~/SDD/nanobanana-py
uv run pytest tests/ -v
```

**重要**：
- 所有測試必須通過才能 commit/發佈
- 新增功能時應同步新增對應的測試
- CI/CD 會自動執行測試，失敗會阻擋發佈

測試結構：
```
tests/
├── conftest.py                  # 共用 fixtures
├── test_types.py                # 型別定義測試
├── test_file_handler.py         # 檔案處理測試
├── test_icon_processor.py       # Icon 處理測試
├── test_image_generator.py      # 認證/超時測試
└── test_image_generator_mock.py # 圖片生成邏輯測試（模擬 API）
```

## 發佈流程

### 1. 修改程式碼並測試

```bash
# 執行測試
cd ~/SDD/nanobanana-py
uv run pytest tests/ -v

# 語法檢查
uv run python -c "from nanobanana_py.server import mcp; print('OK')"
```

### 2. 更新版本號

修改 `pyproject.toml` 中的 `version`：
```toml
version = "0.x.x"
```

### 3. Commit 並 Push

```bash
cd ~/SDD/nanobanana-py

# 加入修改的檔案
git add src/nanobanana_py/*.py pyproject.toml README.md

# Commit
git commit -m "feat: 功能描述

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

# Push
git push origin main
```

### 4. 建立 Tag 並 Push

```bash
git tag v0.x.x
git push origin v0.x.x
```

### 5. 建立 GitHub Release（觸發自動發佈到 PyPI）

```bash
gh release create v0.x.x --title "v0.x.x - 標題" --notes "Release notes..."
```

或在 GitHub 網頁上建立 Release。

### 6. 確認 PyPI 發佈成功

```bash
# 檢查 GitHub Actions 狀態
gh run list --limit 1

# 確認 PyPI 版本
curl -s "https://pypi.org/pypi/nanobanana-py/json" | jq -r '.releases | keys | .[-1]'
```

### 7. 更新 MCP 配置（如果之前用本地版本測試）

將 `.mcp.json` 改回使用 `uvx nanobanana-py`，然後重啟 Claude Code。

## 可用的 Gemini 圖像生成模型

查詢可用模型：
```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$NANOBANANA_GEMINI_API_KEY" | \
  jq '.models[] | select(.name | contains("image")) | {name, displayName}'
```

目前可用：
- `gemini-2.5-flash-image` - Nano Banana（穩定）
- `gemini-3-pro-image-preview` - Nano Banana Pro（較慢但品質高）
- `gemini-2.0-flash-exp-image-generation` - 實驗版本
