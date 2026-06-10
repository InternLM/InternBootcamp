import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CtillicollapseInstructionGenerator(BaseInstructionGenerator):
    """Ctillicollapse Bootcamp指令生成器"""
    
    def __init__(self, max_n=20):
        """
        初始化Ctillicollapse指令生成器
        
        Args:
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n  # 控制生成谜题的最大规模
    
    def case_generator(self):
        """生成具有多样性的测试用例"""
        n = random.randint(1, self.max_n)
        
        # 生成颜色数组（确保至少2种颜色）
        colors = list(range(1, min(n, 5)+1))  # 颜色值限制在1-5范围以增加重复概率
        a = [random.choice(colors) for _ in range(n)]
        
        # 对部分元素做随机扰动
        for _ in range(int(n**0.5)):
            a[random.randint(0, n-1)] = random.choice(colors)
            
        ans = [self._calculate_min_squads(a, k) for k in range(1, n+1)]
        return {'n': n, 'a': a, 'ans': ans}
    
    @staticmethod
    def prompt_func(question_case):
        """增强格式说明的prompt模板"""
        n = question_case['n']
        a = ' '.join(map(str, question_case['a']))
        return (
            "## Mission\nRick和Morty需要将Mr. Ctillicollapse分成连续的squad（每个squad最多k种颜色）\n\n"
            "## Input Format\n"
            "- 第1行：整数n (人数)\n"
            "- 第2行：空格分隔的颜色序列\n\n"
            "## Output Format\n"
            "- 1行：n个空格分隔的整数，第i个数表示k=i时的最小squad数\n\n"
            "## Example\n"
            "Input:\n5\n1 3 4 3 3\n"
            "Output:\n4 2 1 1 1 → 应格式化为：[answer]4 2 1 1 1[/answer]\n\n"
            "## Current Problem\n"
            f"{n}\n{a}\n\n"
            "Answer with [answer]...[/answer]"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _calculate_min_squads(a, k):
        """优化后的贪心算法实现"""
        n = len(a)
        count = 0
        start = 0

        while start < n:
            color_dict = {}
            distinct = 0
            max_end = start

            # 滑动窗口寻找最大有效区间
            for end in range(start, n):
                color = a[end]
                if color not in color_dict or color_dict[color] == 0:
                    distinct += 1
                color_dict[color] = color_dict.get(color, 0) + 1

                if distinct > k:
                    # 回退最后一步
                    color_dict[color] -= 1
                    if color_dict[color] == 0:
                        distinct -= 1
                    break

                max_end = end

            count += 1
            start = max_end + 1

        return count
