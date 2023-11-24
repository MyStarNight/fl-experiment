import pickle
import torch
from torch.utils.data import TensorDataset, DataLoader
from collections import Counter

data_path = 'data/shuffled_HAR_datasets.pkl'
with open(data_path, 'rb') as f:
    user_datasets = pickle.load(f)

labels = user_datasets[1].tensors[-1][0:40].argmax(dim=1)
label_counts = Counter(labels.numpy())
print(label_counts)