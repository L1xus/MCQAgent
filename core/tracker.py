import json
import os
from datetime import datetime
import threading

STATS_FILE = "data/usage_stats.json"

class UsageTracker:
    def __init__(self):
        self._lock = threading.Lock()
        self._ensure_file()

    def _ensure_file(self):
        os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
        if not os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'w') as f:
                json.dump({
                    "total_documents_processed": 0,
                    "total_api_calls": 0,
                    "tokens": {
                        "input": 0,
                        "output": 0,
                        "total": 0
                    },
                    "costs": {
                        "total_usd_est": 0.0,
                        "avg_cost_per_doc": 0.0
                    },
                    "last_updated": None
                }, f, indent=2)

    def log_usage(self, input_tokens: int, output_tokens: int, is_new_document: bool = False):
        with self._lock:
            try:
                # Read existing data
                with open(STATS_FILE, 'r') as f:
                    data = json.load(f)
                
                # Update counters
                data["tokens"]["input"] += input_tokens
                data["tokens"]["output"] += output_tokens
                data["tokens"]["total"] += (input_tokens + output_tokens)
                
                if input_tokens > 0 or output_tokens > 0:
                    data["total_api_calls"] += 1

                if is_new_document:
                    data["total_documents_processed"] += 1
                
                input_cost = (input_tokens / 1_000_000) * 2.50
                output_cost = (output_tokens / 1_000_000) * 10.00
                data["costs"]["total_usd_est"] += (input_cost + output_cost)
                
                if data["total_documents_processed"] > 0:
                    data["costs"]["avg_cost_per_doc"] = data["costs"]["total_usd_est"] / data["total_documents_processed"]

                data["last_updated"] = datetime.now().isoformat()
                
                with open(STATS_FILE, 'w') as f:
                    json.dump(data, f, indent=2)
                    
            except Exception as e:
                print(f"⚠️ Failed to log usage: {e}")

tracker = UsageTracker()
