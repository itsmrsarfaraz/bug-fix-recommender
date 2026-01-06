import json
import random
from pathlib import Path
import config

class DataProcessor:
    def __init__(self):
        """Initialize processor"""
        self.data_dir = config.DATA_DIR
        self.processed_dir = config.PROCESSED_DATA_DIR
        self.processed_dir.mkdir(exist_ok=True)
        
    def clean_code(self, code):
        """
        Basic code cleaning
        - Strip extra whitespace
        - Remove empty lines at start/end
        """
        lines = code.split('\n')
        
        # Remove empty lines at start and end
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        # Join back
        cleaned = '\n'.join(lines)
        
        return cleaned.strip()
    
    def prepare_dataset(self):
        """
        Load extracted data and prepare for training
        Returns: Processed dataset
        """
        print("="*50)
        print("DATA PROCESSOR")
        print("="*50)
        
        # Load extracted bug fixes
        input_file = self.data_dir / "extracted_bug_fixes.json"
        
        if not input_file.exists():
            print("❌ extracted_bug_fixes.json not found. Run code_extractor.py first!")
            return
        
        print(f"\nLoading data from {input_file}...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        print(f"Loaded {len(raw_data)} code pairs")
        
        # Process each pair
        processed_data = []
        
        for item in raw_data:
            # Clean codes
            buggy_clean = self.clean_code(item['buggy_code'])
            fixed_clean = self.clean_code(item['fixed_code'])
            
            # Skip if cleaning made it too short
            if len(buggy_clean) < 50 or len(fixed_clean) < 50:
                continue
            
            processed_item = {
                "input": buggy_clean,  # Model input
                "target": fixed_clean,  # Model output
                "metadata": {
                    "repo": item['repo_name'],
                    "commit": item['commit_hash'],
                    "file": item['file_path'],
                    "message": item['commit_message']
                }
            }
            
            processed_data.append(processed_item)
        
        print(f"After cleaning: {len(processed_data)} valid pairs")
        
        # Shuffle data
        random.seed(42)
        random.shuffle(processed_data)
        
        # Split into train/val/test (80/10/10)
        total = len(processed_data)
        train_size = int(0.8 * total)
        val_size = int(0.1 * total)
        
        train_data = processed_data[:train_size]
        val_data = processed_data[train_size:train_size + val_size]
        test_data = processed_data[train_size + val_size:]
        
        print(f"\nDataset split:")
        print(f"  Train: {len(train_data)} samples")
        print(f"  Validation: {len(val_data)} samples")
        print(f"  Test: {len(test_data)} samples")
        
        # Save splits
        splits = {
            "train": train_data,
            "validation": val_data,
            "test": test_data
        }
        
        for split_name, split_data in splits.items():
            output_file = self.processed_dir / f"{split_name}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(split_data, indent=2, fp=f, ensure_ascii=False)
            print(f"  Saved: {output_file}")
        
        # Save dataset statistics
        stats = {
            "total_samples": total,
            "train_samples": len(train_data),
            "val_samples": len(val_data),
            "test_samples": len(test_data),
            "train_ratio": 0.8,
            "val_ratio": 0.1,
            "test_ratio": 0.1
        }
        
        stats_file = self.processed_dir / "dataset_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, indent=2, fp=f)
        
        print(f"\n✅ Dataset preparation complete!")
        print(f"📁 Processed data saved to: {self.processed_dir}")
        print("="*50)
        
        return splits


if __name__ == "__main__":
    processor = DataProcessor()
    processor.prepare_dataset()