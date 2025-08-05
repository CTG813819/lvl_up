import asyncio
import logging
import subprocess
from app.core.monitoring import system_monitor, api_monitor

logger = logging.getLogger("watchdog")

# Thresholds
CPU_WARN = 80.0
CPU_CRIT = 95.0
MEM_WARN = 80.0
MEM_CRIT = 95.0
RESP_TIME_WARN = 2000  # ms
RESP_TIME_CRIT = 5000  # ms
ERROR_RATE_WARN = 0.1
ERROR_RATE_CRIT = 0.3

async def restart_backend():
    logger.critical("Watchdog: Restarting backend due to critical issue!")
    try:
        subprocess.run(["sudo", "systemctl", "restart", "ai-backend-python"], check=True)
    except Exception as e:
        logger.error(f"Watchdog: Failed to restart backend: {e}")

async def clear_cache():
    # Placeholder for cache clearing logic
    logger.warning("Watchdog: Attempting to clear cache as mitigation.")
    # Implement actual cache clearing if available

async def watchdog_loop():
    while True:
        metrics = system_monitor.get_metrics()
        api_stats = api_monitor.get_endpoint_stats()
        # 1. Check system resource usage
        cpu = metrics.get("cpu_percent", {}).get("current", 0)
        mem = metrics.get("memory_percent", {}).get("current", 0)
        if cpu >= CPU_CRIT or mem >= MEM_CRIT:
            logger.critical(f"Watchdog: CRITICAL resource usage! CPU: {cpu}%, MEM: {mem}%")
            await restart_backend()
        elif cpu >= CPU_WARN or mem >= MEM_WARN:
            logger.warning(f"Watchdog: High resource usage. CPU: {cpu}%, MEM: {mem}%")
            await clear_cache()
        # 2. Check API endpoint performance
        for endpoint, stats in api_stats.items():
            avg_resp = stats.get("avg_response_time", 0)
            error_rate = stats.get("error_rate", 0)
            if avg_resp >= RESP_TIME_CRIT or error_rate >= ERROR_RATE_CRIT:
                logger.critical(f"Watchdog: CRITICAL issue on {endpoint}. Resp: {avg_resp}ms, Error rate: {error_rate}")
                await restart_backend()
            elif avg_resp >= RESP_TIME_WARN or error_rate >= ERROR_RATE_WARN:
                logger.warning(f"Watchdog: Warning on {endpoint}. Resp: {avg_resp}ms, Error rate: {error_rate}")
                await clear_cache()
        await asyncio.sleep(30)  # Run every 30 seconds

def start_watchdog():
    loop = asyncio.get_event_loop()
    loop.create_task(watchdog_loop()) 