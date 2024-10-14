import serial
import glob
import time
import subprocess
import os
import sys

def get_device_info(port):
    print(f"尝试连接到 {port}")
    try:
        with serial.Serial(port, 115200, timeout=1) as ser:
            print(f"成功打开 {port}")
            time.sleep(2)  # 等待 Arduino 重置
            
            # 清除初始输出
            while ser.in_waiting:
                initial_data = ser.readline()
                print(f"初始输出: {initial_data.decode('utf-8', errors='replace').strip()}")
            
            print("发送识别请求 'I'")
            ser.write(b'I')
            print("等待响应...")
            
            # 读取并处理所有响应
            timeout = time.time() + 5  # 5秒超时
            while time.time() < timeout:
                if ser.in_waiting:
                    response = ser.readline()
                    decoded_response = response.decode('utf-8', errors='replace').strip()
                    print(f"收到响应: {decoded_response}")
                    
                    # 尝试解析响应
                    parts = decoded_response.split(',')
                    if len(parts) == 4 and parts[0] in ["MOTOR_CONTROLLER", "ARM_CONTROLLER"]:
                        device_info = {
                            'type': parts[0],
                            'vendor_id': parts[1],
                            'product_id': parts[2],
                            'serial': parts[3]
                        }
                        print(f"成功识别设备: {device_info}")
                        return device_info
                time.sleep(0.1)
            
            print("未收到有效响应")
    except Exception as e:
        print(f"连接到 {port} 时出错: {str(e)}")
    return None

def get_device_path(serial_number):
    print(f"尝试获取设备路径，序列号: {serial_number}")
    try:
        result = subprocess.run(['udevadm', 'info', '--name=/dev/ttyUSB0', '--attribute-walk'], 
                                capture_output=True, text=True)
        for line in result.stdout.splitlines():
            print(f"检查行: {line}")
            if f'ATTRS{{serial}}=="{serial_number}"' in line:
                device_path = line.split('"')[1]
                print(f"找到设备路径: {device_path}")
                return device_path
        print(f"未找到匹配的设备路径")
    except Exception as e:
        print(f"获取设备路径时出错: {str(e)}")
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
    print(f"找到的串口设备: {arduino_ports}")
    rules = []

    for port in arduino_ports:
        device_info = get_device_info(port)
        if device_info:
            print(f"找到设备: {device_info}")
            device_path = get_device_path(device_info['serial'])
            if device_path:
                rule = generate_rule(device_info, device_path)
                if rule:
                    print(f"生成规则: {rule}")
                    rules.append(rule)
                else:
                    print(f"无法生成规则: {device_info}")
            else:
                print(f"无法获取设备路径: {device_info['serial']}")
        else:
            print(f"无法从 {port} 获取设备信息")

    if rules:
        print(f"生成的规则: {rules}")
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
