from dotenv import load_dotenv
load_dotenv()
import os
import requests
import asyncio
import time
from collections import defaultdict

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


def call_claude(prompt, model="claude-3-5-sonnet-20241022", max_tokens=1024):
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set.")
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["content"][0]["text"]

# Anthropic Opus 4 limits (with 15% buffer)
MAX_REQUESTS_PER_MIN = 42  # 50 * 0.85
MAX_TOKENS_PER_REQUEST = 17000  # 20,000 * 0.85
MAX_REQUESTS_PER_DAY = 3400  # 4,000 * 0.85
AI_NAMES = ["imperium", "guardian", "sandbox", "conquest"]

# Track requests per AI
_request_counts_minute = defaultdict(list)  # {ai_name: [timestamps]}
_request_counts_day = defaultdict(list)     # {ai_name: [timestamps]}
_rate_limiter_lock = asyncio.Lock()

async def anthropic_rate_limited_call(prompt, ai_name, model="claude-3-5-sonnet-20241022", max_tokens=1024):
    """Async wrapper for call_claude with per-AI and global rate limiting."""
    if ai_name not in AI_NAMES:
        ai_name = "imperium"  # fallback
    now = time.time()
    async with _rate_limiter_lock:
        # Clean up old timestamps
        _request_counts_minute[ai_name] = [t for t in _request_counts_minute[ai_name] if now - t < 60]
        _request_counts_day[ai_name] = [t for t in _request_counts_day[ai_name] if now - t < 86400]
        # Enforce per-minute and per-day limits
        while (len(_request_counts_minute[ai_name]) >= MAX_REQUESTS_PER_MIN or
               len(_request_counts_day[ai_name]) >= MAX_REQUESTS_PER_DAY):
            await asyncio.sleep(1)
            now = time.time()
            _request_counts_minute[ai_name] = [t for t in _request_counts_minute[ai_name] if now - t < 60]
            _request_counts_day[ai_name] = [t for t in _request_counts_day[ai_name] if now - t < 86400]
        # Register this request
        _request_counts_minute[ai_name].append(now)
        _request_counts_day[ai_name].append(now)
    # Enforce token limit
    if max_tokens > MAX_TOKENS_PER_REQUEST:
        max_tokens = MAX_TOKENS_PER_REQUEST
    # Call Claude
    return call_claude(prompt, model=model, max_tokens=max_tokens) 