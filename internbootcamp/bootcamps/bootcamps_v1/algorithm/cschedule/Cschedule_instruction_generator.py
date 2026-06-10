import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CscheduleInstructionGenerator(BaseInstructionGenerator):
    """Cschedule Bootcamp指令生成器"""
    
    def __init__(self, min_groups=1, max_groups=10, time_max=10**6):
        """
        初始化Cschedule指令生成器
        
        Args:
            min_groups: 参数描述
            max_groups: 参数描述
            time_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_groups = max(1, min_groups)
        self.max_groups = max(self.min_groups, max_groups)
        self.time_max = time_max
    
    def case_generator(self):
        case_type = random.choices([0, 1, 2, 3], weights=[1, 1, 1, 3], k=1)[0]
        n = random.randint(self.min_groups, self.max_groups)
        intervals = []

        if case_type == 0:  # 全不重叠
            current_end = 0
            max_possible = (self.time_max - 1) // 2
            n = min(n, max_possible) if max_possible > 0 else 1
            intervals = []
            for _ in range(n):
                start = current_end + 1
                if start >= self.time_max:
                    break
                end = random.randint(start + 1, min(self.time_max, start + (self.time_max - start) // (n - _)))
                intervals.append({'l': start, 'r': end})
                current_end = end
            n = len(intervals)
        
        elif case_type == 1:  # 必须删除特定组
            n = max(n, 2)
            base_count = n - 1
            intervals = []
            current_end = 0
            for _ in range(base_count):
                start = current_end + 1
                end = start + 1
                intervals.append({'l': start, 'r': end})
                current_end = end
            conflict_group = {'l': intervals[0]['l'], 'r': current_end + 1}
            intervals.append(conflict_group)
        
        elif case_type == 2:  # 全重叠无解
            common_mid = random.randint(1, self.time_max - 1)
            radius = random.randint(1, min(common_mid, self.time_max - common_mid))
            for _ in range(n):
                l = random.randint(common_mid - radius, common_mid)
                r = random.randint(common_mid + 1, common_mid + radius)
                intervals.append({'l': l, 'r': r})
        
        else:  # 随机案例
            intervals = []
            for _ in range(n):
                li = random.randint(1, self.time_max - 1)
                ri = random.randint(li + 1, self.time_max)
                intervals.append({'l': li, 'r': ri})

        return {'n': len(intervals), 'intervals': intervals}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_str = "\n".join([f"{x['l']} {x['r']}" for x in question_case['intervals']])
        return f"""请解决课程冲突问题。输入：
{question_case['n']}
{input_str}

输出两行：解的数量k和升序排列的索引（用空格分隔），如：
[answer]
3
1 2 3
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

