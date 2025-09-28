const express = require('express');
const { PrismaClient } = require('@prisma/client');

const app = express();
const PORT = process.env.PORT || 3000;
const prisma = new PrismaClient({
  log: ['error', 'warn'],
  errorFormat: 'pretty',
});

// 中間件
app.use(express.json());

// 移除請求日誌中間件，專注於性能測試

// 初始化 Prisma 連接
async function initDatabase() {
  try {
    await prisma.$connect();
    console.log('✅ Prisma database connection established');

    // 測試資料庫連接
    await prisma.$queryRaw`SELECT 1`;
    console.log('✅ Database connection verified');
  } catch (error) {
    console.error('❌ Database connection failed:', error.message);
    console.log('⚠️  Continuing without database connection for health endpoint');
  }
}

// API 端點

// 靜態端點 - 純框架性能測試
app.post('/api/health', (req, res) => {
  const timestamp = new Date().toISOString();
  const response = {
    status: 'OK',
    timestamp: timestamp,
    service: 'bench-framework',
    version: '1.0.0',
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    request_id: Math.random().toString(36).substr(2, 9)
  };

  res.json(response);
});

// 簡單查詢端點 - 框架 + 資料庫性能測試
app.post('/api/query', async (req, res) => {
  const requestId = Math.random().toString(36).substr(2, 9);

  try {
    // 執行簡單查詢
    const [currentTime, benchmarkData, recordCount] = await Promise.all([
      // 獲取當前時間
      prisma.$queryRaw`SELECT NOW() as current_time, CONNECTION_ID() as connection_id`,

      // 獲取測試數據
      prisma.benchmarkTest.findFirst({
        orderBy: { id: 'desc' }
      }),

      // 計數查詢
      prisma.benchmarkTest.count()
    ]);

    const response = {
      status: 'OK',
      timestamp: new Date().toISOString(),
      service: 'bench-framework',
      orm: 'prisma',
      request_id: requestId,
      database: {
        current_time: currentTime[0]?.current_time,
        connection_id: currentTime[0]?.connection_id,
        record_count: recordCount,
        latest_record: benchmarkData
      }
    };

    res.json(response);
  } catch (error) {
    console.error('Database query error:', error);
    res.status(500).json({
      error: 'Database query failed',
      message: error.message,
      timestamp: new Date().toISOString(),
      request_id: requestId
    });
  }
});

// 錯誤處理中間件
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({
    error: 'Internal server error',
    timestamp: new Date().toISOString()
  });
});

// 404 處理
app.use((req, res) => {
  res.status(404).json({
    error: 'Not found',
    path: req.path,
    timestamp: new Date().toISOString()
  });
});


// 啟動服務器
async function startServer() {
  await initDatabase();

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Framework server listening on port ${PORT}`);
    console.log(`📦 Environment: ${process.env.NODE_ENV || 'development'}`);
    console.log(`🗄️  ORM: Prisma`);
    console.log(`⚡ Process Manager: PM2`);
    console.log(`🔗 Database URL: ${process.env.DATABASE_URL ? '[Configured]' : '[Not Set]'}`);
  });
}

// 優雅關閉
async function gracefulShutdown(signal) {
  console.log(`${signal} received, shutting down gracefully`);

  try {
    // 關閉 Prisma 連接
    await prisma.$disconnect();
    console.log('✅ Prisma disconnected');
  } catch (error) {
    console.error('❌ Error disconnecting Prisma:', error);
  }

  process.exit(0);
}

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// PM2 優雅關閉處理
process.on('message', (msg) => {
  if (msg === 'shutdown') {
    gracefulShutdown('PM2 SHUTDOWN');
  }
});

startServer().catch((error) => {
  console.error('❌ Failed to start server:', error);
  process.exit(1);
});