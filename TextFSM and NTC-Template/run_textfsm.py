import os
import ntc_templates
from netmiko import ConnectHandler
from textfsmlab import generate_config_commands

ntc_path = os.path.join(os.path.dirname(ntc_templates.__file__), 'templates')
os.environ['NET_TEXTFSM'] = ntc_path

key_path = os.path.expanduser('~/.ssh/id_rsa')
devices = [
    {
        'device_type': 'cisco_ios',
        'host': '172.31.126.3', # S1
        'username': 'admin',
        "use_keys": True,
        "key_file": key_path,
        'disabled_algorithms': {'pubkeys': ['rsa-sha2-512', 'rsa-sha2-256']},
        "edge_ports" : {"GigabitEthernet1/1": "PC"}
    },
    {
        'device_type': 'cisco_ios',
        'host': '172.31.126.4', # R1
        'username': 'admin',
        "use_keys": True,
        "key_file": key_path,
        'disabled_algorithms': {'pubkeys': ['rsa-sha2-512', 'rsa-sha2-256']},
        "edge_ports" : {"GigabitEthernet0/1": "PC"}
    },
    {
        'device_type': 'cisco_ios',
        'host': '172.31.126.5', # R2
        'username': 'admin',
        "use_keys": True,
        "key_file": key_path,
        'disabled_algorithms': {'pubkeys': ['rsa-sha2-512', 'rsa-sha2-256']},
        "edge_ports" : {"GigabitEthernet0/3": "WAN"}
    }
]

if __name__ == "__main__":
    print("Start configuring Interface Description...")
    for device in devices:
        edge_ports = device.pop('edge_ports', {})
        print(f"\nConnecting to {device['host']}...")
        
        try:
            net_connect = ConnectHandler(**device)
            parsed_cdp = net_connect.send_command('show cdp neighbors', use_textfsm=True)
            
            if isinstance(parsed_cdp, str):
                backup_data = []
                lines = parsed_cdp.splitlines()
                dev_id = ""
                for line in lines:
                    line = line.strip()
                    if not line or "Capability" in line or "Device ID" in line:
                        continue
                    parts = line.split()
                    if len(parts) == 1:
                        dev_id = parts[0]
                    elif len(parts) >= 4:
                        curr_dev = parts[0] if len(parts) >= 6 and not parts[0].startswith("Gig") and not parts[0].startswith("Fas") else dev_id
                        if curr_dev:
                            local_p = [p for p in parts if "Gig" in p or "Fas" in p or "Eth" in p or "0/" in p or "1/" in p]
                            if len(local_p) >= 2:
                                backup_data.append({
                                    "destination_host": curr_dev,
                                    "local_interface": local_p[0],
                                    "port_id": local_p[1]
                                })
                            elif len(local_p) == 1 and len(parts) >= 5:
                                backup_data.append({
                                    "destination_host": curr_dev,
                                    "local_interface": local_p[0],
                                    "port_id": parts[-1]
                                })
                            dev_id = ""
                parsed_cdp = backup_data

            if not isinstance(parsed_cdp, list):
                parsed_cdp = []
                
            commands = generate_config_commands(parsed_cdp, edge_ports)
            
            if commands:
                net_connect.send_config_set(commands)
                net_connect.save_config()
                print("✅ Configuration successful!")
            else:
                print("⚠️ No commands to apply.")
                
            net_connect.disconnect()
        except Exception as e:
            print(f"❌ Error: {e}")
