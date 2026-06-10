import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import json
import numpy as np




class Earthdew2humidityInstructionGenerator(BaseInstructionGenerator):
    """Earthdew2humidity Bootcamp指令生成器"""
    
    def __init__(self, temperature_range=(-20, 40), temperature_dewpoint_range=(0, 10), seed=None):
        """
        初始化Earthdew2humidity指令生成器
        
        Args:
            temperature_range: 参数描述
            temperature_dewpoint_range: 参数描述
            seed: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.temperature_range, self.temperature_dewpoint_range = temperature_range, temperature_dewpoint_range
        if seed is not None:
            np.random.seed(seed)
    
    def case_generator(self):
        # 1. 随机采样参数 dewpoint 和 temperature
        temperature_original = float(np.random.uniform(*self.temperature_range))
        dewpoint_original = temperature_original - float(np.random.uniform(*self.temperature_dewpoint_range))
        # 2. 计算湿度
        dewpoint = dewpoint_original + 273.15
        temperature = temperature_original + 273.15
        e = 611.2 * np.exp(17.67 * (dewpoint - 273.15) / (dewpoint - 29.65))
        e_s = 611.2 * np.exp(17.67 * (temperature - 273.15) / (temperature - 29.65))
        rh = e / e_s * 100
        return {"dewpoint": dewpoint_original, "temperature": temperature_original, "humidity": float(rh)}
    
    def prompt_func(self, identity) -> str:
        dewpoint = identity["dewpoint"]
        temperature = identity["temperature"]
        return (
            f"下面给出露点温度（dewpoint）={dewpoint} (摄氏度)\n温度（temperature）={temperature} (摄氏度)\n"
            "请计算湿度，计算公式为：\n"
            "dewpoint = dewpoint + 273.15，temperature = temperature + 273.15\n"
            "e = 611.2 * np.exp(17.67 * (dewpoint - 273.15) / (dewpoint - 29.65))\n"
            "e_s = 611.2 * np.exp(17.67 * (temperature - 273.15) / (temperature - 29.65))\n"
            "relative humidity = e / e_s * 100\n"
            "以\\boxed{relative humidity = ？%} 格式输出你的最终答案，例如\\boxed{relative humidity = your answer%}。"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

