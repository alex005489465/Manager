// k6 測試結果輸出處理

// 生成測試摘要
export function createSummaryHandler(testType, currentStages) {
  return function handleSummary(data) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    // 從stages中提取VUS數量
    const vusLevel = currentStages[0]?.target || 'unknown';
    const testName = `${testType}-${vusLevel}vus`;

    // 提取關鍵指標
    const totalDuration = Math.round(data.state.testRunDurationMs / 1000);
    
    const summary = {
      test_info: {
        name: testName,
        type: testType,
        vus_level: vusLevel,
        timestamp: new Date().toISOString(),
        duration_seconds: totalDuration,
        test_stages: currentStages.map(stage => ({
          duration: stage.duration,
          target_vus: stage.target
        })),
        total_planned_duration: currentStages.reduce((sum, stage) => {
          const duration = stage.duration;
          if (duration.endsWith('s')) {
            return sum + parseInt(duration);
          } else if (duration.endsWith('m')) {
            return sum + parseInt(duration) * 60;
          }
          return sum;
        }, 0)
      },
      performance: {
        total_requests: data.metrics.http_reqs?.values?.count || 0,
        failed_requests: data.metrics.http_req_failed?.values?.passes || 0,
        success_rate: ((1 - (data.metrics.http_req_failed?.values?.rate || 0)) * 100).toFixed(2) + '%',
        rps: Math.round(data.metrics.http_reqs?.values?.rate || 0),
        avg_response_time: Math.round(data.metrics.http_req_duration?.values?.avg || 0) + 'ms',
        p95_response_time: Math.round(data.metrics.http_req_duration?.values?.['p(95)'] || 0) + 'ms',
        // p99_response_time: Math.round(data.metrics.http_req_duration?.values?.['p(99)'] || 0) + 'ms',
        min_response_time: Math.round(data.metrics.http_req_duration?.values?.min || 0) + 'ms',
        max_response_time: Math.round(data.metrics.http_req_duration?.values?.max || 0) + 'ms'
      },
      thresholds: {
        passed: Object.keys(data.thresholds || {}).filter(key => 
          data.thresholds[key].some(t => t.ok)
        ),
        failed: Object.keys(data.thresholds || {}).filter(key => 
          data.thresholds[key].some(t => !t.ok)
        )
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