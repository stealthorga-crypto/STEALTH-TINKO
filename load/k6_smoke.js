import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = { vus: 1, duration: '30s' };

const API = __ENV.API_BASE_URL || 'http://127.0.0.1:8000';

export default function () {
  let res = http.get(`${API}/healthz`);
  check(res, { 'health 200': (r) => r.status === 200 });

  res = http.get(`${API}/v1/analytics/summary`);
  check(res, { 'summary 200': (r) => r.status === 200 });

  // Optional: ingest simulation (if endpoint exists)
  // http.post(`${API}/v1/events/ingest`, JSON.stringify({ type: 'test', payload: {} }), { headers: { 'Content-Type': 'application/json' } });

  sleep(1);
}
