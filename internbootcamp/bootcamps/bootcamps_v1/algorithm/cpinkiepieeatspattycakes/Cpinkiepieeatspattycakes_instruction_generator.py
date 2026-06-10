import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import defaultdict




class CpinkiepieeatspattycakesInstructionGenerator(BaseInstructionGenerator):
    """Cpinkiepieeatspattycakes Bootcamp指令生成器"""
    
    def __init__(self, max_maxx=5, max_ct=3, max_v=10):
        """
        初始化Cpinkiepieeatspattycakes指令生成器
        
        Args:
            max_maxx: 参数描述
            max_ct: 参数描述
            max_v: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_maxx = max_maxx    # 最大重复次数上限
        self.max_ct = max_ct        # 相同最大次数填充类型上限
        self.max_v = max_v          # 虚拟参数v的取值范围上限
    
    def case_generator(self):
        # 保证至少有两次重复
        maxx = random.randint(2, self.max_maxx)
        ct = random.randint(1, self.max_ct)
        
        # 动态调整v的合法取值范围
        min_v = max(0, ct - 1)  # 根据公式推导的最小合法v值
        max_v = max(min_v, self.max_v)  # 保证取值范围有效性
        
        # 生成合法的间隔参数v
        v = random.randint(min_v, max_v)
        
        # 根据题目公式计算总蛋糕数
        n = (maxx - 1) * (v + 1) + ct
        
        # 生成基础重复元素（保证最大重复次数）
        elements = []
        for i in range(ct):
            elements += [i + 1] * maxx  # 填充类型从1开始
        
        # 添加唯一填充元素（保证数值不超过n）
        remaining = n - len(elements)
        if remaining > 0:
            start = ct + 1
            elements += list(range(start, start + remaining))
        
        # 洗牌后输出确保测试案例多样性
        random.shuffle(elements)
        
        return {
            "n": n,
            "a": elements
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        a = question_case['a']
        return f"""
你需要解决Pinkie Pie的蛋糕排列问题。当前袋子包含{n}个蛋糕，填充类型如下：{a}。
相同数字代表相同填充。请找到一种排列顺序，使得相同填充蛋糕之间的最小间隔尽可能大。
输入格式要求：最后将最终答案放在[answer]标签内，例如[answer]3[/answer]。

问题示例：
当蛋糕为[1,1,2]时，最优排列是[1,2,1]，最小间隔为1。
实际题目可能包含多个重复类型，请仔细分析最大重复次数和重复类型数量。
        """.strip() 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

