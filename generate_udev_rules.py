import serial
import glob
import time
import subprocess

def get_device_info(port):
    try:
        with serial.Serial(port, 9600, timeout=1) as ser:
            time.sleep(2)  # 等待 Arduino 重置
            ser.write(b'I')
            response = ser.readline().decode().strip().split(',')
            if len(response) == 4:
                return {
                    'type': response[0],
                    'vendor_id': response[1],
                    'product_id': response[2],
                    'serial': response[3]
                }
    except:
        pass
    return None

def get_device_path(serial_number):
    try:
        result = subprocess.run(['udevadm', 'info', '--name=/dev/ttyACM0', '--attribute-walk'], 
                                capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if f'ATTRS{{serial}}=="{serial_number}"' in line:
                return line.split('"')[1]
    except:
        pass
    return None

def generate_rule(device_info, device_path):
    if device_info['type'] == "ARM_CONTROLLER":
        symlink = "arduino_arm"
    elif device_info['type'] == "MOTOR_CONTROLLER":
        symlink = "arduino_motor"
    else:
        return None

    rule = (f'SUBSYSTEM=="tty", '
            f'ATTRS{{idVendor}}=="{device_info["vendor_id"]}", '
            f'ATTRS{{idProduct}}=="{device_info["product_id"]}", '
            f'ATTRS{{serial}}=="{device_info["serial"]}", '
            f'ATTRS{{devpath}}=="{device_path}", '
            f'SYMLINK+="{symlink}", MODE="0666"')
    return rule

def main():
    arduino_ports = glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*')
    rules = []

    for port in arduino_ports:
        device_info = get_device_info(port)
        if device_info:
            device_path = get_device_path(device_info['serial'])
            if device_path:
                rule = generate_rule(device_info, device_path)
                if rule:
                    rules.append(rule)

    if rules:
        with open('/etc/udev/rules.d/99-arduino-controllers.rules', 'w') as f:
            for rule in rules:
                f.write(rule + '\n')
        
        print("udev 规则已生成并写入文件。")
        subprocess.run(['sudo', 'udevadm', 'control', '--reload-rules'])
        subprocess.run(['sudo', 'udevadm', 'trigger'])
        print("udev 规则已重新加载。")
    else:
        print("未找到 Arduino 控制器或无法识别。")

if __name__ == "__main__":
    main()
