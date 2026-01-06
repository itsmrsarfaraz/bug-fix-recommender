import torch
from transformers import (
    T5ForConditionalGeneration,
    RobertaTokenizer,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback
)
from dataset import load_datasets
import config
import os

class BugFixTrainer:
    def __init__(self):
        """Initialize trainer"""
        print("="*60)
        print("BUG FIX MODEL TRAINER")
        print("="*60)
        
        # Check GPU availability
        self.device = torch.device(config.DEVICE if torch.cuda.is_available() else "cpu")
        print(f"\nDevice: {self.device}")
        
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        else:
            print("⚠️  WARNING: GPU not available, training will be SLOW")
        
        # Load tokenizer
        print(f"\nLoading tokenizer: {config.MODEL_NAME}")
        self.tokenizer = RobertaTokenizer.from_pretrained(config.MODEL_NAME)
        
        # Load model
        print(f"Loading model: {config.MODEL_NAME}")
        self.model = T5ForConditionalGeneration.from_pretrained(config.MODEL_NAME)
        self.model.to(self.device)
        
        print(f"Model parameters: {self.model.num_parameters() / 1e6:.1f}M")
        
        # Load datasets
        print("\nLoading datasets...")
        self.train_dataset, self.val_dataset, self.test_dataset = load_datasets(self.tokenizer)
        
        print(f"  Train: {len(self.train_dataset)} samples")
        print(f"  Validation: {len(self.val_dataset)} samples")
        print(f"  Test: {len(self.test_dataset)} samples")
        
    def train(self):
        """Train the model"""
        print("\n" + "="*60)
        print("STARTING TRAINING")
        print("="*60)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(config.MODEL_OUTPUT_DIR),
            
            # Training parameters
            num_train_epochs=config.NUM_EPOCHS,
            per_device_train_batch_size=config.BATCH_SIZE,
            per_device_eval_batch_size=config.BATCH_SIZE,
            learning_rate=config.LEARNING_RATE,
            warmup_steps=config.WARMUP_STEPS,
            
            # Logging and saving
            logging_steps=config.LOGGING_STEPS,
            save_steps=config.SAVE_STEPS,
            eval_steps=config.EVAL_STEPS,
            save_total_limit=3,  # Keep only 3 best checkpoints
            
            # Evaluation
            eval_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            
            # Performance
            fp16=torch.cuda.is_available(),  # Mixed precision if GPU
            gradient_accumulation_steps=2,  # Effective batch size = 4*2=8
            
            # Other
            report_to="none",  # Don't use wandb/tensorboard
            remove_unused_columns=False,
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.val_dataset,
            tokenizer=self.tokenizer,
            callbacks=[
                EarlyStoppingCallback(
                    early_stopping_patience=config.EARLY_STOPPING_PATIENCE
                )
            ]
        )
        
        # Start training
        print("\nTraining started...")
        print(f"Total steps: {len(self.train_dataset) // config.BATCH_SIZE * config.NUM_EPOCHS}")
        print(f"Epochs: {config.NUM_EPOCHS}")
        print(f"Batch size: {config.BATCH_SIZE}")
        print(f"Learning rate: {config.LEARNING_RATE}")
        print("\nThis will take 20-40 minutes on GPU...\n")
        
        try:
            train_result = trainer.train()
            
            # Save final model
            print("\n" + "="*60)
            print("TRAINING COMPLETE!")
            print("="*60)
            
            print(f"\nFinal train loss: {train_result.training_loss:.4f}")
            
            # Save model and tokenizer
            final_model_path = config.MODEL_OUTPUT_DIR / "final"
            trainer.save_model(str(final_model_path))
            self.tokenizer.save_pretrained(str(final_model_path))
            
            print(f"\n✅ Model saved to: {final_model_path}")
            
            return trainer
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Training interrupted by user")
            # Save current state
            trainer.save_model(str(config.MODEL_OUTPUT_DIR / "interrupted"))
            print("Checkpoint saved.")
            return None
        
        except Exception as e:
            print(f"\n\n❌ Training failed: {e}")
            raise


if __name__ == "__main__":
    trainer = BugFixTrainer()
    trainer.train()