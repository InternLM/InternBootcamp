import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
import bisect

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def compute_answer(n, words):
    if n == 0:
        return 0
    preprocessed = []
    for s in words:
        m = len(s)
        deletions = [s[:i] + s[i+1:] for i in range(m)]
        deletions.sort()
        preprocessed.append(deletions)
    
    prev_deletions = preprocessed[0]
    prev_prefix_sum = [0] * (len(prev_deletions) + 1)
    for i in range(len(prev_deletions)):
        prev_prefix_sum[i+1] = (prev_prefix_sum[i] + 1) % MOD
    
    for x in range(1, n):
        current_deletions = preprocessed[x]
        current_dp = []
        for s in current_deletions:
            j = bisect.bisect_right(prev_deletions, s)
            current_count = prev_prefix_sum[j]
            current_dp.append(current_count % MOD)
        
        current_prefix_sum = [0]
        current_sum = 0
        for cnt in current_dp:
            current_sum = (current_sum + cnt) % MOD
            current_prefix_sum.append(current_sum)
        
        prev_deletions = current_deletions
        prev_prefix_sum = current_prefix_sum
    
    return prev_prefix_sum[-1] % MOD


class E1twilightandancientscrolleasierversionInstructionGenerator(BaseInstructionGenerator):
    """E1twilightandancientscrolleasierversion Bootcamp指令生成器"""
    
    def __init__(self, max_n=1000, max_total_length=20000):
        """
        初始化E1twilightandancientscrolleasierversion指令生成器
        
        Args:
            max_n: 参数描述
            max_total_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_total_length = max_total_length
    
    def case_generator(self):
        # 生成保证有效的测试用例
        n = random.randint(1, 3)
        words = []
        total_length = 0
        
        # 生成原始非递减序列
        original = []
        prev_word = ''
        for _ in range(n):
            # 生成保证≥前一个词的词
            if not original:
                min_length = 0
            else:
                min_length = len(prev_word)
            
            # 生成新词长度（原词长度+1）
            new_length = random.randint(min_length, min_length + 1)
            new_word = []
            for i in range(new_length):
                # 保证词序递增
                min_char = ord('a') if not new_word else ord(new_word[-1])
                new_char = chr(random.randint(min_char, ord('z')))
                new_word.append(new_char)
            
            new_word = ''.join(new_word)
            original.append(new_word)
            prev_word = new_word
        
        # 生成带干扰字符的测试用例
        scroll_words = []
        for orig in original:
            # 原始单词插入一个随机字符
            insert_pos = random.randint(0, len(orig))
            insert_char = chr(random.randint(ord('a'), ord('z')))
            new_word = orig[:insert_pos] + insert_char + orig[insert_pos:]
            scroll_words.append(new_word)
            total_length += len(new_word)
            if total_length > self.max_total_length:
                # 动态调整n值
                n = len(scroll_words)
                break
        
        # 计算正确答案
        try:
            expected = compute_answer(n, scroll_words)
        except Exception as e:
            print(f"Error computing answer: {e}")
            expected = 0
        
        return {
            'n': n,
            'words': scroll_words,
            'expected_answer': expected
        }
    
    @staticmethod
    def prompt_func(question_case):
        case = question_case
        input_str = f"{case['n']}\n" + "\n".join(case['words'])
        return f"""根据以下规则解决古代卷轴问题：
1. 每个单词需要删除正好一个字符
2. 最终序列必须是非递减字典序
3. 输出所有可能方案数模1000000007

输入：
{input_str}

请将最终答案放在[answer]标签内，如：[answer]42[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

