# config.py - paths, env loading, sources list
import os
from pathlib import Path

HUNTER_DIR = Path(__file__).resolve().parent
STATE_DIR = HUNTER_DIR / "state"
STATE_DIR.mkdir(exist_ok=True)
SEEN_FILE = STATE_DIR / "seen.json"
STATS_FILE = STATE_DIR / "stats.json"
LOG_FILE = STATE_DIR / "hunter.log"
CHAT_FILE = STATE_DIR / "chat_id.txt"


def _load_env():
    env_path = HUNTER_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


_load_env()

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openrouter/free")

# sources (validated 2026-11-09, see tracker/sources.md)
FL_RSS = "https://www.fl.ru/rss/all.xml"
TG_CHANNELS = [
    "job_developer",
    "tilda_profiI",
    "sova_freelance",
    "freelance7",
    "Koteyka_Freelancer",
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
COLLECT_EVERY_SEC = 3600   # hourly
MAX_FRESH_PER_RUN = 60     # bound LLM calls
MAX_DIGEST = 10            # max messages per digest run
SEEN_CAP = 3000
