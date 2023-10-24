#!/usr/bin/env python
# coding: utf-8

# # Tutorial: Asynchronous federated learning on MNIST
# 
# This notebook will go through the steps to run a federated learning via websocket workers in an asynchronous way using [TrainConfig](https://github.com/OpenMined/PySyft/blob/dev/examples/tutorials/advanced/Federated%20Learning%20with%20TrainConfig/Introduction%20to%20TrainConfig.ipynb). We will use federated averaging to join the remotely trained models.
# 
# Authors:
# - Silvia - GitHub [@midokura-silvia](https://github.com/midokura-silvia)

# In[ ]:


get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')

import inspect


# ## Federated Learning setup
# 
# For a Federated Learning setup with TrainConfig we need different participants:
# 
# * _Workers_: own datasets.
# 
# * _Coordinator_: an entity that knows the workers and the dataset name that lives in each worker. 
# 
# * _Evaluator_: holds the testing data and tracks model performance 
# 
# Each worker is represented by two parts, a proxy local to the scheduler (websocket client worker) and the remote instance that holds the data and performs the computations. The remote part is called a websocket server worker.

# ## Preparation: Start the websocket workers
# So first, we need to create the remote workers. For this, you need to run in a terminal (not possible from the notebook):
# 
# ```bash
# python start_websocket_servers.py
# ```
# 
# #### What's going on?
# 
# The script will instantiate three workers, Alice, Bob and Charlie and prepare their local data. 
# Each worker is set up to have a subset of the MNIST training dataset. 
# Alice holds all images corresponding to the digits 0-3, 
# Bob holds all images corresponding to the digits 4-6 and 
# Charlie holds all images corresponding to the digits 7-9. 
# 
# | Worker      | Digits in local dataset | Number of samples |
# | ----------- | ----------------------- | ----------------- |
# | Alice       | 0-3                     | 24754             |
# | Bob         | 4-6                     | 17181             |
# | Charlie     | 7-9                     | 18065             |
# 
# 
# The evaluator will be called Testing and holds the entire MNIST testing dataset.
# 
# | Evaluator   | Digits in local dataset | Number of samples |
# | ----------- | ----------------------- | ----------------- |
# | Testing     | 0-9                     | 10000             |
# 

# In[ ]:


# uncomment the following to see the code of the function that starts a worker
# import run_websocket_server

# print(inspect.getsource(run_websocket_server.start_websocket_server_worker))


# Before continuing let's first need to import dependencies, setup needed arguments and configure logging.

# In[ ]:


# Dependencies
import sys
import asyncio

import syft as sy
from syft.workers.websocket_client import WebsocketClientWorker
from syft.frameworks.torch.fl import utils

import torch
from torchvision import datasets, transforms
import numpy as np

import run_websocket_client as rwc


# In[ ]:


# Hook torch
hook = sy.TorchHook(torch)


# In[ ]:


# Arguments
args = rwc.define_and_get_arguments(args=[])
use_cuda = args.cuda and torch.cuda.is_available()
torch.manual_seed(args.seed)
device = torch.device("cuda" if use_cuda else "cpu")
print(args)


# In[ ]:


# Configure logging
import logging

logger = logging.getLogger("run_websocket_client")

if not len(logger.handlers):
    FORMAT = "%(asctime)s - %(message)s"
    DATE_FMT = "%H:%M:%S"
    formatter = logging.Formatter(FORMAT, DATE_FMT)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
LOG_LEVEL = logging.DEBUG
logger.setLevel(LOG_LEVEL)


# Now let's instantiate the websocket client workers, our local proxies to the remote workers.
# Note that **this step will fail, if the websocket server workers are not running**.
# 
# The workers Alice, Bob and Charlie will perform the training, wheras the testing worker hosts the test data and performs the evaluation.

# In[ ]:


# kwargs_websocket = {"host": "0.0.0.0", "hook": hook, "verbose": args.verbose}
# alice = WebsocketClientWorker(id="alice", port=8777, **kwargs_websocket)
# bob = WebsocketClientWorker(id="bob", port=8778, **kwargs_websocket)
# charlie = WebsocketClientWorker(id="charlie", port=8779, **kwargs_websocket)
# testing = WebsocketClientWorker(id="testing", port=8780, **kwargs_websocket)
#
# worker_instances = [alice, bob, charlie]

kwargs_websocket = {"host": "192.168.3.30", "hook": hook, "verbose": args.verbose}
alice = WebsocketClientWorker(id="alice", port=8777, **kwargs_websocket)
testing = WebsocketClientWorker(id="testing", port=8779, **kwargs_websocket)

# worker_instances = [alice, bob, charlie]
worker_instances = [alice ]

# ## Setting up the training

# ### Model
# Let's instantiate the machine learning model. It is a small neural network with 2 convolutional and two fully connected layers. 
# It uses ReLU activations and max pooling.

# In[ ]:


print(inspect.getsource(rwc.Net))


# In[ ]:


model = rwc.Net().to(device)
print(model)


# #### Making the model serializable
# 
# In order to send the model to the workers we need the model to be serializable, for this we use [`jit`](https://pytorch.org/docs/stable/jit.html).

# In[ ]:


traced_model = torch.jit.trace(model, torch.zeros([1, 1, 28, 28], dtype=torch.float))


# ### Let's start the training
# 
# Now we are ready to start the federated training. We will perform training over a given number of batches separately on each worker and then calculate the federated average of the resulting model.
# 
# Every 10th training round we will evaluate the performance of the models returned by the workers and of the model obtained by federated averaging. 
# 
# The performance will be given both as the accuracy (ratio of correct predictions) and as the histograms of predicted digits. This is of interest, as each worker only owns a subset of the digits. Therefore, in the beginning each worker will only predict their numbers and only know about the other numbers via the federated averaging process.
# 
# The training is done in an asynchronous manner. This means that the scheduler just tell the workers to train and does not block to wait for the result of the training before talking to the next worker.

# The parameters of the training are given in the arguments. 
# Each worker will train on a given number of batches, given by the value of federate_after_n_batches.
# The training batch size and learning rate are also configured. 

# In[ ]:


print("Federate_after_n_batches: " + str(args.federate_after_n_batches))
print("Batch size: " + str(args.batch_size))
print("Initial learning rate: " + str(args.lr))


# In[ ]:


learning_rate = args.lr
device = "cpu"  #torch.device("cpu")
traced_model = torch.jit.trace(model, torch.zeros([1, 1, 28, 28], dtype=torch.float))
for curr_round in range(1, args.training_rounds + 1):
    logger.info("Training round %s/%s", curr_round, args.training_rounds)

    results = await asyncio.gather(
        *[
            rwc.fit_model_on_worker(
                worker=worker,
                traced_model=traced_model,
                batch_size=args.batch_size,
                curr_round=curr_round,
                max_nr_batches=args.federate_after_n_batches,
                lr=learning_rate,
            )
            for worker in worker_instances
        ]
    )
    models = {}
    loss_values = {}

    test_models = curr_round % 10 == 1 or curr_round == args.training_rounds
    if test_models:
        logger.info("Evaluating models")
        np.set_printoptions(formatter={"float": "{: .0f}".format})
        for worker_id, worker_model, _ in results:
            rwc.evaluate_model_on_worker(
                model_identifier="Model update " + worker_id,
                worker=testing,
                dataset_key="mnist_testing",
                model=worker_model,
                nr_bins=10,
                batch_size=128,
                print_target_hist=False,
                device=device
            )

    # Federate models (note that this will also change the model in models[0]
    for worker_id, worker_model, worker_loss in results:
        if worker_model is not None:
            models[worker_id] = worker_model
            loss_values[worker_id] = worker_loss

    traced_model = utils.federated_avg(models)

    if test_models:
        rwc.evaluate_model_on_worker(
            model_identifier="Federated model",
            worker=testing,
            dataset_key="mnist_testing",
            model=traced_model,
            nr_bins=10,
            batch_size=128,
            print_target_hist=False,
            device=device
        )

    # decay learning rate
    learning_rate = max(0.98 * learning_rate, args.lr * 0.01)

if args.save_model:
    torch.save(model.state_dict(), "mnist_cnn.pt")


# After 40 rounds of training we achieve an accuracy larger than 95% on the entire testing dataset. 
# This is impressing, given that no worker has access to more than 4 digits!!

# # Congratulations!!! - Time to Join the Community!
# 
# Congratulations on completing this notebook tutorial! If you enjoyed this and would like to join the movement toward privacy preserving, decentralized ownership of AI and the AI supply chain (data), you can do so in the following ways!
# 
# ### Star PySyft on GitHub
# 
# The easiest way to help our community is just by starring the GitHub repos! This helps raise awareness of the cool tools we're building.
# 
# - [Star PySyft](https://github.com/OpenMined/PySyft)
# 
# ### Join our Slack!
# 
# The best way to keep up to date on the latest advancements is to join our community! You can do so by filling out the form at [http://slack.openmined.org](http://slack.openmined.org)
# 
# ### Join a Code Project!
# 
# The best way to contribute to our community is to become a code contributor! At any time you can go to PySyft GitHub Issues page and filter for "Projects". This will show you all the top level Tickets giving an overview of what projects you can join! If you don't want to join a project, but you would like to do a bit of coding, you can also look for more "one off" mini-projects by searching for GitHub issues marked "good first issue".
# 
# - [PySyft Projects](https://github.com/OpenMined/PySyft/issues?q=is%3Aopen+is%3Aissue+label%3AProject)
# - [Good First Issue Tickets](https://github.com/OpenMined/PySyft/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22)
# 
# ### Donate
# 
# If you don't have time to contribute to our codebase, but would still like to lend support, you can also become a Backer on our Open Collective. All donations go toward our web hosting and other community expenses such as hackathons and meetups!
# 
# [OpenMined's Open Collective Page](https://opencollective.com/openmined)

# In[ ]:




