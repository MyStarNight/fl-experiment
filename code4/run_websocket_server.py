import logging
import argparse
import numpy as np
import torch
from torchvision import datasets
from torchvision import transforms

from torch.utils.data import ConcatDataset, DataLoader
import pickle
import syft as sy
from syft.workers import websocket_server

KEEP_LABELS_DICT = {
    "A": [1],
    "B": [2],
    "C": [3],
    "D": [4],
    "E": [5],
    "F": [6],
    "G": [7],
    "H": [8],
    "I": [9],
    "J": [10],
    "testing": [11, 12],
    None: [11, 12],
}

def start_websocket_server_worker(id, host, port, hook, verbose, task, keep_users=None, training=True):
    """Helper function for spinning up a websocket server and setting up the local datasets."""

    server = websocket_server.WebsocketServerWorker(
        id=id, host=host, port=port, hook=hook, verbose=verbose
    )

    logger.info(f"selected user: {keep_users}")

    # 加载数据集
    data_path = './data/HAR_Task_datasets.pkl'
    with open(data_path, 'rb') as f :
        HAR_datasets = pickle.load(f)

    task_str = 'task' + str(task)

    if training:
        selected_data = []
        selected_target = []
        for user in keep_users:
                selected_data.append(HAR_datasets[user][task_str][:][0])
                selected_target.append(HAR_datasets[user][task_str][:][1])

        selected_data_tensor = torch.cat(selected_data, dim=0)
        selected_target_tensor = torch.cat(selected_target, dim=0)

        dataset = sy.BaseDataset(
            data=selected_data_tensor,
            targets=selected_target_tensor
        )

        key = "HAR"

    else:
        selected_data = []
        selected_target = []
        for user in keep_users:
            selected_data.append(HAR_datasets[user][task_str][:][0])
            selected_target.append(HAR_datasets[user][task_str][:][1])

        selected_data_tensor = torch.cat(selected_data, dim=0)
        selected_target_tensor = torch.cat(selected_target, dim=0)

        dataset = sy.BaseDataset(
            data=selected_data_tensor,
            targets=selected_target_tensor.argmax(dim=1)
        )

        key = "HAR_testing"

    server.add_dataset(dataset, key)
    logger.info(f"selected datasets shape:{selected_data_tensor.shape} ")

    logger.info(f"datasets: f{server.datasets}")

    server.start()
    return server

if __name__ == '__main__':
    # Logging setup
    FORMAT = "%(asctime)s | %(message)s"
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger("run_websocket_server")
    logger.setLevel(level=logging.DEBUG)

    # Parse args
    parser = argparse.ArgumentParser(description="Run websocket server worker.")
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        help="port number of the websocket server worker, e.g. --port 8777",
    )
    parser.add_argument("--host", type=str, default="localhost", help="host for the connection")
    parser.add_argument(
        "--id", type=str, help="name (id) of the websocket server worker, e.g. --id alice"
    )
    parser.add_argument(
        "--testing",
        action="store_true",
        help="if set, websocket server worker will load the test dataset instead of the training dataset",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="if set, websocket server worker will be started in verbose mode",
    )
    parser.add_argument(
        "--task",
        "-t",
        type=int,
        help="the task of continual learning."
    )

    args = parser.parse_args()

    hook = sy.TorchHook(torch)
    server = start_websocket_server_worker(
        id=args.id,
        host=args.host,
        port=args.port,
        hook=hook,
        verbose=args.verbose,
        task=args.task,
        keep_users=KEEP_LABELS_DICT[args.id],
        training=not args.testing,
    )

