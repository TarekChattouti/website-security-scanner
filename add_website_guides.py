#!/usr/bin/env python3
import os
import re

# Template for adding guide functionality
guide_template = '''
    # Load guide from help.json
    help_file = os.path.join(os.path.dirname(__file__), 'help.json')
    guide = ""
    try:
        with open(help_file, 'r') as f:
            help_data = json.load(f)
            guide = help_data.get('{check_name}', '')
    except:
        pass'''

def add_guide_to_file(file_path, check_name):
    """Add guide field to a single check file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already has guide
        if "'guide':" in content or '"guide":' in content:
            print(f"✓ {check_name} already has guide")
            return
            
        # Add imports if not present
        lines = content.split('\n')
        has_json_import = any('import json' in line for line in lines[:10])
        has_os_import = any('import os' in line for line in lines[:10])
        
        if not has_json_import:
            lines.insert(0, 'import json')
        if not has_os_import:
            lines.insert(0 if not has_json_import else 1, 'import os')
            
        content = '\n'.join(lines)
        
        # Find the return statement
        return_match = re.search(r"(\s+)return\s*\{([^}]*'risk':\s*[^,}]+)", content, re.DOTALL)
        if not return_match:
            print(f"✗ Could not find return statement in {check_name}")
            return
            
        indent = return_match.group(1)
        before_return = content[:return_match.start()]
        return_content = return_match.group(0)
        after_return = content[return_match.end():]
        
        # Add guide loading code before return
        guide_code = guide_template.format(check_name=check_name).replace('\n    ', f'\n{indent}')
        
        # Add guide field to return statement
        if return_content.endswith(','):
            return_content = return_content[:-1] + f",\n{indent}    'guide': guide"
        else:
            return_content = return_content + f",\n{indent}    'guide': guide"
            
        # Find the closing brace and add comma if needed
        closing_match = re.search(r'(\s*\})', after_return)
        if closing_match:
            after_return = after_return[:closing_match.start()] + f"\n{indent}" + closing_match.group(1) + after_return[closing_match.end():]
        
        new_content = before_return + guide_code + '\n' + return_content + after_return
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print(f"✓ Added guide to {check_name}")
        
    except Exception as e:
        print(f"✗ Error processing {check_name}: {e}")

# List of remaining website scanner files to process
website_files = [
    'check_08_cve_server_software.py',
    'check_09_client_access_policy.py', 
    'check_10_robots_txt.py',
    'check_11_security_txt.py',
    'check_12_ssl_cert.py',
    'check_13_trace_debug.py',
    'check_14_options_method.py',
    'check_15_https_redirect.py',
    'check_16_directory_listing.py',
    'check_17_unencrypted_password_form.py',
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

# Process website scanner files
base_dir = r'c:\Programming\vuln\website_scanner'
print("Processing website scanner files...")
for filename in website_files:
    file_path = os.path.join(base_dir, filename)
    check_name = filename[:-3]  # Remove .py
    if os.path.exists(file_path):
        add_guide_to_file(file_path, check_name)
    else:
        print(f"✗ File not found: {filename}")

print("\nDone processing website scanner files!")
