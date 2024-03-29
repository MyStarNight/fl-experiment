import logging
import argparse
import sys
import asyncio
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import os

import syft as sy
from syft.workers import websocket_client
from syft.workers.websocket_client import WebsocketClientWorker
from syft.frameworks.torch.fl import utils

LOG_INTERVAL = 25
logger = logging.getLogger("run_websocket_client")
# loss = nn.CrossEntropyLoss()

@torch.jit.script
def loss_fn(pred, target):
    return F.cross_entropy(pred, target.argmax(dim=1))

@torch.jit.script
def loss_fn_test(pred, target):
    return F.cross_entropy(pred, target)

class ConvNet1D(nn.Module):
    def __init__(self, input_size, num_classes):
        super(ConvNet1D, self).__init__()
        self.conv1 = nn.Conv1d(in_channels=3, out_channels=64, kernel_size=3)
        self.pool = nn.MaxPool1d(kernel_size=2)
        self.fc1 = nn.Linear(64 * ((input_size-3+1)//2), 128)
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = x.to(torch.float32)
        x = x.transpose(2, 1)
        x = self.conv1(x)
        x = torch.relu(x)
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        x = self.fc1(x)
        x = torch.relu(x)
        x = self.fc2(x)
        return x

def save_raspi_result(input, test_num):
    columns = []
    for i in '0123456789':
        columns.append('raspi' + i)
    index = [test_num * i for i in range(int(len(input)/10))]
    input_array = np.array(input).reshape((-1, 10))
    output_df = pd.DataFrame(input_array, columns=columns, index=index)
    return output_df

def define_and_get_arguments(args=sys.argv[1:]): # 选定参数
    parser = argparse.ArgumentParser(
        description="Run federated learning using websocket client workers."
    )
    parser.add_argument("--batch_size", type=int, default=32, help="batch size of the training")
    parser.add_argument(
        "--test_batch_size", type=int, default=128, help="batch size used for the test data"
    )
    parser.add_argument(
        "--training_rounds", type=int, default=100, help="number of federated learning rounds"
    )
    parser.add_argument(
        "--federate_after_n_batches",
        type=int,
        default=10,
        help="number of training steps performed on each remote worker before averaging",
    )
    parser.add_argument("--lr", type=float, default=1e-3, help="learning rate")
    parser.add_argument("--cuda", action="store_true", help="use cuda")
    parser.add_argument("--seed", type=int, default=12345, help="seed used for randomization")
    # parser.add_argument("--save_model", action="store_true", help="if set, model will be saved")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="if set, websocket client workers will be started in verbose mode",
    )
    parser.add_argument("--stage", type=int, help="continual learning stage")

    args = parser.parse_args(args=args)
    return args

async def fit_model_on_worker(
    worker: websocket_client.WebsocketClientWorker,
    traced_model: torch.jit.ScriptModule,
    batch_size: int,
    curr_round: int,
    max_nr_batches: int,
    lr: float,
    User: str
):
    """Send the model to the worker and fit the model on the worker's training data.

    Args:
        worker: Remote location, where the model shall be trained.
        traced_model: Model which shall be trained.
        batch_size: Batch size of each training step.
        curr_round: Index of the current training round (for logging purposes).
        max_nr_batches: If > 0, training on worker will stop at min(max_nr_batches, nr_available_batches).
        lr: Learning rate of each training step.

    Returns:
        A tuple containing:
            * worker_id: Union[int, str], id of the worker.
            * improved model: torch.jit.ScriptModule, model after training at the worker.
            * loss: Loss on last training batch, torch.tensor.
    """
    # print("The Training Round: ", curr_round)
    try:
        start_time = datetime.now()
        print(f"User-{User} Training start time: {start_time}")

        train_config = sy.TrainConfig(
            model=traced_model,
            loss_fn=loss_fn,
            batch_size=batch_size,
            shuffle=True,
            # max_nr_batches=max_nr_batches,
            epochs=3,
            optimizer="SGD",
            optimizer_args={"lr": lr},
        )
        train_config.send(worker)
        # 远程训练模型；等待远程训练模型的完成
        loss = await worker.async_fit(dataset_key="HAR", return_ids=[0])
        model = train_config.model_ptr.get().obj

        end_time = datetime.now()
        print(f"User-{User} Training end time: {end_time}")
        consuming_time = end_time - start_time

        return worker.id, model, loss, consuming_time.total_seconds()

    except Exception as e:
        print(f"User-{User} {datetime.now()} Inaccessible: {e}")
        return worker.id, None, None, None

def evaluate_model_on_worker(
    model_identifier,
    worker,
    dataset_key,
    model,
    nr_bins,
    batch_size,
    device,
    print_target_hist=False,
):
    model.eval()

    # Create and send train config
    train_config = sy.TrainConfig(
        batch_size=batch_size, model=model, loss_fn=loss_fn_test, optimizer_args=None, epochs=1
    )

    train_config.send(worker)

    result = worker.evaluate(
        dataset_key=dataset_key,
        return_histograms=True,
        nr_bins=nr_bins,
        return_loss=True,
        return_raw_accuracy=True,
        device=device,
    )
    test_loss = result["loss"]
    correct = result["nr_correct_predictions"]
    len_dataset = result["nr_predictions"]
    hist_pred = result["histogram_predictions"]
    hist_target = result["histogram_target"]

    if print_target_hist:
        logger.info("Target histogram: %s", hist_target)


    logger.info(
        "%s: Average loss: %s, Accuracy: %s/%s (%s%%)",
        model_identifier,
        f"{test_loss:.4f}",
        correct,
        len_dataset,
        f"{100.0 * correct / len_dataset:.2f}",
    )

    accuracy = correct / len_dataset

    return test_loss, accuracy

def visualization(input_df:pd.DataFrame, title, ylabel, log_path):
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    for column in input_df.columns:
        plt.figure(figsize=(5, 5))
        plt.plot(input_df.index, input_df[column], label=column, color='red', linewidth=2, alpha=0.7, marker='o')

        plt.xlabel('Training Round')
        plt.ylabel(ylabel)
        plt.title(f'{column}_{title}')
        plt.savefig(f'{log_path}/{column}_accuracy.png')
        plt.show()

async def main():
    args = define_and_get_arguments()
    stage = 'stage' + str(args.stage)

    if args.stage == 1:
        hook = sy.TorchHook(torch)
        loss_list = []
        accuracy_list = []
        raspi_loss_list = []
        raspi_accuracy_list = []

        raspberries = [
            {"host": "192.168.1.117", "hook": hook, "verbose": args.verbose},
            {"host": "192.168.1.118", "hook": hook, "verbose": args.verbose},
            {"host": "192.168.1.119", "hook": hook, "verbose": args.verbose},
            {"host": "192.168.1.120", "hook": hook, "verbose": args.verbose},
            {"host": "192.168.1.121", "hook": hook, "verbose": args.verbose},
            {"host": "192.168.1.122", "hook": hook, "verbose": args.verbose},
            {"host": "192.168.1.123", "hook": hook, "verbose": args.verbose},
            {"host": "192.168.1.124", "hook": hook, "verbose": args.verbose},
            {"host": "192.168.1.125", "hook": hook, "verbose": args.verbose},
            {"host": "192.168.1.127", "hook": hook, "verbose": args.verbose},
        ]

        worker_instances = []
        for raspi, id in zip(raspberries, 'ABCDEFGHIJ'):
            kwargs_websocket = raspi
            worker_instances.append(WebsocketClientWorker(id=id, port=9292, **kwargs_websocket))

        kwargs_websocket = {"host": "192.168.1.116", "hook": hook, "verbose": args.verbose}
        testing = WebsocketClientWorker(id="testing", port=9292, **kwargs_websocket)

        all_nodes = worker_instances + [testing]

        for wcw in all_nodes:
            wcw.clear_objects_remote()

        use_cuda = args.cuda and torch.cuda.is_available()

        torch.manual_seed(args.seed)

        device = torch.device("cuda" if use_cuda else "cpu")

        model = ConvNet1D(input_size=400, num_classes=7).to(device)

        traced_model = torch.jit.trace(model, torch.zeros([1, 400, 3], dtype=torch.float).to(device))
        learning_rate = args.lr

        time_list = []
        test_num = 5

        for curr_round in range(1, args.training_rounds + 1):
            logger.info("Training round %s/%s", curr_round, args.training_rounds)

            results = await asyncio.gather(
                *[
                    fit_model_on_worker(
                        worker=worker,
                        traced_model=traced_model,
                        batch_size=args.batch_size,
                        curr_round=curr_round,
                        max_nr_batches=args.federate_after_n_batches,
                        lr=learning_rate,
                        User=worker.id
                    )
                    for worker in worker_instances
                ]
            )
            models = {}
            loss_values = {}
            time_consuming = {}
            accuracy_dict = {}
            loss_test_values = {}


            test_models = curr_round % test_num == 0 or curr_round == args.training_rounds or curr_round == 1
            # test_models = True
            if test_models:
                logger.info("Evaluating models")
                np.set_printoptions(formatter={"float": "{: .0f}".format})
                for worker_id, worker_model, _, _1 in results:
                    if worker_model is not None:
                        loss, accuracy = evaluate_model_on_worker(
                            model_identifier="Model update " + worker_id,
                            worker=testing,
                            dataset_key="HAR_testing",
                            model=worker_model,
                            nr_bins=7,
                            batch_size=32,
                            device=device,
                            print_target_hist=False,
                        )
                        accuracy_dict[worker_id] = accuracy
                        loss_test_values[worker_id] = loss
                    else:
                        accuracy_dict[worker_id] = None
                        loss_test_values[worker_id] = None

                raspi_loss_list.append(loss_test_values)
                raspi_accuracy_list.append(accuracy_dict)

            # Federate models (note that this will also change the model in models[0]
            for worker_id, worker_model, worker_loss, worker_time in results:
                if worker_model is not None:
                    models[worker_id] = worker_model
                    loss_values[worker_id] = worker_loss
                    time_consuming[worker_id] = worker_time

            time_list.append(time_consuming)

            traced_model = utils.federated_avg(models)
            if curr_round == args.training_rounds:
                torch.save(traced_model.state_dict(), f"model/HAR_{stage}.pt")

            if test_models:
                loss, accuracy = evaluate_model_on_worker(
                    model_identifier="Federated model",
                    worker=testing,
                    dataset_key="HAR_testing",
                    model=traced_model,
                    nr_bins=7,
                    batch_size=128,
                    device=device,
                    print_target_hist=True,
                )
                loss_list.append(loss)
                accuracy_list.append(accuracy)

            # decay learning rate
            # learning_rate = max(0.98 * learning_rate, args.lr * 0.01)
            learning_rate =args.lr


        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d_%H-%M-%S")
        log_path = f'log/{stage}_{formatted_time}'
        if not os.path.exists(log_path):
            os.mkdir(log_path)

        # Visualization
        # loss
        plt.figure(figsize=(5, 5))
        # plt.subplot(1, 2, 1)
        # plt.plot([i * test_num for i in range(len(loss_list))], loss_list, label='Loss', color='red', linewidth=2, alpha=0.7, marker='o')
        # plt.title('Loss Function Curve')
        # plt.xlabel('Training Round')
        # plt.ylabel('Loss')
        #
        # # accuracy
        # plt.subplot(1, 2, 2)
        plt.plot([i * test_num for i in range(len(accuracy_list))], accuracy_list, label='Accuracy', color='blue', linewidth=2, alpha=0.7, marker='o')
        plt.title('Accuracy Curve')
        plt.xlabel('Training Round')
        plt.ylabel('Accuracy')

        plt.tight_layout()
        plt.savefig(f'{log_path}/accuracy.png')
        plt.show()

        # if args.save_model:
        #     torch.save(traced_model.state_dict(), f"model/HAR_{stage}.pt")


        time_df = pd.DataFrame(time_list)
        time_df.to_csv(f'{log_path}/time_consuming.csv')
        accuracy_df = pd.DataFrame(accuracy_list, index=[i * test_num for i in range(len(accuracy_list))])
        accuracy_df.to_csv(f'{log_path}/global_accuracy.csv')
        # raspi_accuracy = save_raspi_result(raspi_accuracy_list, test_num)
        raspi_accuracy = pd.DataFrame(raspi_accuracy_list, index=[i*test_num for i in range(len(accuracy_list))])
        raspi_accuracy.to_csv(f'{log_path}/raspi_accuracy.csv')
        visualization(raspi_accuracy, title='Accuracy Curve', ylabel='Accuracy', log_path=log_path + '/raspi_pic')

    else:
        hook = sy.TorchHook(torch)
        loss_list = []
        accuracy_list = []
        raspi_loss_list = []
        raspi_accuracy_list = []

        raspberries = [
            {"host": "192.168.1.117", "hook": hook, "verbose": args.verbose},
            {"host": "192.168.1.118", "hook": hook, "verbose": args.verbose},
            {"host": "192.168.1.119", "hook": hook, "verbose": args.verbose},
            {"host": "192.168.1.120", "hook": hook, "verbose": args.verbose},
            {"host": "192.168.1.121", "hook": hook, "verbose": args.verbose},
            {"host": "192.168.1.122", "hook": hook, "verbose": args.verbose},
            {"host": "192.168.1.123", "hook": hook, "verbose": args.verbose},
            {"host": "192.168.1.124", "hook": hook, "verbose": args.verbose},
            {"host": "192.168.1.125", "hook": hook, "verbose": args.verbose},
            {"host": "192.168.1.127", "hook": hook, "verbose": args.verbose},
        ]

        worker_instances = []
        for raspi, id in zip(raspberries, 'ABCDEFGHIJ'):
            kwargs_websocket = raspi
            worker_instances.append(WebsocketClientWorker(id=id, port=9292, **kwargs_websocket))

        kwargs_websocket = {"host": "192.168.1.116", "hook": hook, "verbose": args.verbose}
        testing = WebsocketClientWorker(id="testing", port=9292, **kwargs_websocket)

        all_nodes = worker_instances + [testing]

        for wcw in all_nodes:
            wcw.clear_objects_remote()

        use_cuda = args.cuda and torch.cuda.is_available()

        torch.manual_seed(args.seed)

        device = torch.device("cuda" if use_cuda else "cpu")

        model = ConvNet1D(input_size=400, num_classes=7).to(device)

        model_path = f'model/HAR_stage{str(args.stage-1)}.pt'
        checkpoint = torch.load(model_path)
        model.load_state_dict(checkpoint)
        model.train()
        traced_model = torch.jit.trace(model, torch.zeros([1, 400, 3], dtype=torch.float).to(device))
        # print(traced_model.conv1.weight.data)

        learning_rate = args.lr

        time_list = []
        test_num = 5

        for curr_round in range(1, args.training_rounds + 1):
            logger.info("Training round %s/%s", curr_round, args.training_rounds)

            results = await asyncio.gather(
                *[
                    fit_model_on_worker(
                        worker=worker,
                        traced_model=traced_model,
                        batch_size=args.batch_size,
                        curr_round=curr_round,
                        max_nr_batches=args.federate_after_n_batches,
                        lr=learning_rate,
                        User=worker.id
                    )
                    for worker in worker_instances
                ]
            )
            models = {}
            loss_values = {}
            time_consuming = {}
            accuracy_dict = {}
            loss_test_values = {}

            test_models = curr_round % test_num == 0 or curr_round == args.training_rounds or curr_round == 1
            # test_models = True
            if test_models:
                logger.info("Evaluating models")
                np.set_printoptions(formatter={"float": "{: .0f}".format})
                for worker_id, worker_model, _, _1 in results:
                    if worker_model is not None:
                        loss, accuracy = evaluate_model_on_worker(
                            model_identifier="Model update " + worker_id,
                            worker=testing,
                            dataset_key="HAR_testing",
                            model=worker_model,
                            nr_bins=7,
                            batch_size=32,
                            device=device,
                            print_target_hist=False,
                        )
                        accuracy_dict[worker_id] = accuracy
                        loss_test_values[worker_id] = loss
                    else:
                        accuracy_dict[worker_id] = None
                        loss_test_values[worker_id] = None

                raspi_loss_list.append(loss_test_values)
                raspi_accuracy_list.append(accuracy_dict)

            # Federate models (note that this will also change the model in models[0]
            for worker_id, worker_model, worker_loss, worker_time in results:
                if worker_model is not None:
                    models[worker_id] = worker_model
                    loss_values[worker_id] = worker_loss
                    time_consuming[worker_id] = worker_time

            time_list.append(time_consuming)

            traced_model = utils.federated_avg(models)
            if curr_round == args.training_rounds:
                torch.save(traced_model.state_dict(), f"model/HAR_{stage}.pt")

            if test_models:
                loss, accuracy = evaluate_model_on_worker(
                    model_identifier="Federated model",
                    worker=testing,
                    dataset_key="HAR_testing",
                    model=traced_model,
                    nr_bins=7,
                    batch_size=128,
                    device=device,
                    print_target_hist=True,
                )
                loss_list.append(loss)
                accuracy_list.append(accuracy)

            # decay learning rate
            # learning_rate = max(0.98 * learning_rate, args.lr * 0.01)
            learning_rate = args.lr

        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d_%H-%M-%S")
        log_path = f'log/{stage}_{formatted_time}'
        if not os.path.exists(log_path):
            os.mkdir(log_path)

        # Visualization
        # loss
        plt.figure(figsize=(5, 5))
        # plt.subplot(1, 2, 1)
        # plt.plot([i * test_num for i in range(len(loss_list))], loss_list, label='Loss', color='red', linewidth=2, alpha=0.7, marker='o')
        # plt.title('Loss Function Curve')
        # plt.xlabel('Training Round')
        # plt.ylabel('Loss')
        #
        # # accuracy
        # plt.subplot(1, 2, 2)
        plt.plot([i * test_num for i in range(len(accuracy_list))], accuracy_list, label='Accuracy', color='blue',
                 linewidth=2, alpha=0.7, marker='o')
        plt.title('Accuracy Curve')
        plt.xlabel('Training Round')
        plt.ylabel('Accuracy')

        plt.tight_layout()
        plt.savefig(f'{log_path}/accuracy.png')
        plt.show()

        # if args.save_model:
        #     torch.save(traced_model.state_dict(), f"model/HAR_{stage}.pt")

        time_df = pd.DataFrame(time_list)
        time_df.to_csv(f'{log_path}/time_consuming.csv')
        accuracy_df = pd.DataFrame(accuracy_list, index=[i * test_num for i in range(len(accuracy_list))])
        accuracy_df.to_csv(f'{log_path}/global_accuracy.csv')
        # raspi_accuracy = save_raspi_result(raspi_accuracy_list, test_num)
        raspi_accuracy = pd.DataFrame(raspi_accuracy_list, index=[i * test_num for i in range(len(accuracy_list))])
        raspi_accuracy.to_csv(f'{log_path}/raspi_accuracy.csv')
        visualization(raspi_accuracy, title='Accuracy Curve', ylabel='Accuracy', log_path=log_path + '/raspi_pic')

if __name__ == "__main__":
    # Logging setup
    FORMAT = "%(asctime)s | %(message)s"
    logging.basicConfig(format=FORMAT)
    logger.setLevel(level=logging.DEBUG)

    # Websockets setup
    websockets_logger = logging.getLogger("websockets")
    websockets_logger.setLevel(logging.INFO)
    websockets_logger.addHandler(logging.StreamHandler())

    # Run main
    asyncio.get_event_loop().run_until_complete(main())