import subprocess
import os
from dotenv import load_dotenv
from probes_list import probes_scripts
from utils.constants import OUTPUT_FOLDER
from utils.helper import get_passed_arguments
import json
import requests

load_dotenv()
SST_API_URL = os.getenv("SST_API_URL")
project_root = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    args = get_passed_arguments("--SOURCE_DIR", "--DIR_NAME")
    original_directory = os.getcwd()
    probes_directory = "./probes/"

    for script in probes_scripts:
        command_str = f"{script['runner_command']} --INPUT_DIR \"{args.SOURCE_DIR}\" --DIR_NAME {args.DIR_NAME} "
        for i in range(0, len(script['arguments']), 2):
            command_str += f"{script['arguments'][i]} {script['arguments'][i+1]} "
        subprocess.run(command_str, shell=True, cwd=project_root)

    for filename in os.listdir(OUTPUT_FOLDER):
        if filename.endswith(".json"):
            file_path = os.path.join(OUTPUT_FOLDER, filename)

            try:
                with open(file_path, "r", encoding="utf-8") as json_file:
                    json_data = json.load(json_file)

                headers = {"Content-Type": "application/json"}
                response = requests.post(
                    f"{SST_API_URL}/api/upload-graph", json=json_data, headers=headers)

                print(f"Sent {filename}: {response.status_code}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")
