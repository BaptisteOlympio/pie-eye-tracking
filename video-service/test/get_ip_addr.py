import platform
import subprocess
import os

def get_ip_address():
    system = platform.system()

    print("System detected :", system)

    if system == "Windows" :
        command = "Get-NetIPAddress -AddressFamily IPv4 -InterfaceIndex $(Get-NetConnectionProfile | Select-Object -ExpandProperty InterfaceIndex) | Select-Object -ExpandProperty IPAddress"
        result = subprocess.run(["powershell.exe", command], capture_output=True, text=True)
        ipadress = result.stdout[:-1]
    elif system == "Linux" :
        command = "hostname -I | awk '{print $1}'"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        ipadress = result.stdout[:-1]
    elif system == "Darwin" :
        command = "ipconfig getifaddr en0"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        ipadress = result.stdout[:-1]
    else :
        ipadress = "Unknown OS" 

    print("IP Address :", ipadress)
    
    return ipadress

if __name__ == "__main__":
    get_ip_address()