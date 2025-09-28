import http from 'k6/http';
import { check } from 'k6';
import { config } from './config.js';
import { createSummaryHandler } from './output.js';

// 測試配置
export const options = {
  stages: config.stages.load100,
  thresholds: {
    'http_req_duration': [`p(95)<${config.thresholds.http_req_duration.p95 * 2}`],
    'http_req_failed': [`rate<${config.thresholds.http_req_failed.rate * 2}`],
  }
};

export default function() {
  const url = `http://${config.target.host}:${config.target.port}${config.endpoints.query}`;

  // 生成1-100000的隨機ID
  const randomId = Math.floor(Math.random() * 100000) + 1;

  const response = http.post(url, JSON.stringify({ id: randomId }), {
    headers: config.http.headers,
  });

  check(response, {
    'status is 200 or 500': (r) => r.status === 200 || r.status === 500,
    'response has id field': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.id !== undefined;
      } catch (e) {
        return false;
      }
    },
    'response id matches request': (r) => {
      if (r.status !== 200) return true; // 跳過失敗響應
      try {
        const body = JSON.parse(r.body);
        return body.id === randomId;
      } catch (e) {
        return false;
      }
    },
  });
}

// 創建輸出處理函數 - 從配置中讀取VUS
export const handleSummary = createSummaryHandler('query', options.stages);