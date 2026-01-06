import json
import torch
from torch.utils.data import Dataset
from transformers import RobertaTokenizer
import config

class BugFixDataset(Dataset):
    """
    Dataset for bug fix pairs
    """
    def __init__(self, data_file, tokenizer, max_input_length, max_target_length):
        """
        Args:
            data_file: Path to JSON file (train/val/test)
            tokenizer: Tokenizer for encoding text
            max_input_length: Max length for input (buggy code)
            max_target_length: Max length for target (fixed code)
        """
        self.tokenizer = tokenizer
        self.max_input_length = max_input_length
        self.max_target_length = max_target_length
        
        # Load data
        print(f"Loading data from {data_file}...")
        with open(data_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        print(f"Loaded {len(self.data)} samples")
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        """
        Get a single sample
        Returns: Dictionary with input_ids, attention_mask, labels
        """
        item = self.data[idx]
        
        buggy_code = item['input']
        fixed_code = item['target']
        
        # Tokenize buggy code (input)
        input_encoding = self.tokenizer(
            buggy_code,
            max_length=self.max_input_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Tokenize fixed code (target)
        target_encoding = self.tokenizer(
            fixed_code,
            max_length=self.max_target_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Prepare labels (replace padding with -100 so it's ignored in loss)
        labels = target_encoding['input_ids'].squeeze()
        labels[labels == self.tokenizer.pad_token_id] = -100
        
        return {
            'input_ids': input_encoding['input_ids'].squeeze(),
            'attention_mask': input_encoding['attention_mask'].squeeze(),
            'labels': labels
        }


def load_datasets(tokenizer):
    """
    Load train, validation, and test datasets
    Returns: Tuple of (train_dataset, val_dataset, test_dataset)
    """
    train_dataset = BugFixDataset(
        config.TRAIN_FILE,
        tokenizer,
        config.MAX_INPUT_LENGTH,
        config.MAX_TARGET_LENGTH
    )
    
    val_dataset = BugFixDataset(
        config.VAL_FILE,
        tokenizer,
        config.MAX_INPUT_LENGTH,
        config.MAX_TARGET_LENGTH
    )
    
    test_dataset = BugFixDataset(
        config.TEST_FILE,
        tokenizer,
        config.MAX_INPUT_LENGTH,
        config.MAX_TARGET_LENGTH
    )
    
    return train_dataset, val_dataset, test_dataset