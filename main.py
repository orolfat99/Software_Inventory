import datetime
import requests
import json
import platform
import subprocess
import uuid
import winreg
import os
import shutil

def get_system_info():
    """
    Retrieves and prints system information using the platform module.
    """
    my_system = platform.uname()
    mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                            for ele in range(0, 8 * 6, 8)][::-1])
    return {
        "System": my_system.system,
        "Node Name": my_system.node,
        "Release": my_system.release,
        "Version": my_system.version,
        "Machine": my_system.machine,
        "Processor": my_system.processor,
        "MAC Address": mac_address
    }


def get_installed_software():
    """
    Retrieves a list of installed software using WMIC, the Windows Registry, and file metadata.
    """
    software_list = []

    # Get software using WMIC
    try:
        result = subprocess.run(
            ["wmic", "product", "get", "Name,Version,Vendor"],
            capture_output=True,
            text=False,  # Capture raw bytes
            shell=True
        )

        if result.returncode == 0:
            output = result.stdout.decode("cp850", errors="replace").strip()
            lines = output.splitlines()
            for line in lines[1:]:
                columns = [c.strip() for c in line.split("  ") if c.strip()]
                if len(columns) >= 1:
                    software = {
                        "Name": clean_text(columns[0]),
                        "Version": clean_text(columns[1]) if len(columns) > 1 else "N/A",
                        "Vendor": clean_text(columns[2]) if len(columns) > 2 else "N/A"
                    }
                    software_list.append(software)
    except Exception as e:
        print(f"Error using WMIC: {e}")

    # Get software from the Windows Registry
    try:
        reg_paths = [
            r"SOFTWARE/Microsoft\Windows/CurrentVersion/Uninstall",
            r"SOFTWARE/WOW6432Node/Microsoft\Windows/CurrentVersion/Uninstall"
        ]

        for reg_path in reg_paths:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                software_list.extend(query_registry_key(key))
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                software_list.extend(query_registry_key(key))

    except Exception as e:
        print(f"Error accessing registry: {e}")

    # Remove duplicates (if any) by converting to a dictionary and back to a list
    unique_software = {f"{s['Name']}|{s['Version']}|{s['Vendor']}": s for s in software_list}
    return list(unique_software.values())


def query_registry_key(key):
    """
    Helper function to query a registry key for installed software.
    """
    software_list = []
    for i in range(0, winreg.QueryInfoKey(key)[0]):
        try:
            subkey_name = winreg.EnumKey(key, i)
            with winreg.OpenKey(key, subkey_name) as subkey:
                name = clean_text(winreg.QueryValueEx(subkey, "DisplayName")[0])
                version = clean_text(winreg.QueryValueEx(subkey, "DisplayVersion")[0]) if "DisplayVersion" in winreg.QueryValueEx(subkey, "DisplayVersion") else "N/A"
                vendor = clean_text(winreg.QueryValueEx(subkey, "Publisher")[0]) if "Publisher" in winreg.QueryValueEx(subkey, "Publisher") else "N/A"
                if name:  # Only add entries with a valid name
                    software_list.append({
                        "Name": name,
                        "Version": version,
                        "Vendor": vendor
                    })
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Error reading registry: {e}")
    return software_list


def clean_text(text):
    """
    Cleans up text by ensuring proper encoding and removing invalid characters.
    """
    if not text:
        return "N/A"
    return text.encode("utf-8", errors="replace").decode("utf-8", errors="ignore").strip()


def save_to_json(data, unused, output_file):
    """
    Save the collected data to a JSON file.
    """
    try:
        with open(output_file, mode="w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"Data saved to {output_file}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")


def send_json_to_server(json_file, server_url):
    """
    Sends the JSON file to a central server.
    """
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
        response = requests.post(server_url, json=data)
        if response.status_code == 200:
            print("Data successfully sent to the server.")
        else:
            print(f"Failed to send data. Server responded with status code {response.status_code}.")
    except Exception as e:
        print(f"Error sending JSON to server: {e}")


def get_programming_languages():
    """
    Detects installed programming languages and their versions.
    """
    languages = []

    # Check Python version
    try:
        result = subprocess.run(["python", "--version"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            languages.append({"Name": "Python", "Version": result.stdout.strip(), "Vendor": "N/A"})
    except Exception as e:
        print(f"Error detecting Python: {e}")

    # Check Java version
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            version_line = result.stderr.splitlines()[0]  # Java version is printed to stderr
            languages.append({"Name": "Java", "Version": version_line.strip(), "Vendor": "N/A"})
    except Exception as e:
        print(f"Error detecting Java: {e}")

    # Check Node.js version
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            languages.append({"Name": "Node.js", "Version": result.stdout.strip(), "Vendor": "N/A"})
    except Exception as e:
        print(f"Error detecting Node.js: {e}")

    return languages


def get_development_tools():
    """
    Detects installed development tools like IDEs and build tools.
    """
    tools = []

    # Check for Visual Studio Code
    try:
        result = subprocess.run(["code", "--version"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            tools.append({"Name": "Visual Studio Code", "Version": result.stdout.splitlines()[0], "Vendor": "Microsoft"})
    except Exception as e:
        print(f"Error detecting Visual Studio Code: {e}")

    # Check for Docker
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            tools.append({"Name": "Docker", "Version": result.stdout.strip(), "Vendor": "N/A"})
    except Exception as e:
        print(f"Error detecting Docker: {e}")

    return tools


def get_environment_variables():
    """
    Collects important environment variables.
    """
    env_vars = {
        "PATH": os.environ.get("PATH", "N/A"),
        "JAVA_HOME": os.environ.get("JAVA_HOME", "N/A"),
        "PYTHONPATH": os.environ.get("PYTHONPATH", "N/A")
    }
    return env_vars


def get_network_configuration():
    """
    Collects network configuration details.
    """
    network_info = {}
    try:
        result = subprocess.run(["ipconfig"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            network_info["IPConfig"] = result.stdout.strip()
    except Exception as e:
        print(f"Error collecting network configuration: {e}")
    return network_info


def get_hardware_info():
    """
    Collects hardware information such as CPU, RAM, and disk space.
    """
    hardware_info = {}
    try:
        # CPU Information
        hardware_info["CPU"] = platform.processor()

        # RAM Information
        result = subprocess.run(["wmic", "memorychip", "get", "Capacity"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            ram_sizes = [int(x.strip()) for x in result.stdout.splitlines() if x.strip().isdigit()]
            hardware_info["RAM"] = f"{sum(ram_sizes) / (1024 ** 3):.2f} GB"

        # Disk Space
        total, used, free = shutil.disk_usage("/")
        hardware_info["Disk"] = {
            "Total": f"{total / (1024 ** 3):.2f} GB",
            "Used": f"{used / (1024 ** 3):.2f} GB",
            "Free": f"{free / (1024 ** 3):.2f} GB"
        }
    except Exception as e:
        print(f"Error collecting hardware information: {e}")
    return hardware_info


def get_user_accounts():
    """
    Collects information about user accounts on the system.
    """
    users = []
    try:
        result = subprocess.run(["net", "user"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            lines = result.stdout.splitlines()
            for line in lines[4:-2]:  # Skip header and footer
                users.extend(line.split())
    except Exception as e:
        print(f"Error collecting user accounts: {e}")
    return users


def get_security_software():
    """
    Detects installed security software (e.g., antivirus, firewall).
    """
    security_software = []
    try:
        result = subprocess.run(["wmic", "product", "get", "Name"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "antivirus" in line.lower() or "security" in line.lower() or "firewall" in line.lower():
                    security_software.append(line.strip())
    except Exception as e:
        print(f"Error detecting security software: {e}")
    return security_software


def get_running_processes():
    """
    Collects a list of running processes on the system.
    """
    processes = []
    try:
        result = subprocess.run(["tasklist"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            lines = result.stdout.splitlines()
            for line in lines[3:]:  # Skip header rows
                processes.append(line.split()[0])  # Process name is the first column
    except Exception as e:
        print(f"Error collecting running processes: {e}")
    return processes


def get_network_connections():
    """
    Collects active network connections and open ports.
    """
    connections = []
    try:
        result = subprocess.run(["netstat", "-an"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            connections = result.stdout.splitlines()
    except Exception as e:
        print(f"Error collecting network connections: {e}")
    return connections


def get_update_status():
    """
    Collects information about the system's update status.
    """
    updates = []
    try:
        result = subprocess.run(["wmic", "qfe", "list", "brief"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            updates = result.stdout.splitlines()
    except Exception as e:
        print(f"Error collecting update status: {e}")
    return updates


def get_disk_encryption_status():
    """
    Checks if disk encryption (e.g., BitLocker) is enabled.
    """
    encryption_status = {}
    try:
        result = subprocess.run(["manage-bde", "-status"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            encryption_status = result.stdout.strip()
    except Exception as e:
        print(f"Error collecting disk encryption status: {e}")
    return encryption_status


if __name__ == "__main__":
    # Configuration
    system_info = get_system_info()
    programming_languages = get_programming_languages()
    development_tools = get_development_tools()
    environment_variables = get_environment_variables()

    print("\nCollecting network configuration...")
    network_configuration = get_network_configuration()

    print("\nCollecting hardware information...")
    hardware_info = get_hardware_info()

    print("\nCollecting user accounts...")
    user_accounts = get_user_accounts()

    print("\nCollecting security software...")
    security_software = get_security_software()

    print("\nCollecting running processes...")
    running_processes = get_running_processes()

    print("\nCollecting network connections...")
    network_connections = get_network_connections()

    print("\nCollecting update status...")
    update_status = get_update_status()

    print("\nCollecting disk encryption status...")
    disk_encryption_status = get_disk_encryption_status()

    print("\nCollecting installed software...")
    software_list = get_installed_software()

    # Combine all collected data with software_list as the last key
    collected_data = {
        "system_info": system_info,
        "programming_languages": programming_languages,
        "development_tools": development_tools,
        "environment_variables": environment_variables,
        "network_configuration": network_configuration,
        "hardware_info": hardware_info,
        "user_accounts": user_accounts,
        "security_software": security_software,
        "running_processes": running_processes,
        "network_connections": network_connections,
        "update_status": update_status,
        "disk_encryption_status": disk_encryption_status,
        "software_list": software_list  # Place software_list as the last key
    }

    # Save to a JSON file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_output_file = f"all_collected_data_{timestamp}.json"
    save_to_json(collected_data, None, json_output_file)

    # Print payload before sending
    print("Payload being sent to the server:")
    print(json.dumps(collected_data, indent=4))

    # Send the JSON file to the central server
    SERVER_URL = "http://192.168.25.89:5000/api/asset"  # Replace with your server's URL
    print("\nSending JSON file to the server...")
    send_json_to_server(json_output_file, SERVER_URL)
