import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import deque




class CconvenientforeverybodyInstructionGenerator(BaseInstructionGenerator):
    """Cconvenientforeverybody Bootcamp指令生成器"""
    
    def __init__(self, min_n=3, max_n=10, max_people=10):
        """
        初始化Cconvenientforeverybody指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            max_people: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化参数，增加边界值校验
        """
        self.min_n = max(2, min_n)        # n最小应为2
        self.max_n = max(self.min_n, max_n)
        self.max_people = max_people
    
    def case_generator(self):
        """
        增强参数生成逻辑，确保：
        1. n >= 2
        2. s < f <= n
        3. 使用滑动窗口算法预生成合法case
        """
        n = random.randint(self.min_n, self.max_n)
        a = [random.randint(1, self.max_people) for _ in range(n)]
        
        # 动态调整s/f生成范围
        s = random.randint(1, n-1)
        f = random.randint(s+1, n)  # 严格保证s < f <=n
        
        # 使用参考代码验证生成的case合法性
        try:
            # 预验证case有效性
            dif = f - s
            if dif == 0:
                raise ValueError("Invalid s,f parameters")
        except:
            return self.case_generator()  # 重新生成case
        
        return {
            'n': n,
            'a': a,
            's': s,
            'f': f
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        a = question_case['a']
        s = question_case['s']
        f = question_case['f']
        
        problem = f"""## 时空竞赛调度优化
        
在未来的地球时钟系统中，一天被划分为{n}个时区(编号1-{n})，相邻时区整点相差1小时。第1时区当前时间为t时，则第k时区时间为(t+k-1) mod {n}（若结果为0则显示{n}）。

竞赛平台计划举办持续1小时的全球赛事，要求：
1. 所有时区必须整点开始
2. 第i时区用户当且仅当满足以下条件时才参赛：
   - 开始时刻 ≥ 本地时间{s}点整
   - 结束时刻 ≤ 本地时间{f}点整（含等于结束时刻的情况不参赛）

已知各时区参赛人数为：{a}
请计算在第一时区视角下，能获得最多参赛人数的开始时刻。如有多个解，输出最小时刻。

答案要求：
将最终整数结果置于[answer]标签内，如：[answer]3[/answer]。"""
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

