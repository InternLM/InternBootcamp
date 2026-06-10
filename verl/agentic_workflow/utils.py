import re
from typing import Optional

def parse_python_code(text_with_code_block: str) -> Optional[str]:
    pattern = re.compile(r"```python\s*\n(.*?)\n\s*```", re.DOTALL)
    
    match = pattern.search(text_with_code_block)
    
    if match:
        return match.group(1).strip()
    
    return None

def parse_yaml_code(text_with_code_block: str) -> Optional[str]:
    pattern = re.compile(r"```yaml\s*\n(.*?)\n\s*```", re.DOTALL)
    
    match = pattern.search(text_with_code_block)
    
    if match:
        return match.group(1).strip()
    
    return None