import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CanyaandsmartphoneInstructionGenerator(BaseInstructionGenerator):
    """Canyaandsmartphone Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=20, m_min=1, m_max=20, k_min=1, k_max=20):
        """
        初始化Canyaandsmartphone指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            m_min: 参数描述
            m_max: 参数描述
            k_min: 参数描述
            k_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        参数调整说明：
        - 允许k=1的边界情况
        - 支持n=1的极端情况
        - 增加n/m/k的生成范围
        """
        self.n_min = max(n_min, 1)
        self.n_max = max(n_max, self.n_min)
        self.m_min = max(m_min, 1)
        self.m_max = max(m_max, self.m_min)
        self.k_min = max(k_min, 1)
        self.k_max = max(k_max, self.k_min)
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        m = random.randint(self.m_min, self.m_max)
        k = random.randint(self.k_min, min(self.k_max, n))  # 确保k不超过n
        
        # 生成1~n的随机排列
        a = list(range(1, n+1))
        random.shuffle(a)
        
        # 生成可能包含重复的启动序列
        b = [random.choice(a) for _ in range(m)]
        
        return {
            'n': n,
            'm': m,
            'k': k,
            'a': a.copy(),  # 防止后续修改影响原始数据
            'b': b.copy()
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        prompt = f"""你是Berdroid系统的测试工程师，需要计算Anya按照指定顺序启动应用所需的总手势次数。规则如下：

1. 屏幕划分：共有{question_case['n']}个应用，每屏显示{question_case['k']}个图标，按从左到右顺序排列。例如：
   - 第1屏：1~{question_case['k']}号位置
   - 第2屏：{question_case['k']+1}~{2*question_case['k']}号位置
   - （最后一屏可能不满）

2. 启动流程：
   a) 当前显示第1屏
   b) 要启动位于t屏的应用，需要滚动(t-1)次+点击1次，共t次手势
   c) 每次启动后自动回到第1屏

3. 动态调整规则：
   - 启动应用后，该应用会与前一个位置的应用交换（若当前不在第1位）
   - 例：应用在位置5→启动后与位置4的应用交换
   - 交换可能跨屏幕发生（如位置4和5在不同屏幕仍然交换）

输入格式：
第一行：n m k
第二行：a1 a2 ... an （初始图标顺序）
第三行：b1 b2 ... bm （启动顺序）

请根据以下数据计算总手势次数，将最终答案用[answer]标签包裹：

输入：
{question_case['n']} {question_case['m']} {question_case['k']}
{' '.join(map(str, question_case['a']))}
{' '.join(map(str, question_case['b']))}

示例答案格式：[answer]42[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

