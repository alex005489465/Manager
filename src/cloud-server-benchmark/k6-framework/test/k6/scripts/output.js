// k6 測試結果輸出處理
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';

// 生成測試摘要
export function handleSummary(data) {
  const testName = __ENV.TEST_NAME || 'unknown';
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');

  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    [`/results/${testName}-${timestamp}.json`]: JSON.stringify(data, null, 2),
  };
}