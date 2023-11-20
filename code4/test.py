import torch
import pickle
import torch.nn as nn
from run_websocket_client import ConvNet1D
from torch.utils.data import TensorDataset, DataLoader
import numpy as np

data_path = 'data/HAR_datasets.pkl'
with open(data_path, 'rb') as f:
    HAR_datasets = pickle.load(f)

selected_data = []
selected_target = []
for user in [11, 12]:
    selected_data.append(HAR_datasets[user][:][0])
    selected_target.append(HAR_datasets[user][:][1])

selected_data_tensor = torch.cat(selected_data, dim=0)
selected_target_tensor = torch.cat(selected_target, dim=0).argmax(dim=1)
Test_Data = TensorDataset(selected_data_tensor, selected_target_tensor)

model_path = "model/HAR_task3.pt"
model = ConvNet1D(input_size=400, num_classes=7)
model.load_state_dict(torch.load(model_path))
traced_model = torch.jit.trace(model, torch.zeros([1, 400, 3], dtype=torch.float))
traced_model.eval()

# print(model)
for name, param in model.named_parameters():
    print(f"{name}: {param.shape}")
print(type(traced_model.conv1.weight.data))
temp = traced_model.conv1.weight.data

test_loader = DataLoader(Test_Data, batch_size=32)


test_correct = 0
test_total = 0
class_labels = [0, 1, 2, 3, 4, 5, 6]  # Replace with your actual class labels

# Initialize a dictionary to store correct and total predictions for each class
class_correct = {label: 0 for label in class_labels}
class_total = {label: 0 for label in class_labels}

with torch.no_grad():
    for inputs, targets in test_loader:
        outputs = traced_model(inputs)
        _, predicted = torch.max(outputs, 1)

        test_total += targets.size(0)
        test_correct += (predicted == targets).sum().item()

        # Update class-wise correct and total predictions
        for label in class_labels:
            class_mask = targets == label
            class_correct[label] += (predicted[class_mask] == targets[class_mask]).sum().item()
            class_total[label] += class_mask.sum().item()

# Print overall accuracy
print(f'Test Accuracy: {(test_correct / test_total) * 100:.2f}%')

# Print class-wise accuracy
for label in class_labels:
    accuracy = (class_correct[label] / class_total[label]) * 100 if class_total[label] != 0 else 0
    print(f'Class {label} Accuracy: {accuracy:.2f}%')

