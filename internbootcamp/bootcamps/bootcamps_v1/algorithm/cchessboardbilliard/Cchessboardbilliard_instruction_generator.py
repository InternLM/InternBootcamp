import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CchessboardbilliardInstructionGenerator(BaseInstructionGenerator):
    """Cchessboardbilliard Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cchessboardbilliard指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        # 参数校验与默认设置（防止非法参数）
        self.n_min = max(params.get('n_min', 2), 2)
        self.n_max = min(params.get('n_max', 100), 10**6)
        self.m_min = max(params.get('m_min', 2), 2)
        self.m_max = min(params.get('m_max', 100), 10**6)
        # 确保生成参数的有效性
        if self.n_min > self.n_max or self.m_min > self.m_max:
            raise ValueError("Invalid parameter range")
    
    def case_generator(self):
        """生成符合规范的有效棋盘尺寸"""
        while True:
            a = random.randint(self.n_min, self.n_max)
            b = random.randint(self.m_min, self.m_max)
            # 不进行预交换，保持原始生成顺序
            if 2 <= a <= 10**6 and 2 <= b <= 10**6:
                return {'n': a, 'm': b}
    
    @staticmethod
    def prompt_func(question_case):
        n, m = question_case['n'], question_case['m']
        return f"""## 台球布局问题

你正在设计一个棋盘游戏。棋盘尺寸为 {n} 行 × {m} 列。需要放置尽可能多的台球，满足：

**移动规则**：
- 台球按国际象棋象的斜对角方式移动
- 碰到边缘时以90度反射，角落会反射两次（路径反转）
- 移动轨迹无限延伸，可在任意位置停止

**兼容条件**：
- 两个台球如果存在可达路径即为不兼容
- 需要找到最大兼容台球数

**输入格式**  
两个整数 n m (2 ≤ n, m ≤ 1e6)

**输出格式**  
单一整数答案，用[answer]标签包裹，例如：[answer]5[/answer]

**当前测试案例**  
n = {n}, m = {m}

请计算正确结果：""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

