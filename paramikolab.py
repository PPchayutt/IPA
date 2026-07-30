import paramiko
import time
import os

# รายชื่อ IP ของอุปกรณ์ในวง Management
devices = [
    "172.31.126.1", # R0
    "172.31.126.2", # S0
    "172.31.126.3", # S1
    "172.31.126.4", # R1
    "172.31.126.5"  # R2
]

# ตำแหน่งไฟล์ Private Key ใน Windows
key_path = os.path.expanduser('~/.ssh/id_rsa')

def connect_with_key(ip):
    print(f"\nConnect to {ip} ...")
    try:
        # โหลด Private Key
        mykey = paramiko.RSAKey.from_private_key_file(key_path)
        
        # สร้าง SSH Client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # เชื่อมต่อโดยใช้ Public Key Auth
        client.connect(
            hostname=ip,
            username='admin',
            pkey=mykey,
            look_for_keys=False,
            allow_agent=False
        )
        
        print(f"✅ Success! Login to {ip} without using password")
        
        # ปิดการเชื่อมต่อ
        client.close()
        
    except Exception as e:
        print(f"❌ Fail to connect to {ip} : {e}")

# วนลูปเข้าอุปกรณ์ทุกตัว
for device_ip in devices:
    connect_with_key(device_ip)
