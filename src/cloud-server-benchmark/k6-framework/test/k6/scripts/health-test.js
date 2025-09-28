import http from 'k6/http';
import { check } from 'k6';
import { config } from './config.js';
import { createSummaryHandler } from './output.js';

// 測試配置
export const options = {
  stages: config.stages.load100,
  thresholds: {
    'http_req_duration': [`p(95)<${config.thresholds.http_req_duration.p95}`],
    'http_req_failed': [`rate<${config.thresholds.http_req_failed.rate}`],
  }
};

export default function() {
  const url = `http://${config.target.host}:${config.target.port}${config.endpoints.health}`;

  const response = http.post(url, JSON.stringify({}), {
    headers: config.http.headers,
  });

  check(response, {
    'status is 200': (r) => r.status === 200,
    'has status OK': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.status === 'OK';
      } catch (e) {
        return false;
      }
    },
  });
}

// 創建輸出處理函數 - 從配置中讀取VUS
export const handleSummary = createSummaryHandler('health', options.stages);