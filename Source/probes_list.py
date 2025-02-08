probes_scripts = [
    {
        "runner_command": "python3 -m probes.author_method_contribution",
        "probe_file": "author_method_contribution",
        "output_file": "author_tracking.json"
    },
    {
        "runner_command": "python3 -m probes.authors_files_and_relations",
        "probe_file": "authors_files_and_relations",
        "output_file": "author_relation.json"
    },
    {
        "runner_command": "python3 -m probes.java_beans",
        "probe_file": "java_beans",
        "output_file": "beans.json"
    },
    {
        "runner_command": "python3 -m probes.services_dependencies",
        "probe_file": "services_dependencies",
        "output_file": "dependencies.json"
    },
    {
        "runner_command": "python3 -m probes.services_endpoints",
        "probe_file": "services_endpoints",
        "output_file": "endpoints.json"
    },
]
