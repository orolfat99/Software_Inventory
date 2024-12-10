# MAC address
# Node Name: P10241201-PC


# import subprocess
# import csv
# import datetime

# def get_installed_software():
#     """
#     Retrieves a list of installed software using the WMIC command.
#     """
#     try:
#         # Run WMIC command to get software list
#         result = subprocess.run(
#             ["wmic", "product", "get", "Name,Version,Vendor"],
#             capture_output=True,
#             text=True,
#             shell=True
#         )

#         software_list = []
#         if result.returncode == 0:
#             lines = result.stdout.strip().splitlines()
#             headers = [h.strip() for h in lines[0].split()]
#             for line in lines[1:]:
#                 columns = [c.strip() for c in line.split("  ") if c.strip()]
#                 if len(columns) >= 1:
#                     software = {
#                         "Name": columns[0],
#                         "Version": columns[1] if len(columns) > 1 else "N/A",
#                         "Vendor": columns[2] if len(columns) > 2 else "N/A"
#                     }
#                     software_list.append(software)
#         else:
#             print("Error fetching software:", result.stderr)
#         return software_list

#     except Exception as e:
#         print(f"Error: {e}")
#         return []

# def save_to_csv(software_list, output_file):
#     """
#     Save the software list to a CSV file.
#     """
#     try:
#         with open(output_file, mode="w", newline="", encoding="utf-8") as file:
#             writer = csv.DictWriter(file, fieldnames=["Name", "Version", "Vendor"])
#             writer.writeheader()
#             writer.writerows(software_list)
#         print(f"Software list saved to {output_file}")
#     except Exception as e:
#         print(f"Error saving to CSV: {e}")

# if __name__ == "__main__":
#     print("Collecting installed software...")

#     # Collect software
#     software_list = get_installed_software()

#     if software_list:
#         print(f"Total software found: {len(software_list)}")

#         # Save to CSV file with a timestamp
#         timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#         output_file = f"installed_software_{timestamp}.csv"

#         save_to_csv(software_list, output_file)
#     else:
#         print("No software information retrieved.")

import platform
 
my_system = platform.uname()
 
print(f"System: {my_system.system}")
print(f"Node Name: {my_system.node}")
print(f"Release: {my_system.release}")
print(f"Version: {my_system.version}")
# print(f"Machine: {my_system.machine}")
# print(f"Processor: {my_system.processor}")

import uuid
 
# joins elements of getnode() after each 2 digits.
print ("MAC address : ", end="")
print (':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
for ele in range(0,8*6,8)][::-1]))
