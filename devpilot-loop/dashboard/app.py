#!/usr/bin/env python3
"""
Web Status Dashboard for DevPilot Loop
=======================================
Flask-based real-time monitoring dashboard
"""

from flask import Flask, jsonify, render_template_string
import urllib.request
import json
from datetime import datetime, timezone
import threading
import time

app = Flask(__name__)

BASE_URLS = {
    "manager": "http://localhost:8008",
    "intake": "http://localhost:8001",
    "analyst": "http://localhost:8002",
    "fixer": "http://localhost:8003",
    "verifier": "http://localhost:8004",
    "release": "http://localhost:8005",
    "knowledge": "http://localhost:8006",
}


DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevPilot Loop Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #0f172a; color: #e2e8f0; }
        .header { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 20px 40px; border-bottom: 1px solid #334155; }
        .header h1 { font-size: 24px; color: #60a5fa; }
        .header .subtitle { font-size: 14px; color: #94a3b8; margin-top: 4px; }
        .metrics { display: flex; gap: 20px; padding: 20px 40px; }
        .metric-card { background: #1e293b; border-radius: 12px; padding: 20px; min-width: 150px; border: 1px solid #334155; }
        .metric-value { font-size: 32px; font-weight: 700; color: #60a5fa; }
        .metric-label { font-size: 12px; color: #94a3b8; margin-top: 4px; }
        .agents { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; padding: 20px 40px; }
        .agent-card { background: #1e293b; border-radius: 12px; padding: 16px; border: 1px solid #334155; transition: all 0.3s; }
        .agent-card.healthy { border-color: #22c55e; }
        .agent-card.unhealthy { border-color: #ef4444; }
        .agent-name { font-size: 16px; font-weight: 600; }
        .agent-type { font-size: 12px; color: #94a3b8; }
        .agent-status { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-top: 8px; }
        .status-healthy { background: #22c55e20; color: #22c55e; }
        .status-unhealthy { background: #ef444420; color: #ef4444; }
        .logs { padding: 20px 40px; }
        .logs h2 { font-size: 18px; margin-bottom: 16px; color: #94a3b8; }
        .log-entries { background: #1e293b; border-radius: 12px; padding: 16px; max-height: 300px; overflow-y: auto; }
        .log-entry { font-family: monospace; font-size: 12px; padding: 4px 0; border-bottom: 1px solid #334155; }
        .log-entry:last-child { border-bottom: none; }
        .refresh { padding: 20px 40px; }
        button { background: #3b82f6; color: white; border: none; padding: 10px 24px; border-radius: 8px; cursor: pointer; font-size: 14px; }
        button:hover { background: #2563eb; }
    </style>
</head>
<body>
    <div class="header">
        <h1>DevPilot Loop Dashboard</h1>
        <div class="subtitle">Multi-Agent Autonomous R&D System | Version 2.0.0</div>
    </div>

    <div class="metrics" id="metrics"></div>
    <div class="agents" id="agents"></div>
    <div class="logs">
        <h2>Recent Activity</h2>
        <div class="log-entries" id="logs"></div>
    </div>
    <div class="refresh">
        <button onclick="refresh()">Refresh Now</button>
        <span id="last-refresh" style="margin-left: 16px; color: #64748b;"></span>
    </div>

    <script>
        const BASE_URLS = {{ urls | tojson }};

        async function fetchHealth(url) {
            try {
                const resp = await fetch(url + '/health');
                return await resp.json();
            } catch {
                return { status: 'unhealthy', error: 'Connection refused' };
            }
        }

        async function refresh() {
            const agents = document.getElementById('agents');
            const metrics = document.getElementById('metrics');
            const logs = document.getElementById('logs');

            // Fetch all agents
            const results = await Promise.all(
                Object.entries(BASE_URLS).map(async ([name, url]) => ({
                    name, url, data: await fetchHealth(url)
                }))
            );

            // Render metrics
            const total = results.length;
            const healthy = results.filter(r => r.data.status === 'healthy').length;
            metrics.innerHTML = `
                <div class="metric-card"><div class="metric-value">${total}</div><div class="metric-label">Total Services</div></div>
                <div class="metric-card"><div class="metric-value" style="color: #22c55e">${healthy}</div><div class="metric-label">Healthy</div></div>
                <div class="metric-card"><div class="metric-value" style="color: #ef4444">${total - healthy}</div><div class="metric-label">Down</div></div>
                <div class="metric-card"><div class="metric-value">${new Date().toLocaleTimeString()}</div><div class="metric-label">Last Refresh</div></div>
            `;

            // Render agents
            agents.innerHTML = results.map(r => `
                <div class="agent-card ${r.data.status === 'healthy' ? 'healthy' : 'unhealthy'}">
                    <div class="agent-name">${r.name}</div>
                    <div class="agent-type">${r.data.type || 'unknown'} • ${r.url}</div>
                    <div class="agent-status ${r.data.status === 'healthy' ? 'status-healthy' : 'status-unhealthy'}">
                        ${r.data.status === 'healthy' ? 'HEALTHY' : 'DOWN'}
                    </div>
                    ${r.data.version ? `<div style="font-size:11px;color:#64748b;margin-top:4px">v${r.data.version}</div>` : ''}
                </div>
            `).join('');

            // Render recent logs
            logs.innerHTML = results
                .filter(r => r.data.status === 'healthy')
                .slice(0, 3)
                .map(r => `<div class="log-entry">✓ ${r.name} (${r.url}) - ${r.data.uptime_seconds?.toFixed(0) || 0}s uptime</div>`)
                .join('') || '<div class="log-entry">No healthy services</div>';

            document.getElementById('last-refresh').textContent =
                'Last refresh: ' + new Date().toLocaleTimeString();
        }

        // Auto-refresh every 10 seconds
        setInterval(refresh, 10000);
        refresh();
    </script>
</body>
</html>
"""


@app.route('/')
def dashboard():
    """Render dashboard HTML"""
    return render_template_string(DASHBOARD_HTML, urls=BASE_URLS)


@app.route('/api/health')
def api_health():
    """API endpoint for health checks"""
    results = {}
    for name, url in BASE_URLS.items():
        try:
            with urllib.request.urlopen(f"{url}/health", timeout=3) as resp:
                results[name] = json.loads(resp.read())
        except Exception as e:
            results[name] = {"status": "error", "error": str(e)}
    return jsonify({"timestamp": datetime.now(timezone.utc).isoformat(), "services": results})


@app.route('/api/tasks')
def api_tasks():
    """API endpoint for tasks"""
    try:
        with urllib.request.urlopen("http://localhost:8008/tasks", timeout=3) as resp:
            return jsonify(json.loads(resp.read()))
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/api/logs')
def api_logs():
    """API endpoint for logs"""
    try:
        with urllib.request.urlopen("http://localhost:8008/logs?limit=20", timeout=3) as resp:
            return jsonify(json.loads(resp.read()))
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/api/metrics')
def api_metrics():
    """API endpoint for metrics"""
    try:
        with urllib.request.urlopen("http://localhost:8008/metrics", timeout=3) as resp:
            return jsonify(json.loads(resp.read()))
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    print("Starting DevPilot Loop Dashboard on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
