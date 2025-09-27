# Claude Code Playwright MCP 配置指南

## 概述

本文檔說明如何為 Claude Code 添加 Playwright MCP（Model Context Protocol）功能，讓 Claude 能夠直接在對話中控制瀏覽器進行自動化測試和網頁交互。

## 前置需求

- Node.js 和 npm 已安裝
- Claude Code 已安裝並可正常使用

## 安裝步驟

### 1. 安裝 Playwright MCP 包

```bash
# 全局安裝 Microsoft 官方 Playwright MCP 包
npm install -g @playwright/mcp
```

### 2. 配置 Claude Code MCP 服務器

```bash
# 添加 Playwright MCP 服務器到 Claude Code
claude mcp add playwright "npx @playwright/mcp@latest"
```

執行成功後會看到類似以下訊息：
```
Added stdio MCP server playwright with command: npx @playwright/mcp@latest to local config
File modified: C:\Users\user\.claude.json [project: 當前項目路徑]
```

### 3. 安裝瀏覽器驅動（可選）

```bash
# 安裝 Playwright 瀏覽器驅動
npx playwright install
```

> **注意**: 瀏覽器驅動會在首次使用時自動下載，但提前安裝可以避免首次使用時的等待。

## 配置驗證

### 檢查配置文件

配置會保存在 `~/.claude.json` 文件中，針對當前項目目錄。您可以檢查配置是否正確：

```bash
# 檢查配置文件中的 Playwright 配置
grep -A 10 "playwright" ~/.claude.json
```

應該會看到類似的配置：
```json
"mcpServers": {
  "playwright": {
    "type": "stdio",
    "command": "npx @playwright/mcp@latest",
    "args": [],
    "env": {}
  }
}
```

## 使用方法

### 重啟 Claude Code

配置完成後，需要完全關閉並重新啟動 Claude Code 讓配置生效。

### 基本使用語法

在與 Claude 的對話中，使用以下語法來調用 Playwright MCP：

```
Use playwright mcp to [你的指令]
```

### 使用範例

1. **打開網頁**:
   ```
   Use playwright mcp to open a browser to example.com
   ```

2. **截圖**:
   ```
   Use playwright mcp to take a screenshot of google.com
   ```

3. **填寫表單**:
   ```
   Use playwright mcp to fill out the login form on example.com
   ```

4. **點擊元素**:
   ```
   Use playwright mcp to click the submit button on the current page
   ```

## 高級配置選項

### 可用的命令行參數

在配置 MCP 服務器時，可以添加以下參數到 `args` 陣列中：

- `--browser <browser>`: 指定瀏覽器類型 (chrome, firefox, webkit, msedge)
- `--headless`: 以無頭模式運行瀏覽器
- `--allowed-hosts <hosts...>`: 設定允許訪問的域名列表
- `--caps <caps>`: 啟用額外功能 (vision, pdf)

### 自定義配置範例

```bash
# 配置為使用 Firefox 瀏覽器，並啟用視覺功能
claude mcp add playwright "npx @playwright/mcp@latest" --browser firefox --caps vision
```

## 替代方案

除了 Microsoft 官方版本外，還有其他 Playwright MCP 實現：

### ExecuteAutomation 版本

```bash
npm install -g @executeautomation/playwright-mcp-server
claude mcp add playwright "npx @executeautomation/playwright-mcp-server"
```

## 使用提示

### 認證處理

- 瀏覽器會以可見模式運行，方便進行手動認證
- 當需要登入網站時，可以自己手動登入，然後告訴 Claude 接下來要做什麼
- Cookie 會在會話期間保持

### 最佳實踐

1. **首次使用**: 明確說明 "playwright mcp"，避免 Claude 使用 Bash 來執行 Playwright
2. **複雜操作**: 將複雜的自動化任務分解成多個簡單步驟
3. **錯誤處理**: 如果遇到問題，嘗試重新啟動 Claude Code

## 故障排除

### 常見問題

1. **配置未生效**
   - 確保完全關閉 Claude Code 進程
   - 在 Windows 上可能需要從工作管理員中結束進程

2. **瀏覽器驅動問題**
   - 手動安裝瀏覽器驅動: `npx playwright install`
   - 檢查網路連接，驅動下載需要網路

3. **權限問題**
   - 確保有足夠權限安裝全局 npm 包
   - 考慮使用 `sudo` (Linux/macOS) 或管理員權限 (Windows)

### 清理配置

如需移除 Playwright MCP 配置：

```bash
claude mcp remove playwright
```

## 安全注意事項

- 使用第三方 MCP 服務器時請謹慎，Anthropic 未驗證所有第三方服務器的安全性
- 避免在自動化過程中處理敏感資訊
- 定期檢查和更新 MCP 包以獲得最新安全修復

## 相關資源

- [Claude Code MCP 官方文檔](https://docs.claude.com/en/docs/claude-code/mcp)
- [Microsoft Playwright MCP GitHub](https://github.com/microsoft/playwright-mcp)
- [ExecuteAutomation Playwright MCP](https://github.com/executeautomation/mcp-playwright)

---

*最後更新: 2025年9月27日*
*配置完成日期: 2025年9月27日*