import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def compute_max_comfort(n, a):
    # 预处理每个城市的最左和最右出现位置
    lmost = {}
    rmost = {}
    for i in range(n):
        city = a[i]
        if city not in lmost:
            lmost[city] = i
        rmost[city] = i
    
    dp = [0] * (n + 1)
    
    for i in range(n):
        dp[i+1] = dp[i]  # 默认不选当前段
        
        segment_cities = set()
        current_xor = 0
        min_l = n  # 当前段最小左边界
        valid = True
        
        # 从i往左扫描
        for j in range(i, -1, -1):
            city = a[j]
            
            # 检查该城市是否违反右边界约束
            if rmost.get(city, -1) > i:
                valid = False
                break
            
            # 更新当前段最小左边界
            min_l = min(min_l, lmost[city])
            
            # 仅当j到达当前段理论最小左边界时进行状态转移
            if j == min_l and valid:
                # 计算当前段的XOR
                if city not in segment_cities:
                    segment_cities.add(city)
                    current_xor ^= city
                
                # 状态转移
                dp[i+1] = max(dp[i+1], dp[j] + current_xor)
    
    return dp[n]


class CvladikandmemorabletripInstructionGenerator(BaseInstructionGenerator):
    """Cvladikandmemorabletrip Bootcamp指令生成器"""
    
    def __init__(self, min_n=4, max_n=9, max_city=6):
        """
        初始化Cvladikandmemorabletrip指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            max_city: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.max_city = max_city
    
    def case_generator(self):
        for _ in range(100):  # 防止无限循环
            n = random.randint(self.min_n, self.max_n)
            a = [random.randint(0, self.max_city) for _ in range(n)]
            
            # 确保每个城市的出现位置连续
            city_pos = {}
            for i in range(n):
                city = a[i]
                if city in city_pos:
                    last_pos = city_pos[city][-1]
                    if last_pos != i-1:
                        # 强制让相同城市连续出现
                        a[last_pos+1], a[i] = a[i], a[last_pos+1]
                city_pos.setdefault(city, []).append(i)
            
            try:
                answer = compute_max_comfort(n, a)
                return {"n": n, "a": a, "answer": answer}
            except Exception as e:
                continue
        return {"n":4, "a":[1,1,2,2], "answer":3}  # 保底案例
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = question_case['a']
        return f"""## 题目描述
{Cvladikandmemorabletripbootcamp._rule_description()}

## 当前实例
人数n: {n}
城市代码序列: {' '.join(map(str, a))}

## 要求
请给出最大总舒适度，答案置于[answer][/answer]标签内。示例：[answer]42[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _rule_description():
        return """## 规则详解
    *分段规则**：选择的各分段必须满足：若某分段包含城市x的乘客，则该城市所有乘客必须在同一分段
    *舒适度计算**：每个分段的舒适度是该段内不同城市代码的异或(XOR)值
    *目标**：选择若干不相交分段，使总舒适度最大"""
