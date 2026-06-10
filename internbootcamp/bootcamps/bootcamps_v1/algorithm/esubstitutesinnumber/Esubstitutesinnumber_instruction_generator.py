import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class EsubstitutesinnumberInstructionGenerator(BaseInstructionGenerator):
    """Esubstitutesinnumber Bootcamp指令生成器"""
    
    def __init__(self, s_min_length=1, s_max_length=100, max_queries=10, max_total_ti_length=1000):
        """
        初始化Esubstitutesinnumber指令生成器
        
        Args:
            s_min_length: 参数描述
            s_max_length: 参数描述
            max_queries: 参数描述
            max_total_ti_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.s_min_length = s_min_length
        self.s_max_length = s_max_length
        self.max_queries = max_queries
        self.max_total_ti_length = max_total_ti_length
    
    def case_generator(self):
        # 确保生成有效初始字符串（长度>=1）
        s_length = random.randint(max(1, self.s_min_length), self.s_max_length)
        s = ''.join(random.choices('0123456789', k=s_length))
        
        # 动态调整最大查询数避免溢出
        effective_max_queries = min(self.max_queries, 10**5)
        n = random.randint(0, effective_max_queries)
        
        queries = []
        total_ti_length = 0
        
        # 生成合法query序列
        available_digits = list('0123456789')
        for _ in range(n):
            if total_ti_length >= self.max_total_ti_length:
                ti = ''
            else:
                remaining = self.max_total_ti_length - total_ti_length
                ti_length = random.randint(0, min(remaining, 10**5))  # 遵守题目约束
                ti = ''.join(random.choices(available_digits, k=ti_length)) if ti_length > 0 else ''
            
            di = random.choice(available_digits)
            queries.append((di, ti))
            total_ti_length += len(ti)
        
        return {
            's': s,
            'queries': queries
        }
    
    @staticmethod
    def prompt_func(question_case):
        s = question_case['s']
        queries = question_case['queries']
        n = len(queries)
        
        # 格式化query显示
        query_display = []
        for di, ti in queries:
            replacement = "空字符串" if ti == '' else ti
            query_display.append(f"{di} -> {replacement}")
        
        prompt = f"""## 数字替换游戏

### 游戏规则
1. 初始字符串：{s}
2. 需要按顺序执行以下替换操作（共{n}个）：
{chr(10).join(query_display) if query_display else "无替换操作"}
3. 最终结果计算要求：
   - 保留所有前导零（例如替换后得到0023仍视为0023）
   - 空字符串视为0
   - 计算结果对1,000,000,007取模

### 输出格式
请将最终结果放在[answer]标签内，例如：[answer]31415926[/answer]

请逐步思考并给出最终答案。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def compute_answer(cls, s, queries):
        # 加强边界条件处理
        if not s and not queries:
            return 0 % MOD

        value = {str(d): d % MOD for d in range(10)}
        pow10 = {str(d): 10 % MOD for d in range(10)}

        # 初始化特殊键位
        value[''] = 0
        pow10[''] = 1

        # 构建完整操作序列（包含初始字符串）
        operation_stack = [('', s)] + queries

        # 逆向处理操作序列
        for i in reversed(range(len(operation_stack))):
            current_d, replacement = operation_stack[i]

            current_value = 0
            current_pow = 1

            for char in replacement:
                current_value = (current_value * pow10.get(char, 1) + value.get(char, 0)) % MOD
                current_pow = (current_pow * pow10.get(char, 1)) % MOD

            # 更新当前操作的映射关系
            value[current_d] = current_value
            pow10[current_d] = current_pow

        return value.get('', 0) % MOD
