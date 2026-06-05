import os
import re

backend_dir = os.path.dirname(os.path.abspath(__file__))

for root, dirs, files in os.walk(backend_dir):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace 'from ..xyz' with 'from xyz'
            new_content = re.sub(r'from \.\.(database|models|routers|auth|schemas|services|huggingface|core)', r'from \1', content)
            
            # Replace 'from .xyz' with 'from xyz'
            new_content = re.sub(r'from \.(database|models|routers|auth|schemas|services|huggingface|core)', r'from \1', new_content)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {filepath}")
