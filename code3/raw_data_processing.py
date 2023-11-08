import argparse
import glob
import re
import os
import pandas as pd
import numpy as np
import data_pre_processing
from torch.utils.data import TensorDataset
import torch
import torch.nn.functional as F
import pickle


def process_motion_sense_accelerometer_files(accelerometer_data_folder_path):
    """
    Preprocess the accelerometer files of the MotionSense dataset into the 'user-list' format
    Data files can be found at https://github.com/mmalekzadeh/motion-sense/tree/master/data

    Parameters:

        accelerometer_data_folder_path (str):
            the path to the folder containing the data files (unzipped)
            e.g. motionSense/B_Accelerometer_data/
            the trial folders should be directly inside it (e.g. motionSense/B_Accelerometer_data/dws_1/)

    Return:

        user_datsets (dict of {user_id: [(sensor_values, activity_labels)]})
            the processed dataset in a dictionary, of type {user_id: [(sensor_values, activity_labels)]}
            the keys of the dictionary is the user_id (participant id)
            the values of the dictionary are lists of (sensor_values, activity_labels) pairs
                sensor_values are 2D numpy array of shape (length, channels=3)
                activity_labels are 1D numpy array of shape (length)
                each pair corresponds to a separate trial
                    (i.e. time is not contiguous between pairs, which is useful for making sliding windows, where it is easy to separate trials)
    """

    # label_set = {}
    user_datasets = {}
    all_trials_folders = sorted(glob.glob(accelerometer_data_folder_path + "/*"))
    # print(all_trials_folders)

    # Loop through every trial folder
    for trial_folder in all_trials_folders:
        trial_name = os.path.split(trial_folder)[-1]
        # print(trial_name)

        # label of the trial is given in the folder name, separated by underscore
        label = trial_name.split("_")[0]
        # label_set[label] = True
        # print(trial_folder)

        # Loop through files for every user of the trail
        for trial_user_file in sorted(glob.glob(trial_folder + "/*.csv")):

            # use regex to match the user id
            user_id_match = re.search(r'(?P<user_id>[0-9]+)\.csv', os.path.split(trial_user_file)[-1])
            if user_id_match is not None:
                user_id = int(user_id_match.group('user_id'))
                # print(user_id)

                # Read file
                user_trial_dataset = pd.read_csv(trial_user_file)
                user_trial_dataset.dropna(how = "any", inplace = True)

                # Extract the x, y, z channels
                values = user_trial_dataset[["x", "y", "z"]].values
                # 返回 x、y、z 三列数据，‘.values’ 则将这些数据转换为一个 NumPy 数组

                # the label is the same during the entire trial, so it is repeated here to pad to the same length as the values
                labels = np.repeat(label, values.shape[0])

                if user_id not in user_datasets:
                    user_datasets[user_id] = []
                user_datasets[user_id].append((values, labels))
            else:
                print("[ERR] User id not found", trial_user_file)

    return user_datasets
    # 返回类型为一个字典{user_id:(values,labels) };其中values是一个array数据类型，labels是一个一维数组，一个表格为一组(values,labels)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Raw Data Processing')
    parser.add_argument('--path',default='E:/2023mem/Python-PJ/ContrastiveLearningHAR-main/B_Accelerometer_data/B_Accelerometer_data',type=str,help='')

    args = parser.parse_args()
    user_datasets = process_motion_sense_accelerometer_files(args.path)

    user_datasets_windowed = data_pre_processing.get_windows_dataset_from_user_list_format(user_datasets)

    label_list = ['null', 'sit', 'std', 'wlk', 'ups', 'dws', 'jog']
    label_list_full_name = ['null', 'sitting', 'standing', 'walking', 'walking upstairs', 'walking downstairs',
                            'jogging']
    has_null_class = True
    label_map = dict([(l, i) for i, l in enumerate(label_list)])

    user_datasets_tensor = {}

    for key in user_datasets_windowed:
        data = user_datasets_windowed[key][0]
        label = user_datasets_windowed[key][1]

        label_mapped = data_pre_processing.apply_label_map(label, label_map)
        data, label_mapped = data_pre_processing.filter_none_label(data, label_mapped)

        label_one_hot = F.one_hot(torch.from_numpy(label_mapped).to(torch.int64), num_classes = len(label_list))

        # 检错
        r = np.random.randint(len(label_mapped))
        assert label_one_hot[r].argmax() == label_mapped[r]

        datasets_tensor = TensorDataset(torch.from_numpy(data), label_one_hot)
        user_datasets_tensor[key] = datasets_tensor

    file_path = './data/HAR_datasets.pkl'
    with open(file_path, 'wb') as f:
        pickle.dump(user_datasets_tensor, f)