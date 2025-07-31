import socket
import requests
import time

BACKEND_IP = '34.202.215.209'
PORTS = [4000, 8000, 8501]
ENDPOINTS = [
    '/api/imperium/agents',
    '/api/imperium/status',
    '/api/imperium/dashboard',
    '/api/imperium/trusted-sources',
    '/api/imperium/internet-learning/topics',
    '/api/imperium/persistence/learning-analytics',
    '/api/imperium/growth',
    '/api/imperium/proposals',
    '/api/imperium/monitoring',
    '/api/imperium/issues',
    '/api/imperium/health',
    '/api/health',
    '/api/status',
    '/api/config',
    '/api/info',
    '/api/version',
    '/api/learning/data',
    '/api/learning/metrics',
    '/api/learning/status',
    '/api/learning/insights',
    '/api/proposals',
    '/api/proposals/ai-status',
    '/api/proposals/status',
    '/api/oath-papers',
    '/api/oath-papers/ai-insights',
    '/api/oath-papers/learn',
    '/api/oath-papers/categories',
    '/ws',
    '/ws/imperium/learning-analytics',
    '/api/notifications/ws',
    '/socket.io/',
    '/api/logs',
    '/logs',
]

WS_ENDPOINTS = [
    '/ws',
    '/ws/imperium/learning-analytics',
    '/api/notifications/ws',
    '/socket.io/',
]

def check_port(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((ip, port))
        s.close()
        return True
    except Exception:
        return False

def test_http_endpoints(port):
    print(f'\nTesting HTTP endpoints on port {port}...')
    working = []
    for ep in ENDPOINTS:
        url = f'http://{BACKEND_IP}:{port}{ep}'
        try:
            r = requests.get(url, timeout=4)
            if r.status_code == 200:
                print(f'  ✅ {ep} [200]')
                working.append(ep)
            else:
                print(f'  ❌ {ep} [{r.status_code}]')
        except Exception as e:
            print(f'  ❌ {ep} [error: {e}]')
    return working

def test_websocket_endpoints(port):
    print(f'\nTesting WebSocket endpoints on port {port}...')
    import websocket
    ws_working = []
    for ep in WS_ENDPOINTS:
        ws_url = f'ws://{BACKEND_IP}:{port}{ep}'
        try:
            ws = websocket.create_connection(ws_url, timeout=4)
            ws.close()
            print(f'  ✅ {ep} [WebSocket OK]')
            ws_working.append(ep)
        except Exception as e:
            print(f'  ❌ {ep} [WebSocket error: {e}]')
    return ws_working

def try_fetch_logs(port):
    for log_ep in ['/api/logs', '/logs']:
        url = f'http://{BACKEND_IP}:{port}{log_ep}'
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                print(f'\n---- Last 100 lines from {log_ep} on port {port} ----')
                lines = r.text.splitlines()
                for line in lines[-100:]:
                    print(line)
                return True
        except Exception:
            continue
    print(f'No accessible log endpoint found on port {port}.')
    return False

def main():
    print('==== Checking backend ports... ====')
    open_ports = []
    for port in PORTS:
        if check_port(BACKEND_IP, port):
            print(f'  ✅ Port {port} is open')
            open_ports.append(port)
        else:
            print(f'  ❌ Port {port} is closed')
    if 4000 not in open_ports:
        print("\n⚠️  Port 4000 is not open. The backend is NOT running on the required port 4000!")
    else:
        print("\n✅ Port 4000 is open. Proceeding with endpoint and WebSocket tests...")

    for port in open_ports:
        working_eps = test_http_endpoints(port)
        ws_eps = []
        try:
            import websocket
            ws_eps = test_websocket_endpoints(port)
        except ImportError:
            print('websocket-client not installed, skipping WebSocket tests.')
        try_fetch_logs(port)

    print('\n==== Diagnostics Summary ====')
    if 4000 not in open_ports:
        print('❌ Backend is NOT running on port 4000. Please reconfigure and restart the backend to use port 4000 for all APIs and endpoints.')
    else:
        print('✅ Backend is running on port 4000.')
    print('If WebSocket endpoints are not working, ensure your backend supports WebSocket on port 4000 and that no firewall or reverse proxy is blocking it.')
    print('If you need to restart the backend, do so via your EC2 management console or SSH.')

if __name__ == '__main__':
    main() 