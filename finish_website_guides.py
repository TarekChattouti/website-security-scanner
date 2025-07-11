#!/usr/bin/env python3
import os
import re

# Files that still need guide fields (checking modification times from the terminal output)
remaining_files = [
    'check_18_error_messages.py',
    'check_19_debug_messages.py', 
    'check_20_html_comments.py',
    'check_21_missing_hsts.py',
    'check_22_missing_x_content_type.py',
    'check_23_missing_permissions_policy.py',
    'check_24_password_in_url.py',
    'check_25_cookie_domain_scope.py',
    'check_26_cross_domain_js.py',
    'check_27_internal_error_code.py',
    'check_28_missing_secure_cookie.py',
    'check_29_login_interface.py',
    'check_30_secure_password_submission.py',
    'check_31_sensitive_data_in_html.py',
    'check_32_unsafe_csp.py',
    'check_33_exposed_openapi.py',
    'check_34_file_upload.py',
    'check_35_sqli_test.py',
    'check_36_password_in_response.py',
    'check_37_path_disclosure.py',
    'check_38_session_token_in_url.py',
    'check_39_exposed_api_endpoints.py'
]

def add_guide_to_file(file_path, check_name):
    """Add guide imports and field to a check file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Skip if already has guide
        if "'guide':" in content or '"guide":' in content:
            print(f"✓ {check_name} already has guide")
            return
            
        # Add imports at the top
        lines = content.split('\n')
        has_json = any('import json' in line for line in lines[:5])
        has_os = any('import os' in line for line in lines[:5])
        
        insert_pos = 0
        for i, line in enumerate(lines[:5]):
            if line.startswith('import ') or line.startswith('from '):
                insert_pos = i + 1
        
        if not has_json:
            lines.insert(insert_pos, 'import json')
            insert_pos += 1
        if not has_os:
            lines.insert(insert_pos, 'import os')
            
        content = '\n'.join(lines)
        
        # Find the last return statement
        # Look for pattern: return { ... 'risk': ... }
        return_pattern = r'([ \t]+)return\s*\{([^}]*\'risk\':\s*[^,}]+[,]?)([^}]*)\}'
        match = re.search(return_pattern, content, re.DOTALL)
        
        if match:
            indent = match.group(1)
            before_risk = match.group(2)
            after_risk = match.group(3)
            
            # Add guide loading code before return
            guide_code = f'''{indent}
{indent}# Load guide from help.json
{indent}help_file = os.path.join(os.path.dirname(__file__), 'help.json')
{indent}guide = ""
{indent}try:
{indent}    with open(help_file, 'r') as f:
{indent}        help_data = json.load(f)
{indent}        guide = help_data.get('{check_name}', '')
{indent}except:
{indent}    pass
{indent}'''
            
            # Build new return statement with guide field
            new_return = f"{indent}return {{{before_risk}{after_risk.rstrip()},\n{indent}    'guide': guide\n{indent}}}"
            
            # Replace the return statement
            new_content = content[:match.start()] + guide_code + new_return + content[match.end():]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            print(f"✓ Added guide to {check_name}")
        else:
            print(f"✗ Could not find return statement in {check_name}")
            
    except Exception as e:
        print(f"✗ Error processing {check_name}: {e}")

# Process remaining website scanner files
base_dir = r'c:\Programming\vuln\website_scanner'
print("Processing remaining website scanner files...")
for filename in remaining_files:
    file_path = os.path.join(base_dir, filename)
    check_name = filename[:-3]  # Remove .py
    if os.path.exists(file_path):
        add_guide_to_file(file_path, check_name)
    else:
        print(f"✗ File not found: {filename}")

print("\n✓ Finished processing remaining website scanner files!")
