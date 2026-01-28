import platform
import subprocess

def get_ip_adress():
    """
    Function to get the IP address of the host machine based on the operating system.
    Returns:
        str: The IP address of the host machine.   
    """
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

print(get_ip_adress())