import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DlosttreeRewardCalculator(BaseRewardCalculator):
    """Dlosttree奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        从模型输出中提取最后一个[answer]块内的边数据
        """
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
            
        last_block = answer_blocks[-1].strip()
        edges = []
        for line in last_block.split('\n'):
            line = line.strip()
            if line == '!' or not line:
                continue
            match = re.fullmatch(r'\s*(\d+)\s+(\d+)\s*', line)
            if match:
                try:
                    a, b = int(match.group(1)), int(match.group(2))
                    edges.append((a, b))
                except:
                    continue
        return edges if edges else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        验证答案边集合与原始树结构是否一致
        """
        if not solution:
            return False
        
        n = identity['n']
        if len(solution) != n - 1:
            return False

        try:
            # 将提交的答案转换为标准化边集合
            submitted = {tuple(sorted(e)) for e in solution}
            # 原始树的标准边集合
            expected = {tuple(sorted(edge)) for edge in identity['edges']}
        except:
            return False

        return submitted == expected and len(submitted) == n - 1
    
    # 其他额外方法

