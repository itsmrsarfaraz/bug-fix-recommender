import os
from dotenv import load_dotenv

load_dotenv()

# GitHub API
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in .env file")

# Search criteria
LANGUAGE = "Java"
MIN_STARS = 100  
MAX_REPOS = 10  
BUG_FIX_KEYWORDS = ["fix", "bug", "issue", "error", "crash", "patch"]

# Local storage
DATA_DIR = "data"
REPOS_DIR = os.path.join(DATA_DIR, "repos")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

# File filters (only analyze Java files)
FILE_EXTENSIONS = [".java"]

# Commit filters
MAX_COMMITS_PER_REPO = 1000  
MIN_CODE_LINES = 3           
MAX_CODE_LINES = 100         