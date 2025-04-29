import datetime
import requests
import json
import platform
import subprocess
import uuid
import winreg

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
    Retrieves a list of installed software using WMIC and the Windows Registry.
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
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        user_reg_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        ]

        # Query HKEY_LOCAL_MACHINE
        for reg_path in reg_paths:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                software_list.extend(query_registry_key(key))

        # Query HKEY_CURRENT_USER
        for reg_path in user_reg_paths:
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


def save_to_json(system_info, software_list, output_file):
    """
    Save the collected data to a JSON file.
    """
    try:
        data = {
            "system_info": system_info,
            "software_list": software_list
        }
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


if __name__ == "__main__":
    # Configuration
    SERVER_URL = "http://192.168.25.89:5000/api/asset"  # Replace with your server's URL
    SAVE_LOCALLY = True  # Set to True to save data locally as a backup

    print("Collecting system information...")
    system_info = get_system_info()

    print("\nCollecting installed software...")
    software_list = get_installed_software()

    if software_list:
        print(f"Total software found: {len(software_list)}")
    else:
        print("No software information retrieved.")

    # Save to a JSON file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_output_file = f"all_installed_software_{timestamp}.json"
    save_to_json(system_info, software_list, json_output_file)

    # Send the JSON file to the central server
    print("\nSending JSON file to the server...")
    send_json_to_server(json_output_file, SERVER_URL)