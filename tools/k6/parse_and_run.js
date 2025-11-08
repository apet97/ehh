/**
 * k6 Load Test Script for Clankerbot
 *
 * Tests the /actions/parse and /actions/run endpoints under load.
 *
 * Usage:
 *   k6 run parse_and_run.js
 *
 * Environment Variables:
 *   BASE_URL - Base URL for the API (default: http://localhost:8000)
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const parseLatency = new Trend('parse_latency');
const runLatency = new Trend('run_latency');

// Configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  stages: [
    { duration: '30s', target: 10 },  // Ramp up to 10 RPS over 30s
    { duration: '2m', target: 10 },   // Maintain 10 RPS for 2 minutes
    { duration: '30s', target: 0 },   // Ramp down to 0 over 30s
  ],
  thresholds: {
    'errors': ['rate<0.01'],           // Error rate < 1%
    'http_req_duration': ['p(95)<300'], // P95 latency < 300ms
    'http_req_failed': ['rate<0.01'],  // Failed requests < 1%
  },
};

// Test payloads
const parsePayload = {
  text: "get user john.doe from clockify"
};

const runPayload = {
  action: "get_user",
  arguments: {
    identifier: "john.doe",
    source: "clockify"
  },
  mock: true  // Use mock mode to avoid hitting real APIs
};

export default function () {
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'X-Request-ID': `k6-${__VU}-${__ITER}`,
    },
    timeout: '5s',
  };

  // Test scenario 1: Parse endpoint (rule-based parsing)
  const parseResponse = http.post(
    `${BASE_URL}/actions/parse`,
    JSON.stringify(parsePayload),
    params
  );

  const parseSuccess = check(parseResponse, {
    'parse: status is 200': (r) => r.status === 200,
    'parse: response is valid JSON': (r) => {
      try {
        JSON.parse(r.body);
        return true;
      } catch {
        return false;
      }
    },
    'parse: has success field': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.success !== undefined;
      } catch {
        return false;
      }
    },
  });

  parseLatency.add(parseResponse.timings.duration);
  errorRate.add(!parseSuccess);

  sleep(0.5);

  // Test scenario 2: Run endpoint (with mock)
  const runResponse = http.post(
    `${BASE_URL}/actions/run`,
    JSON.stringify(runPayload),
    params
  );

  const runSuccess = check(runResponse, {
    'run: status is 200': (r) => r.status === 200,
    'run: response is valid JSON': (r) => {
      try {
        JSON.parse(r.body);
        return true;
      } catch {
        return false;
      }
    },
    'run: has success field': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.success !== undefined;
      } catch {
        return false;
      }
    },
  });

  runLatency.add(runResponse.timings.duration);
  errorRate.add(!runSuccess);

  sleep(0.5);
}

export function handleSummary(data) {
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    'load-test-results.json': JSON.stringify(data, null, 2),
  };
}

function textSummary(data, options) {
  const indent = options.indent || '';
  const enableColors = options.enableColors || false;

  let summary = '\n';
  summary += `${indent}Test Results:\n`;
  summary += `${indent}============\n\n`;

  // Requests
  const requests = data.metrics.http_reqs;
  if (requests) {
    summary += `${indent}Total Requests: ${requests.values.count}\n`;
    summary += `${indent}Request Rate:   ${requests.values.rate.toFixed(2)} req/s\n\n`;
  }

  // Duration
  const duration = data.metrics.http_req_duration;
  if (duration) {
    summary += `${indent}Response Time:\n`;
    summary += `${indent}  Min:  ${duration.values.min.toFixed(2)} ms\n`;
    summary += `${indent}  Avg:  ${duration.values.avg.toFixed(2)} ms\n`;
    summary += `${indent}  P50:  ${duration.values['p(50)'].toFixed(2)} ms\n`;
    summary += `${indent}  P95:  ${duration.values['p(95)'].toFixed(2)} ms\n`;
    summary += `${indent}  P99:  ${duration.values['p(99)'].toFixed(2)} ms\n`;
    summary += `${indent}  Max:  ${duration.values.max.toFixed(2)} ms\n\n`;
  }

  // Errors
  const errors = data.metrics.errors;
  if (errors) {
    const errorPct = (errors.values.rate * 100).toFixed(2);
    summary += `${indent}Error Rate: ${errorPct}%\n\n`;
  }

  // Custom metrics
  if (data.metrics.parse_latency) {
    summary += `${indent}Parse Endpoint Latency:\n`;
    summary += `${indent}  Avg: ${data.metrics.parse_latency.values.avg.toFixed(2)} ms\n`;
    summary += `${indent}  P95: ${data.metrics.parse_latency.values['p(95)'].toFixed(2)} ms\n\n`;
  }

  if (data.metrics.run_latency) {
    summary += `${indent}Run Endpoint Latency:\n`;
    summary += `${indent}  Avg: ${data.metrics.run_latency.values.avg.toFixed(2)} ms\n`;
    summary += `${indent}  P95: ${data.metrics.run_latency.values['p(95)'].toFixed(2)} ms\n\n`;
  }

  return summary;
}
