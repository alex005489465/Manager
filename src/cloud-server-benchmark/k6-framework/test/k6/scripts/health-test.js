import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { config, buildUrl, generateTestData, checkResponse, generateSummary } from './config.js';

// 自定義指標
export const errorRate = new Rate('health_errors');
export const healthTrend = new Trend('health_response_time');
export const healthRequests = new Counter('health_requests');

// 測試配置
export const options = {
  // 使用配置中的靜態端點測試階段
  stages: config.stages.health,

  // 設定閾值
  thresholds: {
    'http_req_duration': [`p(95)<${config.thresholds.http_req_duration.p95}`],
    'http_req_duration{expected_response:true}': [`p(99)<${config.thresholds.http_req_duration.p99}`],
    'http_req_failed': [`rate<${config.thresholds.http_req_failed.rate}`],
    'health_errors': ['rate<0.01'],
    'health_response_time': ['p(95)<500', 'avg<200'],
  },

  // 輸出配置
  noConnectionReuse: false,
  userAgent: config.http.headers['User-Agent'],
};

// 測試設定函數
export function setup() {
  console.log('🚀 開始靜態端點性能測試');
  console.log(`📍 目標端點: ${buildUrl(config.endpoints.health)}`);
  console.log(`⏱️  測試階段: ${JSON.stringify(config.stages.health)}`);

  // 驗證端點可用性
  const testUrl = buildUrl(config.endpoints.health);
  const response = http.post(testUrl, JSON.stringify(generateTestData()), {
    headers: config.http.headers,
    timeout: config.http.timeout,
  });

  if (response.status !== 200) {
    console.error(`❌ 端點不可用: ${response.status} ${response.body}`);
    throw new Error(`Health endpoint not available: ${response.status}`);
  }

  console.log('✅ 端點可用性驗證成功');
  return { testUrl: testUrl };
}

// 主要測試函數
export default function(data) {
  const testData = generateTestData();
  const url = data.testUrl;

  // 發送 POST 請求到健康檢查端點
  const response = http.post(url, JSON.stringify(testData), {
    headers: config.http.headers,
    timeout: config.http.timeout,
    tags: {
      test_type: 'health',
      endpoint: config.endpoints.health
    },
  });

  // 記錄自定義指標
  healthRequests.add(1);
  healthTrend.add(response.timings.duration);
  errorRate.add(response.status !== 200);

  // 檢查響應
  const checks = checkResponse(response, 'health');
  const checkResult = check(response, {
    ...checks,
    'health specific: has status field': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.status === 'OK';
      } catch (e) {
        return false;
      }
    },
    'health specific: has timestamp': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.timestamp && new Date(body.timestamp).getTime() > 0;
      } catch (e) {
        return false;
      }
    },
    'health specific: has service info': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.service === 'bench-framework';
      } catch (e) {
        return false;
      }
    }
  });

  // 記錄詳細響應信息（僅在失敗時）
  if (!checkResult || response.status !== 200) {
    console.error(`❌ Health test failed:`, {
      status: response.status,
      body: response.body,
      duration: response.timings.duration,
      checks: checkResult
    });
  }

  // 模擬真實用戶行為的思考時間
  sleep(0.1);
}

// 測試清理函數
export function teardown(data) {
  console.log('🏁 靜態端點性能測試完成');
  console.log(`📊 測試數據已保存到: /results/health-results.json`);
  console.log(`📈 HTML 報告已保存到: /results/health-report.html`);
}

// 結果摘要處理函數
export function handleSummary(data) {
  const summary = generateSummary(data);

  console.log('📋 健康檢查測試摘要:');
  console.log(`   ├── 總請求數: ${summary.total_requests}`);
  console.log(`   ├── 失敗請求數: ${summary.failed_requests}`);
  console.log(`   ├── 平均響應時間: ${summary.avg_response_time.toFixed(2)}ms`);
  console.log(`   ├── P95 響應時間: ${summary.p95_response_time.toFixed(2)}ms`);
  console.log(`   ├── P99 響應時間: ${summary.p99_response_time.toFixed(2)}ms`);
  console.log(`   └── 每秒請求數: ${summary.rps.toFixed(2)} RPS`);

  // 返回多種格式的報告
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    '/results/health-summary.json': JSON.stringify({
      ...summary,
      test_type: 'health',
      endpoint: config.endpoints.health,
      detailed_metrics: {
        http_reqs: data.metrics.http_reqs,
        http_req_duration: data.metrics.http_req_duration,
        http_req_failed: data.metrics.http_req_failed,
        health_requests: data.metrics.health_requests,
        health_response_time: data.metrics.health_response_time,
        health_errors: data.metrics.health_errors
      }
    }, null, 2),
  };
}