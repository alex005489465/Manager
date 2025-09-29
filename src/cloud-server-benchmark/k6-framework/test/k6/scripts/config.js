// k6 測試配置文件
// 提供所有測試腳本的共用配置選項

export const config = {
  // 框架配置
  frameworks: {
    node: {
      port: '8080',
      name: 'node'
    },
    phalcon: {
      port: '8081',
      name: 'phalcon'
    }
  },

  // 目標服務器配置
  target: {
    host: __ENV.TARGET_HOST,
    framework: __ENV.FRAMEWORK || 'node',
    get port() {
      return config.frameworks[this.framework]?.port || '8080';
    },
    get frameworkName() {
      return config.frameworks[this.framework]?.name || 'node';
    },
    protocol: 'http'
  },

  // 測試執行配置
  execution: {
    duration: '30s',
    vus: 10,
    rps: 100
  },

  // API 端點配置
  endpoints: {
    health: '/api/health',
    query: '/api/query'
  },

  // 測試閾值配置
  thresholds: {
    // HTTP 請求持續時間閾值
    http_req_duration: {
      p95: 500,  // 95% 的請求應在 500ms 內完成
      p99: 1000, // 99% 的請求應在 1000ms 內完成
      avg: 200   // 平均響應時間應在 200ms 內
    },

    // HTTP 請求失敗率閾值
    http_req_failed: {
      rate: 0.01 // 失敗率應低於 1%
    },

    // 每秒請求數閾值
    http_reqs: {
      min_rate: 50 // 最小 RPS 應達到 50
    }
  },

  // 負載階段配置
  stages: {
    // 100用戶負載測試
    load100: [
      { duration: '10s', target: 100 },  // 10秒快速爬升到100用戶
      { duration: '2m', target: 100 }    // 保持100用戶2分鐘
    ],

    // 200用戶負載測試
    load200: [
      { duration: '10s', target: 200 },  // 10秒快速爬升到200用戶
      { duration: '2m', target: 200 }    // 保持200用戶2分鐘
    ],

    // 400用戶負載測試
    load400: [
      { duration: '10s', target: 400 },  // 10秒快速爬升到400用戶
      { duration: '2m', target: 400 }    // 保持400用戶2分鐘
    ]
  },

  // HTTP 請求配置
  http: {
    timeout: '30s',
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'k6-benchmark-test/1.0.0'
    }
  }

};

