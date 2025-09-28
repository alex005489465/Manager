import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { config, buildUrl, generateTestData, checkResponse, generateSummary } from './config.js';

// 自定義指標
export const queryErrorRate = new Rate('query_errors');
export const queryTrend = new Trend('query_response_time');
export const queryRequests = new Counter('query_requests');
export const dbConnectionErrors = new Counter('db_connection_errors');

// 測試配置
export const options = {
  // 使用配置中的查詢端點測試階段
  stages: config.stages.query,

  // 設定閾值（資料庫查詢通常較慢）
  thresholds: {
    'http_req_duration': [`p(95)<${config.thresholds.http_req_duration.p95 * 2}`], // 資料庫查詢允許較長時間
    'http_req_duration{expected_response:true}': [`p(99)<${config.thresholds.http_req_duration.p99 * 2}`],
    'http_req_failed': [`rate<${config.thresholds.http_req_failed.rate * 2}`], // 允許較高錯誤率
    'query_errors': ['rate<0.05'], // 查詢錯誤率應低於 5%
    'query_response_time': ['p(95)<1000', 'avg<500'], // 查詢響應時間閾值
  },

  // 輸出配置
  noConnectionReuse: false,
  userAgent: config.http.headers['User-Agent'],
};

// 測試設定函數
export function setup() {
  console.log('🚀 開始簡單查詢性能測試');
  console.log(`📍 目標端點: ${buildUrl(config.endpoints.query)}`);
  console.log(`⏱️  測試階段: ${JSON.stringify(config.stages.query)}`);

  // 驗證端點可用性
  const testUrl = buildUrl(config.endpoints.query);
  const response = http.post(testUrl, JSON.stringify(generateTestData()), {
    headers: config.http.headers,
    timeout: config.http.timeout,
  });

  if (response.status === 503) {
    console.warn('⚠️  資料庫服務不可用，測試將記錄此狀況');
  } else if (response.status !== 200) {
    console.error(`❌ 端點不可用: ${response.status} ${response.body}`);
    throw new Error(`Query endpoint not available: ${response.status}`);
  } else {
    console.log('✅ 端點可用性驗證成功');
  }

  return { testUrl: testUrl };
}

// 主要測試函數
export default function(data) {
  const testData = generateTestData();
  const url = data.testUrl;

  // 發送 POST 請求到查詢端點
  const response = http.post(url, JSON.stringify(testData), {
    headers: config.http.headers,
    timeout: config.http.timeout,
    tags: {
      test_type: 'query',
      endpoint: config.endpoints.query
    },
  });

  // 記錄自定義指標
  queryRequests.add(1);
  queryTrend.add(response.timings.duration);
  queryErrorRate.add(response.status !== 200 && response.status !== 503);

  // 特殊處理資料庫連接錯誤
  if (response.status === 503) {
    dbConnectionErrors.add(1);
  }

  // 檢查響應
  const checks = checkResponse(response, 'query');
  const checkResult = check(response, {
    'status is 200 or 503 (db unavailable)': (r) => r.status === 200 || r.status === 503,
    'response time acceptable': (r) => r.timings.duration < 2000, // 允許較長的響應時間
    'response has body': (r) => r.body && r.body.length > 0,
    'response is JSON': (r) => {
      try {
        JSON.parse(r.body);
        return true;
      } catch (e) {
        return false;
      }
    },
    'query specific: success response structure': (r) => {
      if (r.status !== 200) return true; // 跳過非成功響應的檢查
      try {
        const body = JSON.parse(r.body);
        return body.status === 'OK' && body.database && body.timestamp;
      } catch (e) {
        return false;
      }
    },
    'query specific: database connection info': (r) => {
      if (r.status !== 200) return true; // 跳過非成功響應的檢查
      try {
        const body = JSON.parse(r.body);
        return body.database.current_time && body.database.connection_id;
      } catch (e) {
        return false;
      }
    },
    'query specific: error response structure': (r) => {
      if (r.status === 200) return true; // 跳過成功響應的檢查
      try {
        const body = JSON.parse(r.body);
        return body.error && body.timestamp;
      } catch (e) {
        return false;
      }
    }
  });

  // 記錄詳細響應信息
  if (response.status === 200) {
    // 成功響應的詳細記錄（僅在開發時啟用）
    if (__ENV.DEBUG === 'true') {
      try {
        const body = JSON.parse(response.body);
        console.log(`✅ Query success: DB time=${body.database.current_time}, Duration=${response.timings.duration}ms`);
      } catch (e) {
        console.warn('⚠️  Could not parse successful response body');
      }
    }
  } else if (response.status === 503) {
    // 資料庫不可用（預期錯誤）
    console.log(`⚠️  Database unavailable (503), Duration=${response.timings.duration}ms`);
  } else {
    // 其他錯誤
    console.error(`❌ Query test failed:`, {
      status: response.status,
      body: response.body.substring(0, 200), // 限制錯誤訊息長度
      duration: response.timings.duration,
      checks: checkResult
    });
  }

  // 模擬真實用戶行為的思考時間（查詢後通常會處理結果）
  sleep(0.2);
}

// 測試清理函數
export function teardown(data) {
  console.log('🏁 簡單查詢性能測試完成');
  console.log(`📊 測試數據已保存到: /results/query-results.json`);
  console.log(`📈 HTML 報告已保存到: /results/query-report.html`);
}

// 結果摘要處理函數
export function handleSummary(data) {
  const summary = generateSummary(data);

  // 計算資料庫相關指標
  const dbErrors = data.metrics.db_connection_errors ? data.metrics.db_connection_errors.count : 0;
  const queryErrors = data.metrics.query_errors ? data.metrics.query_errors.count : 0;
  const dbAvailability = ((summary.total_requests - dbErrors) / summary.total_requests * 100).toFixed(2);

  console.log('📋 簡單查詢測試摘要:');
  console.log(`   ├── 總請求數: ${summary.total_requests}`);
  console.log(`   ├── 失敗請求數: ${summary.failed_requests}`);
  console.log(`   ├── 資料庫連接錯誤: ${dbErrors}`);
  console.log(`   ├── 查詢錯誤: ${queryErrors}`);
  console.log(`   ├── 資料庫可用性: ${dbAvailability}%`);
  console.log(`   ├── 平均響應時間: ${summary.avg_response_time.toFixed(2)}ms`);
  console.log(`   ├── P95 響應時間: ${summary.p95_response_time.toFixed(2)}ms`);
  console.log(`   ├── P99 響應時間: ${summary.p99_response_time.toFixed(2)}ms`);
  console.log(`   └── 每秒請求數: ${summary.rps.toFixed(2)} RPS`);

  // 返回多種格式的報告
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    '/results/query-summary.json': JSON.stringify({
      ...summary,
      test_type: 'query',
      endpoint: config.endpoints.query,
      database_metrics: {
        connection_errors: dbErrors,
        query_errors: queryErrors,
        availability_percentage: parseFloat(dbAvailability),
        total_db_operations: summary.total_requests - dbErrors
      },
      detailed_metrics: {
        http_reqs: data.metrics.http_reqs,
        http_req_duration: data.metrics.http_req_duration,
        http_req_failed: data.metrics.http_req_failed,
        query_requests: data.metrics.query_requests,
        query_response_time: data.metrics.query_response_time,
        query_errors: data.metrics.query_errors,
        db_connection_errors: data.metrics.db_connection_errors
      }
    }, null, 2),
  };
}