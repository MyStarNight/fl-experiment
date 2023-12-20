#!/bin/bash

# 定义变量
HOST='192.168.1.123'
ID='G'

# 检查是否提供了参数
if [ $# -eq 0 ]; then
    echo "Usage: $0 -5|--code5 -v2|--version2"
    exit 1
fi

# 解析参数
while [ "$#" -gt 0 ]; do
    case "$1" in
        -5|--code5 )
            code5=true
            ;;
        -v2|--version2 )
            version2=true
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

# 处理选择的选项
if [ "$code5" = true ]; then
    cd /home/pi/work/fl-pj/code5; python run_websocket_server.py --host "$HOST" --port 9292 --id "$ID"
fi

if [ "$version2" = true ]; then
    cd /home/pi/work/fl-pj/v2.0; python run_websocket_server.py --host "$HOST" --port 9292 --id "$ID"
fi