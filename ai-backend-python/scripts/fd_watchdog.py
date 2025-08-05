#!/usr/bin/env python3
"""
File Descriptor Watchdog for Backend
Monitors open file descriptors for the backend process, learns safe/peak values, and logs warnings if usage nears the system limit.
"""
import os
import time
import psutil
import logging
import subprocess

# --- CONFIG ---
BACKEND_PROCESS_NAME = "uvicorn"  # Change if your backend process is named differently
FD_WARN_PERCENT = 80  # Warn if open FDs > 80% of limit
CHECK_INTERVAL = 60   # seconds
LEARNING_WINDOW = 100 # Number of samples to learn from
LOG_PATH = "/tmp/fd_watchdog.log"

logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

def find_backend_pid():
    """Find the backend process PID by name."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if BACKEND_PROCESS_NAME in proc.info['name'] or \
               any(BACKEND_PROCESS_NAME in str(arg) for arg in proc.info.get('cmdline', [])):
                return proc.info['pid']
        except Exception:
            continue
    return None

def get_fd_limit():
    try:
        import resource
        return resource.getrlimit(resource.RLIMIT_NOFILE)[0]
    except Exception:
        return 1024

def get_open_fds(pid):
    try:
        proc = psutil.Process(pid)
        if hasattr(proc, 'num_fds'):
            return proc.num_fds()
        fd_dir = f"/proc/{pid}/fd"
        return len(os.listdir(fd_dir))
    except Exception:
        return -1

def log_open_files(pid):
    """Log all open files and sockets for the given PID."""
    try:
        proc = psutil.Process(pid)
        files = proc.open_files()
        conns = proc.connections()
        logging.warning(f"Open files ({len(files)}): {[f.path for f in files]}")
        logging.warning(f"Open sockets ({len(conns)}): {[f'{c.laddr}->{c.raddr}' for c in conns if c.raddr]}")
    except Exception as e:
        logging.error(f"Failed to log open files/sockets: {e}")

def main():
    fd_limit = get_fd_limit()
    fd_history = []
    max_observed = 0
    adaptive_threshold = int(fd_limit * FD_WARN_PERCENT / 100)
    print(f"[FD Watchdog] Monitoring backend for open file descriptors. Limit: {fd_limit}")
    while True:
        pid = find_backend_pid()
        if not pid:
            logging.warning("Backend process not found.")
            print("[FD Watchdog] Backend process not found.")
            time.sleep(CHECK_INTERVAL)
            continue
        open_fds = get_open_fds(pid)
        if open_fds < 0:
            logging.error("Could not determine open FDs.")
            print("[FD Watchdog] Could not determine open FDs.")
            time.sleep(CHECK_INTERVAL)
            continue
        fd_history.append(open_fds)
        if len(fd_history) > LEARNING_WINDOW:
            fd_history.pop(0)
        if open_fds > max_observed:
            max_observed = open_fds
        # Adaptive threshold: if max observed is much lower than limit, relax; if close, tighten
        if max_observed > adaptive_threshold:
            adaptive_threshold = int(max_observed * 1.05)
        percent = (open_fds / fd_limit) * 100 if fd_limit else 0
        msg = f"Open FDs: {open_fds} ({percent:.1f}% of limit {fd_limit}), Adaptive threshold: {adaptive_threshold}"
        print(f"[FD Watchdog] {msg}")
        logging.info(msg)
        if open_fds > adaptive_threshold:
            warn_msg = f"WARNING: High open file descriptors: {open_fds} ({percent:.1f}% of limit {fd_limit})"
            print(f"[FD Watchdog] {warn_msg}")
            logging.warning(warn_msg)
            log_open_files(pid)
            # Attempt to restart backend service
            try:
                logging.warning("Attempting to restart backend service due to high FD usage...")
                subprocess.run(RESTART_COMMAND, check=True)
                logging.warning("Backend service restarted successfully.")
                print("[FD Watchdog] Backend service restarted.")
            except Exception as e:
                logging.error(f"Failed to restart backend service: {e}")
                print(f"[FD Watchdog] Failed to restart backend service: {e}")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main() 