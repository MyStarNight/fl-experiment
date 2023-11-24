import pickle
import torch
from torch.utils.data import TensorDataset, DataLoader

data_path = 'data/HAR_datasets.pkl'
with open(data_path, 'rb') as f:
    user_datasets = pickle.load(f)

shuffled_user_datasets = {}
for user in user_datasets:
    indices = torch.randperm(len(user_datasets[user]))
    data_list = []
    label_list = []
    for index in indices:
        data_list.append(user_datasets[user][index][0])
        label_list.append(user_datasets[user][index][1])
    data_tensor = torch.cat(data_list).view(-1, 400, 3)
    label_tensor = torch.cat(label_list).view(-1, 7)
    shuffled_dataset = TensorDataset(data_tensor, label_tensor)
    shuffled_user_datasets[user] = shuffled_dataset

save_path = "data/shuffled_HAR_datasets.pkl"
with open(save_path, 'wb') as f:
    pickle.dump(shuffled_user_datasets, f)