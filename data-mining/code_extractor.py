import git
import json
from pathlib import Path
import config

class CodeExtractor:
    def __init__(self):
        """Initialize extractor"""
        self.repos_dir = config.REPOS_DIR
        
    def extract_code_changes(self, repo_path, commit_hash, file_path):
        """
        Extract buggy and fixed code for a specific file in a commit
        Returns: dict with buggy_code and fixed_code, or None if extraction fails
        """
        try:
            repo = git.Repo(repo_path)
            commit = repo.commit(commit_hash)
            
            # Must have parent to compare
            if not commit.parents:
                return None
            
            parent = commit.parents[0]
            
            # Get diff for this specific file
            diffs = parent.diff(commit, paths=file_path, create_patch=True)
            
            if not diffs:
                return None
            
            diff = diffs[0]
            
            # Get the actual code changes
            try:
                # Buggy code (before fix)
                buggy_code = diff.a_blob.data_stream.read().decode('utf-8', errors='ignore')
                
                # Fixed code (after fix)
                fixed_code = diff.b_blob.data_stream.read().decode('utf-8', errors='ignore')
                
            except Exception:
                return None
            
            # Filter by size constraints
            buggy_lines = buggy_code.count('\n') + 1
            fixed_lines = fixed_code.count('\n') + 1
            
            # Skip if too small or too large
            if buggy_lines < config.MIN_CODE_LINES or buggy_lines > config.MAX_CODE_LINES:
                return None
            
            if fixed_lines < config.MIN_CODE_LINES or fixed_lines > config.MAX_CODE_LINES:
                return None
            
            return {
                "buggy_code": buggy_code,
                "fixed_code": fixed_code,
                "buggy_lines": buggy_lines,
                "fixed_lines": fixed_lines
            }
            
        except Exception as e:
            return None
    
    def process_bug_fixes(self):
        """Process all bug fix commits and extract code"""
        print("="*50)
        print("CODE EXTRACTOR")
        print("="*50)
        
        # Load bug fix commits
        commits_file = config.DATA_DIR / "bug_fix_commits.json"
        
        if not commits_file.exists():
            print("❌ bug_fix_commits.json not found. Run commit_analyzer.py first!")
            return
        
        with open(commits_file, 'r') as f:
            bug_fixes = json.load(f)
        
        print(f"\nProcessing {len(bug_fixes)} bug fix commits...\n")
        
        extracted_data = []
        processed = 0
        
        for i, bug_fix in enumerate(bug_fixes, 1):
            repo_name = bug_fix['repo_name']
            repo_path = self.repos_dir / repo_name
            
            if not repo_path.exists():
                continue
            
            # Process each changed file
            for file_path in bug_fix['changed_files']:
                code_changes = self.extract_code_changes(
                    repo_path,
                    bug_fix['commit_hash'],
                    file_path
                )
                
                if code_changes:
                    extracted_data.append({
                        "repo_name": repo_name,
                        "commit_hash": bug_fix['commit_hash'],
                        "commit_message": bug_fix['commit_message'],
                        "file_path": file_path,
                        "buggy_code": code_changes['buggy_code'],
                        "fixed_code": code_changes['fixed_code'],
                        "buggy_lines": code_changes['buggy_lines'],
                        "fixed_lines": code_changes['fixed_lines']
                    })
                    processed += 1
            
            # Progress update every 50 commits
            if i % 50 == 0:
                print(f"  Processed {i}/{len(bug_fixes)} commits, extracted {processed} code pairs")
        
        # Save extracted data
        output_file = config.DATA_DIR / "extracted_bug_fixes.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, indent=2, fp=f, ensure_ascii=False)
        
        print("\n" + "="*50)
        print(f"✅ Successfully extracted: {len(extracted_data)} code pairs")
        print(f"📁 Saved to: {output_file}")
        print("="*50)
        
        return extracted_data


if __name__ == "__main__":
    extractor = CodeExtractor()
    extractor.process_bug_fixes()