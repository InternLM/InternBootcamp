import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import defaultdict
import re




class BmorningjoggingInstructionGenerator(BaseInstructionGenerator):
    """Bmorningjogging Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_m=5, **kwargs):
        """
        初始化Bmorningjogging指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.max_n = max_n
        self.max_m = max_m
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        m = random.randint(1, self.max_m)
        segments = []
        for _ in range(n):
            segment = sorted([random.randint(1, 100) for _ in range(m)], reverse=True)
            segments.append(segment)
        
        all_values = [num for seg in segments for num in seg]
        all_values.sort()
        correct_sum = sum(all_values[:m])
        
        return {
            "n": n,
            "m": m,
            "segments": segments,
            "correct_sum": correct_sum
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        segments = question_case['segments']
        
        # 预先生成分段描述字符串
        segments_desc = []
        for i, seg in enumerate(segments, 1):
            segments_desc.append(f"路段{i}：{' '.join(map(str, seg))}")
        segments_str = '\n'.join(segments_desc)

        problem = f"""你是2050年「Run! Chase the Rising Sun」活动的组织者。需要为{m}位跑步者安排路径以最小化总疲劳值：

规则说明：
1. 共有{n+1}个检查点(0~{n})，必须按顺序经过所有检查点
2. 每个相邻检查点间有{m}条路径，所有路径必须被恰好使用一次
3. 每个跑者的疲劳值是其使用路径的最小长度值

输入数据：
- 路段数：{n}
- 跑者人数：{m}
- 各路段路径长度：
{segments_str}

请输出每个路段的路径排列，每行{m}个整数（必须使用所有路径），将最终答案置于[answer]标签内。

示例格式：
[answer]
1 2 3
4 5 6
[/answer]"""

        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

