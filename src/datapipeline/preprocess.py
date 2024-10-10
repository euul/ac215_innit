import os
import json
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader

def get_filepaths(directory):
    filepaths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            filepaths.append(os.path.join(root, file))
    return filepaths


class JSONDataset(Dataset):
    def __init__(self, file_paths):
        self.data = []
        for file_path in file_paths:
            with open(file_path, 'r') as f:
                file_content = f.read()
                # Split content by newlines (assuming each JSON object is on a new line)
                for json_obj in file_content.splitlines():
                    try:
                        file_data = json.loads(json_obj)
                        self.data.append(file_data)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON from {file_path}: {e}")
    def __getitem__(self, idx):
        # Get an item from the dataset based on the index
        item = self.data[idx]
        return item
    
    def __len__(self):
        return len(self.data)

directory = 'app/data/' 
file_paths = get_filepaths(directory)
json_dataset = JSONDataset(file_paths)

print(json_dataset[64])
print(len(json_dataset))


