/**
 * k6 smoke — E10 endpoints cacheados / públicos.
 * Uso: k6 run loadtests/k6_smoke.js
 * Env: BASE_URL=https://metgo-api.onrender.com
 */
import http from 'k6/http'
import { check, sleep } from 'k6'

const BASE = __ENV.BASE_URL || 'http://127.0.0.1:8080'

export const options = {
  vus: 10,
  duration: '20s',
  thresholds: {
    http_req_duration: ['p(95)<800'],
    http_req_failed: ['rate<0.05'],
  },
}

export default function () {
  const health = http.get(`${BASE}/api/health`)
  check(health, { 'health 200': (r) => r.status === 200 })

  const sitios = http.get(`${BASE}/api/health/sitios`)
  check(sitios, { 'health sitios 200': (r) => r.status === 200 })

  const metrics = http.get(`${BASE}/api/metrics`)
  check(metrics, { 'metrics 200': (r) => r.status === 200 })

  sleep(0.5)
}
