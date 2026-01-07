import platform
import subprocess
import os
from get_ip_addr import get_ip_address

def write_ip_to_config():
    """Write the IP address to the config.py file"""
    ip_address = get_ip_address()
    config_path = os.path.join(os.path.dirname(__file__), 'config.py')
    
    with open(config_path, 'r') as f:
        lines = f.readlines()
    
    with open(config_path, 'w') as f:
        for line in lines:
            if line.startswith('IP_ADDRESS'):
                f.write(f'IP_ADDRESS = "{ip_address}"\n')
            else:
                f.write(line)
    
    print(f"IP address written to config.py: {ip_address}")

if __name__ == "__main__":
    write_ip_to_config()