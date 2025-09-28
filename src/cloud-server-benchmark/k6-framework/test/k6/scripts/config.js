// k6 測試配置文件
// 提供所有測試腳本的共用配置選項

export const config = {
  // 目標服務器配置
  target: {
    host: __ENV.TARGET_HOST || 'localhost',
    port: __ENV.TARGET_PORT || '80',
    protocol: 'http'
  },

  // 測試執行配置
  execution: {
    duration: __ENV.TEST_DURATION || '30s',
    vus: parseInt(__ENV.VUS) || 10,
    rps: parseInt(__ENV.RPS) || 100
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
    // 靜態端點測試階段
    health: [
      { duration: '10s', target: 5 },   // 預熱：10 秒內逐步增加到 5 個用戶
      { duration: '20s', target: 10 },  // 穩定負載：20 秒維持 10 個用戶
      { duration: '10s', target: 0 }    // 降載：10 秒內降到 0 個用戶
    ],

    // 查詢端點測試階段
    query: [
      { duration: '15s', target: 3 },   // 預熱：15 秒內逐步增加到 3 個用戶
      { duration: '30s', target: 5 },   // 穩定負載：30 秒維持 5 個用戶
      { duration: '15s', target: 0 }    // 降載：15 秒內降到 0 個用戶
    ],

    // 自定義負載測試階段
    custom: [
      { duration: '5s', target: parseInt(__ENV.VUS) || 10 },
      { duration: __ENV.TEST_DURATION || '30s', target: parseInt(__ENV.VUS) || 10 },
      { duration: '5s', target: 0 }
    ]
  },

  // HTTP 請求配置
  http: {
    timeout: '30s',
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'k6-benchmark-test/1.0.0'
    }
  },

  // 輸出配置
  output: {
    json: {
      file: '/results/test-results.json'
    },
    html: {
      file: '/results/test-report.html'
    }
  }
};

// 建構完整的 URL
export function buildUrl(endpoint) {
  return `${config.target.protocol}://${config.target.host}:${config.target.port}${endpoint}`;
}

// 生成測試數據
export function generateTestData() {
  return {
    timestamp: new Date().toISOString(),
    test_id: Math.random().toString(36).substr(2, 9),
    user_id: Math.floor(Math.random() * 1000) + 1
  };
}

// 檢查響應
export function checkResponse(response, endpoint) {
  return {
    'status is 200': response.status === 200,
    [`${endpoint} response time < ${config.thresholds.http_req_duration.p95}ms`]: response.timings.duration < config.thresholds.http_req_duration.p95,
    'response has body': response.body && response.body.length > 0,
    'response is JSON': response.headers['Content-Type'] && response.headers['Content-Type'].includes('application/json')
  };
}

// 生成測試摘要
export function generateSummary(data) {
  return {
    test_start: data.state.testRunDurationMs ? new Date(Date.now() - data.state.testRunDurationMs).toISOString() : null,
    test_end: new Date().toISOString(),
    total_requests: data.metrics.http_reqs ? data.metrics.http_reqs.count : 0,
    failed_requests: data.metrics.http_req_failed ? data.metrics.http_req_failed.count : 0,
    avg_response_time: data.metrics.http_req_duration ? data.metrics.http_req_duration.med : 0,
    p95_response_time: data.metrics.http_req_duration ? data.metrics.http_req_duration['p(95)'] : 0,
    p99_response_time: data.metrics.http_req_duration ? data.metrics.http_req_duration['p(99)'] : 0,
    rps: data.metrics.http_reqs ? data.metrics.http_reqs.rate : 0
  };
}