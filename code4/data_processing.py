import pickle
from torch.utils.data import TensorDataset, DataLoader
import torch

path = 'data/HAR_datasets.pkl'
with open(path, 'rb') as f:
    raw_dataset = pickle.load(f)

task_dict = {'task1':[1, 2], 'task2':[3, 4], 'task3':[5,6]}

# x_task = []
# y_task = []
# for x, y in data[1]:
#     if y.argmax() in task_dict['task1']:
#         x_task.append(x)
#         y_task.append(y)
# x_tensor = torch.cat(x_task).view(-1, 400, 3)
# y_tensor = torch.cat(y_task).view(-1, 7)
# dataset_task = TensorDataset(x_tensor, y_tensor)

processed_dataset = {}
for user in raw_dataset:
    task_dataset = {}
    raw_user_dataset = raw_dataset[user]
    for task in task_dict:
        x_task = []
        y_task = []
        for x, y in raw_user_dataset:
            if y.argmax() in task_dict[task]:
                x_task.append(x)
                y_task.append(y)
        x_tensor = torch.cat(x_task).view(-1, 400, 3)
        y_tensor = torch.cat(y_task).view(-1, 7)
        task_dataset[task] = TensorDataset(x_tensor, y_tensor)
    processed_dataset[user] = task_dataset

save_path = 'data/HAR_Task_datasets.pkl'
with open(save_path,'wb') as f:
    pickle.dump(processed_dataset, f)