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

// 請求日誌中間件
app.use(async (req, res, next) => {
  const start = Date.now();

  res.on('finish', async () => {
    const duration = Date.now() - start;

    // 異步記錄請求日誌，不影響響應速度
    setImmediate(async () => {
      try {
        await prisma.requestLog.create({
          data: {
            endpoint: req.path,
            method: req.method,
            statusCode: res.statusCode,
            responseTime: duration,
            requestSize: parseInt(req.get('content-length')) || 0,
            responseSize: parseInt(res.get('content-length')) || 0,
            userAgent: req.get('user-agent'),
            ipAddress: req.ip || req.connection.remoteAddress,
          },
        });
      } catch (error) {
        // 靜默處理日誌錯誤，不影響應用運行
        console.warn('Failed to log request:', error.message);
      }
    });
  });

  next();
});

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
    // 檢查 Prisma 連接狀態
    try {
      await prisma.$queryRaw`SELECT 1`;
    } catch (connectError) {
      return res.status(503).json({
        error: 'Database not available',
        message: connectError.message,
        timestamp: new Date().toISOString(),
        request_id: requestId
      });
    }

    // 執行多個簡單查詢來測試性能
    const [currentTime, connectionInfo, benchmarkData] = await Promise.all([
      // 獲取當前時間
      prisma.$queryRaw`SELECT NOW() as current_time`,

      // 獲取連接資訊
      prisma.$queryRaw`SELECT CONNECTION_ID() as connection_id, DATABASE() as database_name`,

      // 獲取測試數據
      prisma.benchmarkTest.findFirst({
        select: {
          id: true,
          name: true,
          value: true,
          timestamp: true,
        },
        orderBy: {
          id: 'desc'
        }
      })
    ]);

    // 執行一個計數查詢
    const [recordCount, performanceCount] = await Promise.all([
      prisma.benchmarkTest.count(),
      prisma.performanceData.count()
    ]);

    const response = {
      status: 'OK',
      timestamp: new Date().toISOString(),
      service: 'bench-framework',
      orm: 'prisma',
      request_id: requestId,
      database: {
        current_time: currentTime[0]?.current_time,
        connection_id: connectionInfo[0]?.connection_id,
        database_name: connectionInfo[0]?.database_name,
        record_counts: {
          benchmark_test: recordCount,
          performance_data: performanceCount
        },
        latest_benchmark: benchmarkData ? {
          id: benchmarkData.id,
          name: benchmarkData.name,
          value: benchmarkData.value,
          timestamp: benchmarkData.timestamp
        } : null
      },
      query_time: new Date().toISOString()
    };

    res.json(response);
  } catch (error) {
    console.error('Database query error:', error);
    res.status(500).json({
      error: 'Database query failed',
      message: error.message,
      timestamp: new Date().toISOString(),
      request_id: requestId,
      orm: 'prisma'
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

// 新增統計端點
app.get('/api/stats', async (req, res) => {
  try {
    const [
      totalRequests,
      recentRequests,
      avgResponseTime,
      benchmarkCount,
      performanceCount
    ] = await Promise.all([
      prisma.requestLog.count(),
      prisma.requestLog.count({
        where: {
          timestamp: {
            gte: new Date(Date.now() - 5 * 60 * 1000) // 最近 5 分鐘
          }
        }
      }),
      prisma.requestLog.aggregate({
        _avg: {
          responseTime: true
        },
        where: {
          timestamp: {
            gte: new Date(Date.now() - 5 * 60 * 1000)
          }
        }
      }),
      prisma.benchmarkTest.count(),
      prisma.performanceData.count()
    ]);

    const stats = {
      status: 'OK',
      timestamp: new Date().toISOString(),
      service: 'bench-framework',
      orm: 'prisma',
      process_manager: 'pm2',
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      request_stats: {
        total_requests: totalRequests,
        recent_requests_5min: recentRequests,
        avg_response_time_5min: avgResponseTime._avg.responseTime || 0
      },
      database_stats: {
        benchmark_records: benchmarkCount,
        performance_records: performanceCount
      }
    };

    res.json(stats);
  } catch (error) {
    console.error('Stats query error:', error);
    res.status(500).json({
      error: 'Stats query failed',
      message: error.message,
      timestamp: new Date().toISOString()
    });
  }
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