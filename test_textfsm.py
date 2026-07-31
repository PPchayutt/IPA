from textfsmlab import generate_description

def test_generate_description_cisco():
    interface_name = "G0/1"
    remote_device = "R2"
    assert generate_description(interface_name, remote_device) == "Connect to G0/1 of R2"

def test_generate_description_pc():
    interface_name = ""
    remote_device = "PC"
    assert generate_description(interface_name, remote_device) == "Connect to PC"

def test_generate_description_wan():
    interface_name = ""
    remote_device = "WAN"
    assert generate_description(interface_name, remote_device) == "Connect to WAN"
