import subprocess
import os
from probes_list import probes_scripts
from utils.constants import OUTPUT_FOLDER
from utils.helper import get_passed_arguments

project_root = os.path.dirname(os.path.abspath(__file__))
if __name__ == '__main__':

    args = get_passed_arguments("--SOURCE_DIR")
    original_directory = os.getcwd()
    probes_directory = "./probes/"

    for script in probes_scripts:
        subprocess.run(
            f"{script['runner_command']} --INPUT_DIR \"{args.SOURCE_DIR}\" --OUTPUT \
                {OUTPUT_FOLDER}{script['output_file']}", shell=True, cwd=project_root)
