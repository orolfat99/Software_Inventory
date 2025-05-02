from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

# Directory to store the JSON files
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)  # Ensure the directory exists

def save_data_to_json(data):
    """
    Save the received data to a JSON file.
    """
    try:
        # Print the received data for debugging
        print("Data received by save_data_to_json:")
        print(json.dumps(data, indent=4))  # Pretty-print the data

        # Extract Node Name from the system_info section
        node_name = data.get("system_info", {}).get("Node Name", "Unknown").replace(" ", "_")

        # Generate a filename based on the Node Name and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(DATA_DIR, f"{node_name}_{timestamp}.json")

        # Save the entire data to the JSON file
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
    try:
        data = request.json  # Parse the JSON payload
        if not data:
            print("No JSON payload received or payload is empty.")
            return jsonify({"error": "No JSON payload received"}), 400

        print("Received payload:")
        print(json.dumps(data, indent=4))  # Log the received data for debugging

        # Save the received data to a JSON file
        save_data_to_json(data)

        return jsonify({"message": "Data received and saved successfully"}), 200
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

