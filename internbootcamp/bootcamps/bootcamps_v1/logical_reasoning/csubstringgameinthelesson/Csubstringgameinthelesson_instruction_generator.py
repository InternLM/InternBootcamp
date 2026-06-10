import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from string import ascii_lowercase
import re




class CsubstringgameinthelessonInstructionGenerator(BaseInstructionGenerator):
    """Csubstringgameinthelesson Bootcamp指令生成器"""
    
    def __init__(self, min_length=1, max_length=6):
        """
        初始化Csubstringgameinthelesson指令生成器
        
        Args:
            min_length: 参数描述
            max_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        # 修正参数校验逻辑
        self.min_length = max(1, min(min_length, max_length))  # 确保最小值合法
        self.max_length = max(self.min_length, max_length)  # 确保max >= min
    
    def case_generator(self):
        """生成全范围合法测试用例"""
        # 确保生成长度在合法范围内
        n = random.randint(self.min_length, self.max_length)
        
        # 生成字符串逻辑优化
        if random.random() < 0.25:  # 25%特殊case
            # 生成全相同字符或严格递减序列
            if random.choice([True, False]):
                c = random.choice(ascii_lowercase)
                s = c * n
            else:
                # 生成严格递减字符串如'cba'
                start = random.randint(0, 25-n+1)
                s = ''.join([ascii_lowercase[start+i] for i in range(n)][::-1])
        else:
            s = ''.join(random.choices(ascii_lowercase, k=n))
        
        # 计算结果逻辑
        correct = []
        if not s:
            return {'s': s, 'correct': []}
        
        min_char = s[0]
        correct.append("Mike")  # k=0
        
        for i in range(1, len(s)):
            current_char = s[i]
            # 严格按题目逻辑判断
            if current_char > min_char:
                correct.append("Ann")
            else:
                correct.append("Mike")
                min_char = current_char  # 更新最小值
        
        return {
            's': s,
            'correct': correct
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        s = question_case['s']
        return f"""请根据以下游戏规则，严格按指定格式输出结果：

# 游戏规则
1. 使用字符串s = "{s}"（长度{len(s)}）
2. 对每个起始位置k（0 ≤ k < {len(s)}）判断胜者
3. Ann先手，双方采取最优策略
4. 每次操作必须扩展子串范围且新子串字典序严格更小

# 输出要求
- 输出{len(s)}行，每行一个结果
- 结果只能是Mike或Ann，首字母大写
- 按k从0到{len(s)-1}的顺序输出

将最终答案放在[answer]标签内，示例：
[answer]
Mike
Ann
Ann
Mike
[/answer]

现在开始处理当前字符串：""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

