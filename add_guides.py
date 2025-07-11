#!/usr/bin/env python3
import os
import re

# Define the scanners and their directories
scanners = {
    'website_scanner': 'c:\\Programming\\vuln\\website_scanner',
    'wordpress': 'c:\\Programming\\vuln\\wordpress', 
    'network_scanner': 'c:\\Programming\\vuln\\network_scanner',
    'ssl_scanner': 'c:\\Programming\\vuln\\ssl_scanner',
    'subdomain_finder': 'c:\\Programming\\vuln\\subdomain_finder'
}

def add_guide_to_check(file_path, check_name, scanner_name):
    """Add guide field to a check module"""
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if guide is already added
        if "'guide':" in content or '"guide":' in content:
            print(f"Guide already exists in {file_path}")
            return
            
        # Add imports if not present
        if 'import json' not in content:
            content = 'import json\n' + content
        if 'import os' not in content:
            content = 'import os\n' + content
            
        # Find the return statement pattern
        return_pattern = r'(    return\s*\{[^}]*\'risk\':\s*[^,}]+)([\s,]*\})'
        
        # Create the guide loading code
        guide_code = f'''
    
    # Load guide from help.json
    help_file = os.path.join(os.path.dirname(__file__), 'help.json')
    guide = ""
    try:
        with open(help_file, 'r') as f:
            help_data = json.load(f)
            guide = help_data.get('{check_name}', '')
    except:
        pass'''
        
        # Find the return statement and add guide field
        def replace_return(match):
            before_closing = match.group(1)
            closing = match.group(2)
            return before_closing + ",\n        'guide': guide" + closing
            
        # Insert guide loading code before return statement
        content = re.sub(r'(    return\s*\{)', guide_code + r'\n\1', content)
        
        # Add guide field to return statement
        content = re.sub(return_pattern, replace_return, content)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Added guide to {file_path}")
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def process_scanner(scanner_name, scanner_dir):
    """Process all check files in a scanner directory"""
    print(f"\nProcessing {scanner_name}...")
    
    for filename in os.listdir(scanner_dir):
        if filename.startswith('check_') and filename.endswith('.py'):
            file_path = os.path.join(scanner_dir, filename)
            check_name = filename[:-3]  # Remove .py extension
            add_guide_to_check(file_path, check_name, scanner_name)

# Process all scanners
for scanner_name, scanner_dir in scanners.items():
    if os.path.exists(scanner_dir):
        process_scanner(scanner_name, scanner_dir)
    else:
        print(f"Directory not found: {scanner_dir}")

print("\nDone!")
