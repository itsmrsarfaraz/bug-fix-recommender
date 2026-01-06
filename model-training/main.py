import sys
from trainer import BugFixTrainer
from evaluate import ModelEvaluator
import config

def main():
    """
    Run complete model training pipeline
    """
    print("\n" + "="*60)
    print("BUG FIX MODEL TRAINING PIPELINE")
    print("="*60)
    
    print("\nThis will:")
    print("1. Load CodeT5 pre-trained model")
    print("2. Fine-tune on your bug fix data")
    print("3. Evaluate on test set")
    print("4. Save the trained model")
    
    print(f"\nExpected time: 20-40 minutes (with GPU)")
    print(f"Output directory: {config.MODEL_OUTPUT_DIR}")
    
    print("\n" + "="*60)
    
    response = input("\nProceed with training? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Aborted.")
        return
    
    try:
        # Step 1: Train model
        print("\n[STEP 1/2] Training model...")
        trainer = BugFixTrainer()
        result = trainer.train()
        
        if result is None:
            print("\n⚠️  Training was interrupted")
            return
        
        # Step 2: Evaluate model
        print("\n[STEP 2/2] Evaluating model...")
        model_path = config.MODEL_OUTPUT_DIR / "final"
        evaluator = ModelEvaluator(str(model_path))
        evaluator.evaluate(num_samples=5)
        
        print("\n" + "="*60)
        print("✅ TRAINING PIPELINE COMPLETE!")
        print("="*60)
        print(f"\nTrained model saved at: {model_path}")
        print("\nNext step: Build backend API to serve the model")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()