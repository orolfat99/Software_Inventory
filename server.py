from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

# Directory to store the JSON files
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)  # Ensure the directory exists

def save_data_to_json(system_info, software_list):
    """
    Save the received data to a JSON file.
    """
    try:
        # Get the Node Name from system_info
        node_name = system_info.get("Node Name", "Unknown").replace(" ", "_")

        # Generate a filename based on the Node Name
        output_file = os.path.join(DATA_DIR, f"{node_name}.json")

        # Combine system_info and software_list into a single dictionary
        data = {
            "system_info": system_info,
            "software_list": software_list
        }

        # Write the data to the JSON file
        with open(output_file, mode="w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print(f"Data saved to {output_file}")
    except Exception as e:
        print(f"Error saving data to JSON: {e}")


@app.route('/api/asset', methods=['POST'])
def receive_asset_data():
    """
    Endpoint to receive asset data from the agent.
    """
    data = request.json
    if data:
        # Extract system info and software list
        system_info = data.get("system_info", {})
        software_list = data.get("software_list", [])

        # Save the data to a JSON file
        save_data_to_json(system_info, software_list)

        return jsonify({"message": "Data received and saved successfully"}), 200
    return jsonify({"error": "No data received"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

