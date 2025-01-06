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