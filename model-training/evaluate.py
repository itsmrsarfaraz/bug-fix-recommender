import torch
from transformers import T5ForConditionalGeneration, RobertaTokenizer
from dataset import BugFixDataset
import config
from tqdm import tqdm

class ModelEvaluator:
    def __init__(self, model_path):
        """
        Initialize evaluator
        Args:
            model_path: Path to trained model
        """
        print("="*60)
        print("MODEL EVALUATOR")
        print("="*60)
        
        self.device = torch.device(config.DEVICE if torch.cuda.is_available() else "cpu")
        print(f"\nDevice: {self.device}")
        
        # Load model and tokenizer
        print(f"\nLoading model from: {model_path}")
        self.model = T5ForConditionalGeneration.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()  # Set to evaluation mode
        
        self.tokenizer = RobertaTokenizer.from_pretrained(model_path)
        
        # Load test dataset
        print("Loading test dataset...")
        self.test_dataset = BugFixDataset(
            config.TEST_FILE,
            self.tokenizer,
            config.MAX_INPUT_LENGTH,
            config.MAX_TARGET_LENGTH
        )
    
    def generate_fix(self, buggy_code):
        """
        Generate fixed code for a single buggy code sample
        Args:
            buggy_code: String of buggy code
        Returns: String of fixed code
        """
        # Tokenize input
        input_encoding = self.tokenizer(
            buggy_code,
            max_length=config.MAX_INPUT_LENGTH,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        input_ids = input_encoding['input_ids'].to(self.device)
        attention_mask = input_encoding['attention_mask'].to(self.device)
        
        # Generate output
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_length=config.MAX_TARGET_LENGTH,
                num_beams=5,  # Beam search for better quality
                early_stopping=True
            )
        
        # Decode output
        fixed_code = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return fixed_code
    
    def evaluate(self, num_samples=10):
        """
        Evaluate model on test set
        Args:
            num_samples: Number of samples to show examples for
        """
        print("\n" + "="*60)
        print("EVALUATING ON TEST SET")
        print("="*60)
        
        print(f"\nGenerating predictions for {len(self.test_dataset)} test samples...")
        
        correct_predictions = 0
        
        # Evaluate all samples
        for i in tqdm(range(len(self.test_dataset))):
            sample = self.test_dataset.data[i]
            buggy_code = sample['input']
            expected_fix = sample['target']
            
            # Generate fix
            predicted_fix = self.generate_fix(buggy_code)
            
            # Simple accuracy check (exact match)
            if predicted_fix.strip() == expected_fix.strip():
                correct_predictions += 1
        
        accuracy = correct_predictions / len(self.test_dataset) * 100
        
        print("\n" + "="*60)
        print("EVALUATION RESULTS")
        print("="*60)
        print(f"\nExact match accuracy: {accuracy:.2f}%")
        print(f"Correct predictions: {correct_predictions}/{len(self.test_dataset)}")
        
        # Show examples
        print("\n" + "="*60)
        print(f"SHOWING {num_samples} EXAMPLE PREDICTIONS")
        print("="*60)
        
        for i in range(min(num_samples, len(self.test_dataset))):
            sample = self.test_dataset.data[i]
            buggy_code = sample['input']
            expected_fix = sample['target']
            predicted_fix = self.generate_fix(buggy_code)
            
            print(f"\n{'='*60}")
            print(f"EXAMPLE {i+1}")
            print(f"{'='*60}")
            
            print("\n🐛 BUGGY CODE:")
            print("-" * 60)
            print(buggy_code[:300] + "..." if len(buggy_code) > 300 else buggy_code)
            
            print("\n✅ EXPECTED FIX:")
            print("-" * 60)
            print(expected_fix[:300] + "..." if len(expected_fix) > 300 else expected_fix)
            
            print("\n🤖 MODEL PREDICTION:")
            print("-" * 60)
            print(predicted_fix[:300] + "..." if len(predicted_fix) > 300 else predicted_fix)
            
            # Check if correct
            match = predicted_fix.strip() == expected_fix.strip()
            print(f"\n{'✅ CORRECT' if match else '❌ INCORRECT'}")
        
        print("\n" + "="*60)


if __name__ == "__main__":
    # Evaluate the final trained model
    model_path = config.MODEL_OUTPUT_DIR / "final"
    
    if not model_path.exists():
        print(f"❌ Model not found at {model_path}")
        print("Train the model first using trainer.py")
    else:
        evaluator = ModelEvaluator(str(model_path))
        evaluator.evaluate(num_samples=5)