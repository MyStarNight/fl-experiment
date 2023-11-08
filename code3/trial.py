import pickle

import torch
from torch.utils.data import ConcatDataset
from torch.utils.data import DataLoader

data_path = './data/HAR_datasets.pkl'
with open(data_path, 'rb') as f:
    HAR_datasets = pickle.load(f)

keep_users = [1, 2, 3]

selected_data = []
selected_target = []
for user in keep_users:
    selected_data.append(HAR_datasets[user][:][0])
    selected_target.append(HAR_datasets[user][:][1])

selected_data_tensor = torch.cat(selected_data, dim=0)
selected_target_tensor = torch.cat(selected_target, dim=0)
print(selected_target_tensor)
# selected_data_tensor = ConcatDataset(selected_data)
# a = selected_data_tensor[0]
