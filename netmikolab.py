import os
from netmiko import ConnectHandler

MGT_NET = "172.31.126.0 0.0.0.15"       # วง Management
LAB306_NET = "192.168.0.0 0.0.0.255"    # วง Wi-Fi บ้าน
DATA_OSPF_NET = "10.1.0.0 0.0.255.255"  # วง Control/Data ทั้งหมด

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
# S1: สร้าง VLAN 101, เอาพอร์ตเข้า VLAN และทำ ACL
s1_commands = [
    'vlan 101',
    'name Control-Data',
    'exit',
    'interface range GigabitEthernet0/1 , GigabitEthernet1/1',
    'switchport mode access',
    'switchport access vlan 101',
    'no shutdown',
    'exit',
    'ip access-list standard MGT_LAB306_ONLY',
    f'permit {MGT_NET}',
    f'permit {LAB306_NET}',
    'line vty 0 4',
    'access-class MGT_LAB306_ONLY in',
    'transport input ssh telnet'
]

# R1: ใส่ IP ลิงก์กลาง, ทำ OSPF และทำ ACL
r1_commands = [
    'interface GigabitEthernet0/2',
    'ip vrf forwarding control-data',
    'ip address 10.1.2.1 255.255.255.0',
    'no shutdown',
    'exit',
    'router ospf 1 vrf control-data',
    f'network {DATA_OSPF_NET} area 0',
    'exit',
    'ip access-list standard MGT_LAB306_ONLY',
    f'permit {MGT_NET}',
    f'permit {LAB306_NET}',
    'line vty 0 4',
    'access-class MGT_LAB306_ONLY in',
    'transport input ssh telnet'
]

# R2: ใส่ IP, ทำ OSPF, Default Route, NAT และทำ ACL
r2_commands = [
    'interface GigabitEthernet0/1',
    'ip vrf forwarding control-data',
    'ip address 10.1.2.2 255.255.255.0',
    'no shutdown',
    'exit',
    'interface GigabitEthernet0/2',
    'ip vrf forwarding control-data',
    'ip address 10.1.3.1 255.255.255.0',
    'no shutdown',
    'exit',
    'interface GigabitEthernet0/3',
    'ip vrf forwarding control-data',
    'ip address dhcp',
    'ip nat outside',
    'no shutdown',
    'exit',
    'router ospf 1 vrf control-data',
    f'network {DATA_OSPF_NET} area 0',
    'default-information originate',
    'exit',
    'ip access-list standard NAT_ACL',
    f'permit {DATA_OSPF_NET}',
    'ip nat inside source list NAT_ACL interface GigabitEthernet0/3 vrf control-data overload',
    'interface range GigabitEthernet0/1 - 2',
    'ip nat inside',
    'exit',
    'ip access-list standard MGT_LAB306_ONLY',
    f'permit {MGT_NET}',
    f'permit {LAB306_NET}',
    'line vty 0 4',
    'access-class MGT_LAB306_ONLY in',
    'transport input ssh telnet'
]

devices_config = {
    '172.31.126.3': s1_commands, # S1
    '172.31.126.4': r1_commands, # R1
    '172.31.126.5': r2_commands  # R2
}

# ยิง Script
print("Start Configuration with Netmiko...")
for ip, commands in devices_config.items():
    print(f"\nConnect to {ip} ...")
    try:
        device = create_device(ip)
        net_connect = ConnectHandler(**device)
        output = net_connect.send_config_set(commands)
        net_connect.save_config()
        print(f"✅ Success Configuration to {ip} !")
        net_connect.disconnect()
    except Exception as e:
        print(f"❌ Fail Configuration to {ip} : {e}")
