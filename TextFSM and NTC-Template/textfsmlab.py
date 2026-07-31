def format_port(port_name):
    port_name = port_name.replace(" ", "")
    if port_name.startswith("GigabitEthernet"):
        return port_name.replace("GigabitEthernet", "G")
    elif port_name.startswith("Gig"):
        return port_name.replace("Gig", "G")
    elif port_name.startswith("0/") or port_name.startswith("1/"):
        return "G" + port_name
    return port_name

def generate_description(interface_name, remote_device):
    if remote_device in ["PC", "WAN"] and interface_name == "":
        return f"Connect to {remote_device}"
    else:
        formatted_intf = format_port(interface_name)
        return f"Connect to {formatted_intf} of {remote_device}"

def generate_config_commands(parsed_data, edge_ports):
    config_commands = []

    # ข้อมูล PC และ WAN
    for local_int, neighbor_dev in edge_ports.items():
        parsed_data.append({
            "destination_host": neighbor_dev,
            "local_interface": local_int,
            "port_id": ""
        })

    # สร้างคำสั่งจากข้อมูล CDP
    for item in parsed_data:
        remote_device = item.get('destination_host') or item.get('neighbor') or item.get('device_id') or ''
        remote_port = item.get('port_id') or item.get('neighbor_interface') or ''
        local_port = item.get('local_interface') or item.get('local_port') or ''

        local_port = local_port.replace(" ", "")

        # ตัดชื่อโดเมนออกถ้ามี
        if "." in remote_device:
            remote_device = remote_device.split(".")[0]

        if remote_device and local_port:
            desc_text = generate_description(remote_port, remote_device)
            config_commands.extend([
                f"interface {local_port}",
                f"description {desc_text}"
            ])

    return config_commands
