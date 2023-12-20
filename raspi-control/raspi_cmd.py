import paramiko
import shutil
import subprocess
import os

def send_folder(raspberries:list, local_folder:str, remote_folder:str):
    for raspberry in raspberries:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(raspberry["ip"], username=raspberry["username"], password=raspberry["password"])

            sftp = ssh.open_sftp()

            # 递归地复制本地文件夹到远程文件夹
            shutil.make_archive("temp_archive", 'zip', local_folder)
            sftp.put("temp_archive.zip", remote_folder + "/temp_archive.zip")
            sftp.close()

            # 解压缩文件夹
            commands = [
                f"cd {remote_folder} ; unzip temp_archive.zip",
                f"cd {remote_folder} ; rm temp_archive.zip; ls"
            ]
            for c in commands:
                stdin, stdout, stderr = ssh.exec_command(c)
                print(f"Output from {raspberry['ip']}:\n{stdout.read().decode()}")

            ssh.close()

            print(f"Sent {local_folder} to {raspberry['ip']}")
            print("="*80)

        except Exception as e:
            print(f"Failed to send {local_folder} to {raspberry['ip']}: {str(e)}")


def send_file(raspberries:list, local_file:str, remote_folder:str):
    for raspberry in raspberries:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(raspberry["ip"], username=raspberry["username"], password=raspberry["password"])

            sftp = ssh.open_sftp()
            sftp.put(local_file, remote_folder + "/" + os.path.split(local_file)[-1])
            sftp.close()

            ssh.close()

            print(f"Sent {local_file} to {raspberry['ip']}")

        except Exception as e:
            print(f"Failed to send {local_file} to {raspberry['ip']}: {str(e)}")


def command(raspberry:dict, commands_to_execute:list):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(raspberry["ip"], username=raspberry["username"], password=raspberry["password"])

        # 执行指令
        for command in commands_to_execute:
            stdin, stdout, stderr = ssh.exec_command(command)

            # 打印命令输出
            print(f"Output from {raspberry['ip']}:\n{stdout.read().decode()}")
            print("=" * 80)

        # ssh.close()

    except Exception as e:
        print(f"Failed to execute command on {raspberry['ip']}: {str(e)}")


if __name__ == '__main__':
    # 定义树莓派的IP地址、用户名和密码

    raspberries = [
        {"ip": "192.168.1.117", "username": "pi", "password": "raspberry"},
        {"ip": "192.168.1.118", "username": "pi", "password": "raspberry"},
        {"ip": "192.168.1.119", "username": "pi", "password": "raspberry"},
        {"ip": "192.168.1.120", "username": "pi", "password": "raspberry"},
        {"ip": "192.168.1.121", "username": "pi", "password": "raspberry"},
        {"ip": "192.168.1.122", "username": "pi", "password": "raspberry"},
        {"ip": "192.168.1.123", "username": "pi", "password": "raspberry"},
        {"ip": "192.168.1.124", "username": "pi", "password": "raspberry"},
        {"ip": "192.168.1.125", "username": "pi", "password": "raspberry"},
        {"ip": "192.168.1.127", "username": "pi", "password": "raspberry"},
    ]

    operation_dict = {
        1: 'send_folder',
        2: 'send_file'
    }
    operation = operation_dict[2]

    if operation == 'send_folder':
        # 要发送目标文件夹
        local_folder = r"E:\2023mem\Python-PJ\fl-experiment\data"
        remote_folder = "/home/pi/work/fl-pj/v2.0/data"

        # 执行命令
        commands_to_execute = [
                              f"mkdir {remote_folder}; cd {remote_folder}; pwd",
                                  ]
        for raspi in raspberries:
            command(raspi, commands_to_execute)

        # 发送文件夹
        send_folder(raspberries, local_folder, remote_folder)

    else:
        # 要发送的目标文件
        local_file = r"E:\2023mem\Python-PJ\fl-experiment\run_websocket_server.py"
        remote_folder = "/home/pi/work/fl-pj/v2.0"

        # 执行命令
        # commands_to_execute = [
        #                       f"mkdir /home/pi/work/fl-pj/v2.0; cd /home/pi/work/fl-pj/; ls"
        #                           ]
        # for raspi in raspberries:
        #     command(raspi, commands_to_execute)

        # 发送文件
        send_file(raspberries, local_file, remote_folder)