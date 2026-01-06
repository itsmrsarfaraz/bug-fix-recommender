import os
import git
from pathlib import Path
import config
import json

class CommitAnalyzer:
    def __init__(self):
        """Initialize analyzer"""
        self.repos_dir = config.REPOS_DIR
        self.bug_keywords = config.BUG_FIX_KEYWORDS
        
    def is_bug_fix_commit(self, commit_message):
        """
        Check if commit message indicates a bug fix
        Returns: True if bug fix, False otherwise
        """
        message_lower = commit_message.lower()
        
        # Check if any bug fix keyword is in message
        return any(keyword in message_lower for keyword in self.bug_keywords)
    
    def analyze_repo(self, repo_path):
        """
        Analyze a single repository for bug fix commits
        Returns: List of bug fix commit info
        """
        repo_name = repo_path.name
        print(f"  📊 Analyzing: {repo_name}")
        
        try:
            repo = git.Repo(repo_path)
        except Exception as e:
            print(f"  ❌ Failed to open repo: {e}")
            return []
        
        bug_fixes = []
        commit_count = 0
        
        # Iterate through commits
        for commit in repo.iter_commits(max_count=config.MAX_COMMITS_PER_REPO):
            commit_count += 1
            
            # Check if bug fix
            if self.is_bug_fix_commit(commit.message):
                
                # Get changed files (only Java files)
                changed_files = []
                
                try:
                    # Get parent commit to compare
                    if commit.parents:
                        parent = commit.parents[0]
                        diffs = parent.diff(commit)
                        
                        for diff in diffs:
                            # Check if Java file
                            if diff.a_path and any(diff.a_path.endswith(ext) for ext in config.FILE_EXTENSIONS):
                                changed_files.append(diff.a_path)
                
                except Exception as e:
                    # Skip commits with diff errors
                    continue
                
                # Only include if Java files were changed
                if changed_files:
                    bug_fix_info = {
                        "repo_name": repo_name,
                        "commit_hash": commit.hexsha,
                        "commit_message": commit.message.strip(),
                        "author": str(commit.author),
                        "date": commit.committed_datetime.isoformat(),
                        "changed_files": changed_files
                    }
                    bug_fixes.append(bug_fix_info)
        
        print(f"    ✅ Found {len(bug_fixes)} bug fixes out of {commit_count} commits")
        return bug_fixes
    
    def run(self):
        """Analyze all cloned repositories"""
        print("="*50)
        print("COMMIT ANALYZER")
        print("="*50)
        
        if not self.repos_dir.exists():
            print("❌ No repositories found. Run repo_cloner.py first!")
            return
        
        all_bug_fixes = []
        
        # Get all repo directories
        repo_dirs = [d for d in self.repos_dir.iterdir() if d.is_dir()]
        
        print(f"\nAnalyzing {len(repo_dirs)} repositories...\n")
        
        for i, repo_dir in enumerate(repo_dirs, 1):
            print(f"[{i}/{len(repo_dirs)}]")
            bug_fixes = self.analyze_repo(repo_dir)
            all_bug_fixes.extend(bug_fixes)
            print()
        
        # Save results
        output_file = config.DATA_DIR / "bug_fix_commits.json"
        with open(output_file, 'w') as f:
            json.dump(all_bug_fixes, indent=2, fp=f)
        
        print("="*50)
        print(f"✅ Total bug fix commits found: {len(all_bug_fixes)}")
        print(f"📁 Saved to: {output_file}")
        print("="*50)
        
        return all_bug_fixes


if __name__ == "__main__":
    analyzer = CommitAnalyzer()
    analyzer.run()