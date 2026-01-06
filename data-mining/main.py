import sys
from repo_finder import RepoFinder
from repo_cloner import RepoCloner
from commit_analyzer import CommitAnalyzer
from code_extractor import CodeExtractor
from data_processor import DataProcessor

def main():
    """
    Run the complete data mining pipeline
    """
    print("\n" + "="*60)
    print("BUG FIX DATA MINING PIPELINE")
    print("="*60)
    
    print("\nThis will:")
    print("1. Find Java repositories on GitHub")
    print("2. Clone repositories locally")
    print("3. Analyze commits for bug fixes")
    print("4. Extract buggy/fixed code pairs")
    print("5. Process and split data for training")
    print("\n" + "="*60)
    
    response = input("\nProceed? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Aborted.")
        return
    
    try:
        # Step 1: Find repositories
        print("\n[STEP 1/5] Finding repositories...")
        finder = RepoFinder()
        finder.run()
        
        # Step 2: Clone repositories
        print("\n[STEP 2/5] Cloning repositories...")
        cloner = RepoCloner()
        cloner.run()
        
        # Step 3: Analyze commits
        print("\n[STEP 3/5] Analyzing commits...")
        analyzer = CommitAnalyzer()
        analyzer.run()
        
        # Step 4: Extract code
        print("\n[STEP 4/5] Extracting code pairs...")
        extractor = CodeExtractor()
        extractor.process_bug_fixes()
        
        # Step 5: Process data
        print("\n[STEP 5/5] Processing dataset...")
        processor = DataProcessor()
        processor.prepare_dataset()
        
        print("\n" + "="*60)
        print("✅ PIPELINE COMPLETE!")
        print("="*60)
        print("\nNext step: Train the model using model-training/")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()