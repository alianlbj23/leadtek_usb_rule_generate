# USB Device Rule Generator

This script automatically generates udev rules for specific USB devices connected to your system. It's designed to create persistent device names for USB devices based on their custom identifiers.

## Purpose

The script performs the following tasks:
1. Detects connected USB devices (ttyACM* and ttyUSB*).
2. Queries each device for a custom identifier.
3. Based on the identifier, assigns a specific device type.
4. Creates udev rules to give these devices persistent names and permissions.

## Supported Devices

Currently, the script supports two types of devices:
- Robot Arm (Custom ID: ARM001)
- Rear Wheel Motor (Custom ID: MOTOR001)

## Prerequisites

- Linux operating system with udev
- Bash shell
- Root privileges (sudo access)

## Usage

1. Make sure the script is executable:
   ```
   chmod +x create_udev_rule.sh
   ```

2. Run the script with sudo privileges:
   ```
   sudo ./create_udev_rule.sh
   ```

3. The script will automatically detect connected devices, query them, and create appropriate udev rules.

4. After the script finishes, it will reload udev rules and trigger them.

## Output

- The script creates or updates the file `/etc/udev/rules.d/99-custom-usb.rules`.
- Each detected and supported device will have a rule in this file.
- Devices will be assigned symbolic links based on their type:
  - Robot Arm: `/dev/usb_robot_arm`
  - Rear Wheel Motor: `/dev/usb_rear_wheel`

## Notes

- Ensure that your devices are connected and powered on before running the script.
- The script uses a baud rate of 115200 for communication. Adjust the `BAUD_RATE` variable if your devices use a different rate.
- The script will overwrite any existing rules in the `99-custom-usb.rules` file.

## Troubleshooting

- If a device is not detected, ensure it's properly connected and powered on.
- Check the script output for any error messages or skipped devices.
- Verify that your device responds with the expected custom ID when queried.

## Customization

To add support for new device types:
1. Add a new condition in the script to check for the new custom ID.
2. Assign an appropriate `DEVICE_TYPE` for the new device.

## License

[Specify your license here]
