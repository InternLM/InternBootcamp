import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class ColdberlandlanguageInstructionGenerator(BaseInstructionGenerator):
    """Coldberlandlanguage Bootcamp指令生成器"""
    
    def __init__(self, max_n=1000, max_length=1000):
        """
        初始化Coldberlandlanguage指令生成器
        
        Args:
            max_n: 参数描述
            max_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max(max_n, 1)
        self.max_length = max(max_length, 1)
    
    def case_generator(self):
        # 尝试生成有效案例的多种组合
        for _ in range(5):  # 有限次尝试避免死循环
            n = random.randint(1, min(20, self.max_n))  # 控制生成规模
            lengths = [random.randint(1, min(20, self.max_length)) for _ in range(n)]
            
            # 按照参考算法进行验证
            try:
                sorted_indices = sorted(enumerate(lengths), key=lambda x: x[1])
                pref = 2
                ans = [None] * n
                valid_case = True
                
                for idx, (original_idx, length) in enumerate(sorted_indices):
                    current_len = len(bin(pref)) - 3  # 当前前缀长度
                    shift_needed = length - current_len
                    
                    if shift_needed < 0:
                        valid_case = False
                        break
                    
                    pref <<= shift_needed
                    word = bin(pref)[3:]  # 去除'0b1'
                    
                    if len(word) != length or (None in ans and '0' not in word):
                        valid_case = False
                        break
                    
                    ans[original_idx] = word
                    pref += 1
                
                if valid_case and None not in ans:
                    # 最终验证前缀条件
                    prefix_valid = True
                    for i in range(n):
                        for j in range(n):
                            if i != j and (ans[i].startswith(ans[j]) or ans[j].startswith(ans[i])):
                                prefix_valid = False
                                break
                        if not prefix_valid:
                            break
                    if prefix_valid:
                        return {
                            'n': n,
                            'lengths': lengths,
                            'possible': True
                        }
            except:
                continue
        
        # 生成无效案例（如多个长度1或随机冲突）
        return {
            'n': random.randint(2, 10),
            'lengths': [1] * random.randint(2, 10),
            'possible': False
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        lengths = question_case['lengths']
        lengths_str = ' '.join(map(str, lengths))
        return (
            f"Determine if {n} binary words with lengths {lengths_str} can exist such that no word is a prefix of another. "
            f"If possible, output YES followed by the words in input order. Otherwise, output NO. "
            f"Format your answer within [answer]...[/answer] tags.\n\n"
            f"Example format:\n[answer]YES\n0\n10\n110[/answer] or [answer]NO[/answer]"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

