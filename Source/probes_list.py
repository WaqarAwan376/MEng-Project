from utils.constants import OUTPUT_FOLDER

probes_scripts = [
    {
        "runner_command": "python3 -m probes.author_method_contribution",
        "probe_file": "author_method_contribution",
        "arguments": [
            "--PROBE_NAME", "Method_Contributor",
            "--OUTPUT", f"{OUTPUT_FOLDER}{'author_tracking.json'}"
        ]
    },
    {
        "runner_command": "python3 -m probes.authors_files_and_relations",
        "probe_file": "authors_files_and_relations",
        "arguments": [
            "--PROBE_NAME_1", "Authors_Relation",
            "--OUTPUT_FILE_1", f"{OUTPUT_FOLDER}{'author_relation.json'}",
            "--PROBE_NAME_2", "File_Contributors",
            "--OUTPUT_FILE_2", f"{OUTPUT_FOLDER}{'file_contributors.json'}",
        ]
    },
    {
        "runner_command": "python3 -m probes.java_beans",
        "probe_file": "java_beans",
        "arguments": [
            "--PROBE_NAME", "Beans",
            "--OUTPUT", f"{OUTPUT_FOLDER}{'beans.json'}"
        ]
    },
    {
        "runner_command": "python3 -m probes.services_dependencies",
        "probe_file": "services_dependencies",
        "arguments": [
            "--PROBE_NAME", "Dependencies",
            "--OUTPUT", f"{OUTPUT_FOLDER}{'dependencies.json'}"
        ]
    },
    {
        "runner_command": "python3 -m probes.services_endpoints",
        "probe_file": "services_endpoints",
        "arguments": [
            "--PROBE_NAME", "Endpoints",
            "--OUTPUT", f"{OUTPUT_FOLDER}{'endpoints.json'}"
        ]
    },
]
