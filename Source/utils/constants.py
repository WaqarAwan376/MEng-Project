method_patterns = {
    "GET": [
        r'@GetMapping\s*\(\s*(?:value\s*=\s*)?"([^"]*)"\s*\)',
        r'@GetMapping\s*\(\s*path\s*=\s*\{"([^"]*)"\s*\}\)',
        r"@GetMapping\s*\(\s*\)",
        r"@GetMapping(?!\()",
    ],
    "POST": [
        r'@PostMapping\s*\(\s*(?:value\s*=\s*)?"([^"]*)"\s*\)',
        r'@PostMapping\s*\(\s*path\s*=\s*\{"([^"]*)"\s*\}\)',
        r"@PostMapping\s*\(\s*\)",
        r"@PostMapping(?!\()",
    ],
    "PUT": [
        r'@PutMapping\s*\(\s*(?:value\s*=\s*)?"([^"]*)"\s*\)',
        r'@PutMapping\s*\(\s*path\s*=\s*\{"([^"]*)"\s*\}\)',
        r"@PutMapping\s*\(\s*\)",
        r"@PutMapping(?!\()",
    ],
    "DELETE": [
        r'@DeleteMapping\s*\(\s*(?:value\s*=\s*)?"([^"]*)"\s*\)',
        r'@DeleteMapping\s*\(\s*path\s*=\s*\{"([^"]*)"\s*\}\)',
        r"@DeleteMapping\s*\(\s*\)",
        r"@DeleteMapping(?!\()",
    ],
}


# Class-level @RequestMapping pattern
class_pattern = r'@RequestMapping\s*\(\s*(?:value\s*=\s*)?"([^"]+)"\s*\)'


# Define directories and files to ignore
IGNORE_DIRS = {
    'target',
    'build',
    '.m2',
    '.gradle',
    '.idea',
    '.settings',
    '.git',
    'node_modules',
    '__pycache__',
    'static',
    '.mvn'
}
IGNORE_FILES = {
    '.classpath',
    '.project',
    '.iml',
    '.DS_Store',
    'Thumbs.db',
    '.png',
    '.jpg',
    '.jar'
}

# List of common Spring bean annotations
BEAN_ANNOTATIONS = [
    "@Component", "@Service", "@Repository", "@Controller", "@Bean", "@Configuration"
]

# Pattern to match class declarations (class or interface)
CLASS_PATTERN = r"^\s*(?:public|private|protected)?\s*(class|interface)\s+(\w+)"

# Pattern to match method declarations
METHOD_PATTERN = r"\s*(?:[\w<>,\.\s]+)\s+(\w+)\s*\(.*?\)\s*\{"
