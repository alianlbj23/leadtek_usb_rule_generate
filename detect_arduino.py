import serial
import glob
import time
import subprocess

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
                            'serial': parts[3],
                            'port': port
                        }
                        print(f"成功识别设备: {device_info}")
                        return device_info
                time.sleep(0.1)
            
            print("未收到有效响应")
    except Exception as e:
        print(f"连接到 {port} 时出错: {str(e)}")
    return None

def main():
    arduino_ports = glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*')
    print(f"找到的串口设备: {arduino_ports}")

    for port in arduino_ports:
        device_info = get_device_info(port)
        if device_info:
            print(f"找到设备: {device_info}")
            # 调用 shell 脚本生成 udev 规则
            subprocess.run(['sudo', './generate_udev_rule.sh', 
                            device_info['type'], 
                            device_info['vendor_id'], 
                            device_info['product_id'], 
                            device_info['serial'],
                            device_info['port']])
        else:
            print(f"无法从 {port} 获取设备信息")

if __name__ == "__main__":
    main()
