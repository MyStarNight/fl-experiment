import pandas as pd
import matplotlib.pyplot as plt

data_path = 'log/Accuracy2.xlsx'
df = pd.read_excel(data_path, index_col=0)

plt.figure(figsize=(16, 8))

plt_list = [(0, 15), (15, 35), (35, 60), (60, 90), (90, 125), (125, 165), (165, 210), (210, 260), (260, 305), (305, 355)]
data_num = [40*i+40 for i in range(len(plt_list))]

for i, (start, end) in enumerate(plt_list):
    label = 'stage'+str(i+1)+'-'+str(data_num[i])
    plt.plot(df.loc[start:end], marker='o', label=label)


plt.title('Accuracy Curve for different stages')
plt.xlabel('Training Rounds')
plt.ylabel('Accuracy')
plt.legend()
plt.show()