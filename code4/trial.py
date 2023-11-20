import matplotlib.pyplot as plt

test_num = 5
accuracy_list = [0, 0, 0, 0.011, 0.0349, 0.140, 0.3605, 0.4284]

plt.figure(figsize=(5, 5))
plt.plot([i * test_num for i in range(len(accuracy_list))], accuracy_list, label='Accuracy', color='blue',
         linewidth=2, alpha=0.7, marker='o')
plt.title('Accuracy Curve')
plt.xlabel('Training Round')
plt.ylabel('Accuracy')

plt.tight_layout()
# plt.savefig(f'{log_path}/accuracy.png')
plt.show()