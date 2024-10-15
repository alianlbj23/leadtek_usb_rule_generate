#!/bin/bash

RULE_FILE="/etc/udev/rules.d/99-custom-usb.rules"
BAUD_RATE=115200

sudo rm -f "$RULE_FILE"

check_robot_arm_link() {
    if [ -e "/dev/usb_robot_arm" ]; then
        echo "Robot arm is already correctly linked. Skipping rule creation for robot arm."
        ROBOT_ARM_PORT=$(readlink -f /dev/usb_robot_arm)
        echo "Robot arm is linked to $ROBOT_ARM_PORT"
        return 0
    fi
    return 1
}

if check_robot_arm_link; then
    robot_arm_linked=true
    ROBOT_ARM_PORT=$(readlink -f /dev/usb_robot_arm)
else
    robot_arm_linked=false
    ROBOT_ARM_PORT=""
fi

for DEVICE in /dev/ttyACM* /dev/ttyUSB*; do
    if [[ -e "$DEVICE" ]]; then
        if $robot_arm_linked && [[ "$DEVICE" == "$ROBOT_ARM_PORT" ]]; then
            echo "Skipping $DEVICE as it's already linked to robot arm"
            continue
        fi

        sleep 2

        echo "Checking device: $DEVICE"

        CUSTOM_ID=$(stty -F "$DEVICE" $BAUD_RATE; echo -n "I" > "$DEVICE"; cat < "$DEVICE" | head -n 1)

        if [[ -n "$CUSTOM_ID" ]]; then
            echo "Received CUSTOM_ID: $CUSTOM_ID from $DEVICE"

            if [[ "$CUSTOM_ID" == "ARM001" ]]; then
                if $robot_arm_linked; then
                    echo "Robot arm already linked. Skipping."
                    continue
                fi
                DEVICE_TYPE="usb_robot_arm"
            elif [[ "$CUSTOM_ID" == "MOTOR001" ]]; then
                DEVICE_TYPE="usb_rear_wheel"
            else
                echo "Unknown CUSTOM_ID: $CUSTOM_ID, skipping device."
                continue
            fi

            VENDOR_ID=$(udevadm info --query=all --name="$DEVICE" | grep "ID_VENDOR_ID" | awk -F'=' '{print $2}')
            PRODUCT_ID=$(udevadm info --query=all --name="$DEVICE" | grep "ID_MODEL_ID" | awk -F'=' '{print $2}')
            KERNELS=$(udevadm info -a -n "$DEVICE" | grep -m 1 'KERNELS=="[1-9]' | awk -F '"' '{print $2}' | cut -d':' -f1)

            if [[ -n "$KERNELS" ]]; then
                RULE="SUBSYSTEM==\"tty\", ATTRS{idVendor}==\"$VENDOR_ID\", ATTRS{idProduct}==\"$PRODUCT_ID\", KERNELS==\"$KERNELS\", SYMLINK+=\"$DEVICE_TYPE\", MODE=\"0666\""
                echo "$RULE" | sudo tee -a "$RULE_FILE"
                echo "Added rule for $DEVICE_TYPE using KERNELS=$KERNELS"
            else
                echo "Failed to get KERNELS for $DEVICE"
            fi
        else
            echo "Failed to read CUSTOM_ID from $DEVICE"
        fi
    fi
done

sudo udevadm control --reload-rules
sudo udevadm trigger

echo "All rules have been added to $RULE_FILE"
