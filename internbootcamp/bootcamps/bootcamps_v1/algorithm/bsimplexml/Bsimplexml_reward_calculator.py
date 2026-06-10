import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class BsimplexmlRewardCalculator(BaseRewardCalculator):
    """Bsimplexml奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if matches:
            # 清理首尾空白和空行
            content = matches[-1].strip()
            return '\n'.join([line.rstrip() for line in content.split('\n') if line.strip()])
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            # 解析原始Bsimplexml结构
            tags = []
            stack = []
            for match in re.finditer(r'</?([a-z])>', identity['xml']):
                is_closing = match.group(0).startswith('</')
                char = match.group(1)
                tags.append((is_closing, char))
                
                # 验证标签匹配
                if not is_closing:
                    stack.append(char)
                else:
                    if not stack or stack.pop() != char:
                        return False

            # 生成标准答案
            expected = []
            indent_level = 0
            for is_closing, char in tags:
                if is_closing:
                    indent_level -= 1
                
                line = ' ' * (indent_level * 2) + f'<{"/" if is_closing else ""}{char}>'
                expected.append(line)
                
                if not is_closing:
                    indent_level += 1

            # 对比用户答案
            user_lines = solution.split('\n')
            return user_lines == expected
        except:
            return False
    
    # 其他额外方法

