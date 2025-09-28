// k6 測試結果輸出處理

// 生成測試摘要
export function createSummaryHandler(testType, currentStages) {
  return function handleSummary(data) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    // 從stages中提取VUS數量
    const vusLevel = currentStages[0]?.target || 'unknown';
    const testName = `${testType}-${vusLevel}vus`;

    // 提取關鍵指標
    const summary = {
      test_info: {
        name: testName,
        type: testType,
        vus_level: vusLevel,
        timestamp: new Date().toISOString(),
        duration_seconds: Math.round(data.state.testRunDurationMs / 1000)
      },
      performance: {
        total_requests: data.metrics.http_reqs?.count || 0,
        failed_requests: data.metrics.http_req_failed?.count || 0,
        success_rate: ((1 - (data.metrics.http_req_failed?.rate || 0)) * 100).toFixed(2) + '%',
        rps: Math.round(data.metrics.http_reqs?.rate || 0),
        avg_response_time: Math.round(data.metrics.http_req_duration?.avg || 0) + 'ms',
        p95_response_time: Math.round(data.metrics.http_req_duration?.['p(95)'] || 0) + 'ms',
        p99_response_time: Math.round(data.metrics.http_req_duration?.['p(99)'] || 0) + 'ms'
      }
    };

    // 控制台顯示簡化結果
    console.log(`📊 ${testName} 測試結果:`);
    console.log(`   ├── 總請求數: ${summary.performance.total_requests}`);
    console.log(`   ├── 成功率: ${summary.performance.success_rate}`);
    console.log(`   ├── RPS: ${summary.performance.rps}`);
    console.log(`   ├── 平均回應: ${summary.performance.avg_response_time}`);
    console.log(`   └── P95回應: ${summary.performance.p95_response_time}`);

    return {
      [`/results/${testName}-${timestamp}.json`]: JSON.stringify(summary, null, 2),
    };
  };
}