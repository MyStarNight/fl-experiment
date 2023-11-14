import run_websocket_client
import pandas as pd

df = pd.read_csv('log/2023-11-13_11-23-50/raspi_accuracy.csv')
run_websocket_client.visualization(df, title='test', ylabel='test', log_path='log/2023-11-13_11-23-50')