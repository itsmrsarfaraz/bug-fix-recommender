from github import Github
import config
import json
import os

class RepoFinder:
    def __init__(self):
        """Initialize GitHub API client"""
        self.github = Github(config.GITHUB_TOKEN)
        
    def search_repos(self):
        """
        Search GitHub for Java repositories
        Returns: List of repo full names (e.g., 'apache/commons-lang')
        """
        print(f"Searching for {config.LANGUAGE} repos with {config.MIN_STARS}+ stars...")
        
        # Search query
        query = f"language:{config.LANGUAGE} stars:>={config.MIN_STARS}"
        
        # Search and get results
        repos = self.github.search_repositories(query=query, sort="stars", order="desc")
        
        selected_repos = []
        count = 0
        
        for repo in repos:
            if count >= config.MAX_REPOS:
                break
                
            repo_info = {
                "full_name": repo.full_name,
                "stars": repo.stargazers_count,
                "url": repo.clone_url,
                "description": repo.description
            }
            
            selected_repos.append(repo_info)
            print(f"  [{count+1}] {repo.full_name} - {repo.stargazers_count} stars")
            count += 1
        
        return selected_repos
    
    def save_repos(self, repos):
        """Save found repos to JSON file"""
        os.makedirs(config.DATA_DIR, exist_ok=True)
        
        output_file = os.path.join(config.DATA_DIR, "selected_repos.json")
        
        with open(output_file, 'w') as f:
            json.dump(repos, indent=2, fp=f)
        
        print(f"\nSaved {len(repos)} repositories to {output_file}")
        
    def run(self):
        """Main execution"""
        print("="*50)
        print("REPOSITORY FINDER")
        print("="*50)
        
        repos = self.search_repos()
        self.save_repos(repos)
        
        return repos


if __name__ == "__main__":
    finder = RepoFinder()
    finder.run()