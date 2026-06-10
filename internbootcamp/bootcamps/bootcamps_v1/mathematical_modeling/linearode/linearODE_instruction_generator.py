import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import json
import numpy as np
from scipy.integrate import odeint




class LinearodeInstructionGenerator(BaseInstructionGenerator):
    """Linearode Bootcamp指令生成器"""
    
    def __init__(self, k_range=(0.1, 1.0), x0_range=(0.5, 2.0), t_span=(0, 5), n_points=50, seed=None):
        """
        初始化Linearode指令生成器
        
        Args:
            k_range: 参数描述
            x0_range: 参数描述
            t_span: 参数描述
            n_points: 参数描述
            seed: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.k_range, self.x0_range = k_range, x0_range
        self.t0, self.t1 = t_span
        self.n_points = n_points
        if seed is not None:
            np.random.seed(seed)
    
    def case_generator(self):
        # 1. 随机采样参数 k 和初始值 x0
        k = float(np.random.uniform(*self.k_range))
        x0 = float(np.random.uniform(*self.x0_range))
        # 2. 构造时间序列并模拟 dx/dt = -k * x
        t = np.linspace(self.t0, self.t1, self.n_points).tolist()
        def model(x, t_val):
            return -k * x
        x = odeint(model, x0, t).flatten().tolist()
        return {"t": t, "x": x, "k": k}
    
    def prompt_func(self, identity) -> str:
        # 将 (t, x) 对格式化为提示
        points = ", ".join(f"({t:.2f}, {x:.2f})"
                           for t, x in zip(identity["t"], identity["x"]))
        return (
            f"下面给出变量 x(t) 的观测数据点：\n{points}\n\n"
            "请找出其满足的微分方程，形式为：dx/dt = f(x)。\n"
            "以dx/dt = <表达式>格式表示你的答案。"
            "并且使用[answer]标签包裹你的最终答案, 例如[answer]dx/dt = <表达式>[/answer]."
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

