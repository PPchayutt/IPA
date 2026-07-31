import os
import re
from netmiko import ConnectHandler

key_path = os.path.expanduser('~/.ssh/id_rsa')

def create_device(ip):
    return {
        'device_type': 'cisco_ios',
        'host': ip,
        'username': 'admin',
        'use_keys': True,
        'key_file': key_path,
        'fast_cli': True,
        'disabled_algorithms': {'pubkeys': ['rsa-sha2-512', 'rsa-sha2-256']}
    }

# Router R1 และ R2
routers = {
    'R1': '172.31.126.4',
    'R2': '172.31.126.5'
}

print("Start checking Active Interfaces and Uptime using Regex...\n")

for name, ip in routers.items():
    print(f"[{name} - {ip}] Retrieving data...")
    try:
        device = create_device(ip)
        net_connect = ConnectHandler(**device)
        
        # 1. ดึงข้อมูลจาก show version แล้วใช้ Regex หา Uptime
        sh_ver = net_connect.send_command("show version")
        uptime_match = re.search(r'uptime is (.*)', sh_ver)
        uptime = uptime_match.group(1) if uptime_match else "No uptime data found."
        
        # 2. ดึงข้อมูลจาก show ip int brief แล้วใช้ Regex หา Interface ที่ Active (up/up)
        sh_ip_int = net_connect.send_command("show ip interface brief")
        
        # ค้นหารูปแบบ: (ชื่อพอร์ต) (IP) (OK?) (Method) up up
        active_interfaces = re.findall(r'^(\S+)\s+(\S+)\s+\S+\s+\S+\s+up\s+up', sh_ip_int, re.MULTILINE)
        
        # แสดงผลลัพธ์
        print(f"Uptime: {uptime}")
        print("Active Interfaces (up/up):")
        
        if active_interfaces:
            for intf, ip_addr in active_interfaces:
                print(f"   - {intf} (IP: {ip_addr})")
        else:
            print("   - None of the ports are active.")
            
        net_connect.disconnect()
        print("-" * 40)
        
    except Exception as e:
        print(f"❌ Unable to connect to {ip} : {e}")
        print("-" * 40)
