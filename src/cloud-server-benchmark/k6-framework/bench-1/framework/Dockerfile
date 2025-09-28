FROM node:18-alpine

# 安裝必要的系統依賴
RUN apk add --no-cache libc6-compat

WORKDIR /app

# 複製 package 檔案
COPY package*.json ./
COPY prisma ./prisma/

# 安裝 dependencies (包含 dev dependencies 用於 Prisma)
RUN npm ci

# 生成 Prisma Client
RUN npm run db:generate

# 複製應用程式碼
COPY src/ ./src/
COPY ecosystem.config.js ./
COPY logs/ ./logs/

# 清理 dev dependencies (保留 Prisma Client)
RUN npm prune --production

# 設定環境變數
ENV NODE_ENV=production
ENV PORT=3000

# 創建非 root 用戶
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# 設定權限
RUN chown -R nextjs:nodejs /app
USER nextjs

# 暴露端口
EXPOSE 3000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (res) => process.exit(res.statusCode === 200 ? 0 : 1))"

# 啟動應用 (使用 PM2 runtime)
CMD ["npm", "start"]