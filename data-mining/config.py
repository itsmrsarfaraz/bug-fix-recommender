import os
from pathlib import Path
from dotenv import load_dotenv

# Get project root directory (one level up from data-mining/)
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / '.env')

# GitHub API
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in .env file")

# Search criteria
LANGUAGE = "Java"
MIN_STARS = 100  
MAX_REPOS = 10
BUG_FIX_KEYWORDS = ["fix", "bug", "issue", "error", "crash", "patch"]

# Local storage - ABSOLUTE PATHS
DATA_DIR = PROJECT_ROOT / "data"
REPOS_DIR = DATA_DIR / "repos"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# File filters (only analyze Java files)
FILE_EXTENSIONS = [".java"]

# Commit filters
MAX_COMMITS_PER_REPO = 1000  
MIN_CODE_LINES = 3           
MAX_CODE_LINES = 100         