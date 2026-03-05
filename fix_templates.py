#!/usr/bin/env python3
"""
Replaces all {{ success_msg }} and {{ error }} in feedback alert blocks
with translated keys pattern: {{ _(success_key) }} / {{ _(error_key) }}
"""
import os
import re

TEMPLATES = [
    'app/templates/register.html',
    'app/templates/change_password.html',
    'app/templates/delete_user.html',
    'app/templates/login.html',
]

SUCCESS_OLD = '<span class="font-bold">{{ success_msg }}</span>'
SUCCESS_NEW = '<span class="font-bold">{% if success_key %}{% set _tpl = _(success_key) %}{% if success_args %}{{ _tpl.format(**success_args) }}{% else %}{{ _tpl }}{% endif %}{% elif success_msg %}{{ success_msg }}{% endif %}</span>'

ERROR_OLD_EXACT = '<span class="font-bold">{{ error }}</span>'
ERROR_NEW = '<span class="font-bold">{% if error_key %}{{ _(error_key) }}{% if error_detail %}: {{ error_detail }}{% endif %}{% elif error %}{{ error }}{% endif %}</span>'

# login.html also has an error in the base, but the base handles {{ error }} already
# We also need to handle the error block in login.html template
# Actually base.html has {% if error %} {{ error }} - we need to support error_key there too

for path in TEMPLATES:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    content = content.replace(SUCCESS_OLD, SUCCESS_NEW)
    content = content.replace(ERROR_OLD_EXACT, ERROR_NEW)
    
    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {path}")
    else:
        print(f"No change needed: {path}")

print("Done!")
