import os
import json
import git
from pathlib import Path
import config

class RepoCloner:
    def __init__(self):
        """Initialize cloner"""
        self.repos_dir = config.REPOS_DIR
        os.makedirs(self.repos_dir, exist_ok=True)
        
    def load_repos(self):
        """Load repository list from JSON"""
        repos_file = config.DATA_DIR / "selected_repos.json"
        
        if not repos_file.exists():
            raise FileNotFoundError(f"Run repo_finder.py first! File not found: {repos_file}")
        
        with open(repos_file, 'r') as f:
            return json.load(f)
    
    def clone_repo(self, repo_info):
        """
        Clone a single repository
        Returns: True if successful, False otherwise
        """
        repo_name = repo_info['full_name'].replace('/', '_')
        repo_path = self.repos_dir / repo_name
        
        # Skip if already cloned
        if repo_path.exists():
            print(f"  ⏭️  Already exists: {repo_info['full_name']}")
            return True
        
        print(f"  📥 Cloning: {repo_info['full_name']}...")
        
        try:
            # Clone repository
            git.Repo.clone_from(
                repo_info['url'],
                repo_path,
                depth=config.MAX_COMMITS_PER_REPO  # Shallow clone (saves space/time)
            )
            print(f"  ✅ Success: {repo_info['full_name']}")
            return True
            
        except Exception as e:
            print(f"  ❌ Failed: {repo_info['full_name']} - {str(e)}")
            return False
    
    def run(self):
        """Clone all repositories"""
        print("="*50)
        print("REPOSITORY CLONER")
        print("="*50)
        
        repos = self.load_repos()
        print(f"\nFound {len(repos)} repositories to clone\n")
        
        success_count = 0
        
        for i, repo in enumerate(repos, 1):
            print(f"[{i}/{len(repos)}]")
            if self.clone_repo(repo):
                success_count += 1
            print()
        
        print("="*50)
        print(f"✅ Successfully cloned: {success_count}/{len(repos)}")
        print(f"📁 Location: {self.repos_dir}")
        print("="*50)


if __name__ == "__main__":
    cloner = RepoCloner()
    cloner.run()