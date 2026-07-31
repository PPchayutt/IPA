import os
from netmiko import ConnectHandler
from jinja2 import Environment, FileSystemLoader

# ตัวแปรสำหรับเติมลงใน Template (Jinja2)
template_vars = {
    'mgt_net': '172.31.126.0 0.0.0.15',     # วง Management
    'lab306_net': '192.168.0.0 0.0.0.255',  # วง Wi-Fi บ้าน
    'ospf_net': '10.1.0.0 0.0.255.255'      # วง Control/Data ทั้งหมด
}

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

# โหลดระบบ Jinja2 (ค้นหาไฟล์ .j2 ในโฟลเดอร์ปัจจุบัน)
env = Environment(loader=FileSystemLoader('.'))

# จับคู่ IP กับไฟล์ Template
devices_config = {
    '172.31.126.3': 's1.j2', # S1
    '172.31.126.4': 'r1.j2', # R1
    '172.31.126.5': 'r2.j2'  # R2
}

# ยิง Script
print("Start Configuration with Netmiko & Jinja2...")

for ip, template_file in devices_config.items():
    print(f"\nConnect to {ip} ...")
    try:
        # ให้ Jinja2 เอาตัวแปรไปเติมในไฟล์ Template แล้วแปลงเป็นข้อความ
        template = env.get_template(template_file)
        config_string = template.render(template_vars)
        
        # หั่นข้อความออกเป็นบรรทัดๆ เพื่อให้ Netmiko เข้าใจ
        commands = config_string.splitlines()
        
        # ส่งคำสั่งเข้าอุปกรณ์
        device = create_device(ip)
        net_connect = ConnectHandler(**device)
        output = net_connect.send_config_set(commands)
        net_connect.save_config()
        print(f"✅ Success Configuration to {ip} !")
        net_connect.disconnect()
    except Exception as e:
        print(f"❌ Fail Configuration to {ip} : {e}")
    