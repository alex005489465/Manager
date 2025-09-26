# Cloudflare Pages 部署流程

## 準備階段

1. **申請 Cloudflare 帳號**
2. **安裝 CLI 工具**
   ```bash
   npm install -g wrangler
   ```

## 授權登入

```bash
wrangler login
```
- 會開啟授權頁面
- 完成授權確認

## 創建專案

```bash
npx wrangler pages project create <專案名稱>
```
- 到 Cloudflare 儀表板確認
- Pages 區域會出現新專案

## 構建部署

1. **在前端容器內構建**
   ```bash
   # 產生 ./dist 資料夾
   npm run build
   ```

2. **部署到 Cloudflare**
   ```bash
   # 在 ./dist 同目錄執行
   npx wrangler pages deploy ./dist
   ```
   - CLI 選擇剛創建的專案名稱
   - 分支選擇 `main`

## 完成

- Cloudflare 自動分配預設域名
- 點開連結查看部署結果
- 部署完成

---

**狀態**: 基本流程