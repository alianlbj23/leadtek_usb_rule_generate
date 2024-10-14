#!/bin/bash

# 检查参数数量
if [ "$#" -ne 5 ]; then
    echo "Usage: $0 <type> <vendor_id> <product_id> <serial> <port>"
    exit 1
fi

TYPE=$1
VENDOR_ID=$2
PRODUCT_ID=$3
SERIAL=$4
PORT=$5

# 根据类型设置 symlink
if [ "$TYPE" == "ARM_CONTROLLER" ]; then
    SYMLINK="arduino_arm"
elif [ "$TYPE" == "MOTOR_CONTROLLER" ]; then
    SYMLINK="arduino_motor"
else
    echo "Unknown device type: $TYPE"
    exit 1
fi

# 获取设备路径
DEVICE_PATH=$(udevadm info --name=$PORT --attribute-walk | grep -m1 "ATTRS{devpath}" | awk -F'"' '{print $2}')

if [ -z "$DEVICE_PATH" ]; then
    echo "Failed to get device path for $PORT"
    exit 1
fi

# 生成 udev 规则
RULE="SUBSYSTEM==\"tty\", ATTRS{idVendor}==\"$VENDOR_ID\", ATTRS{idProduct}==\"$PRODUCT_ID\", ATTRS{serial}==\"$SERIAL\", ATTRS{devpath}==\"$DEVICE_PATH\", SYMLINK+=\"$SYMLINK\", MODE=\"0666\""

# 写入规则文件
echo $RULE | sudo tee /etc/udev/rules.d/99-arduino-controllers.rules > /dev/null

# 重新加载 udev 规则
sudo udevadm control --reload-rules
sudo udevadm trigger

echo "udev rule generated and applied for $TYPE"
