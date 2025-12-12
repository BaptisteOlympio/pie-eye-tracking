# Script pour récupérer l'adresse ip de la machine qui fait tourner le code
import platform
import subprocess

system = platform.system()

if system == "Windows" :
    command = "Get-NetIPAddress -AddressFamily IPv4 -InterfaceIndex $(Get-NetConnectionProfile | Select-Object -ExpandProperty InterfaceIndex) | Select-Object -ExpandProperty IPAddress"
    result = subprocess.run(["powershell.exe", command], capture_output=True, text=True)
    ipadress = result.stdout[:-1] # on met le -1 pour retirer le retour à la ligne à la fin


print(ipadress)