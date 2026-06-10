import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class KorciphercustominverseshiftsubstitutioncipherInstructionGenerator(BaseInstructionGenerator):
    """Korciphercustominverseshiftsubstitutioncipher Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Korciphercustominverseshiftsubstitutioncipher指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.standard_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.reversed_alphabet = "ZYXWVUTSRQPONMLKJIHGFEDCBA"
        self.substitution_alphabet = "RFDJUHABCEGIKLMNOPQSTVWXYZ"
    
    def case_generator(self):
        """生成合法问题实例，保证可验证性"""
        # 生成随机长度3-8的明文
        plaintext = ''.join(random.choices(self.standard_alphabet, k=random.randint(3, 8)))
        ciphertext = ''.join([self._encrypt_single(c) for c in plaintext])
        # 随机生成加密或解密问题
        if random.random() < 0.5:
            return {
                'type': 'encrypt',
                'question': plaintext,
                'answer': ciphertext
            }
        else:
            return {
                'type': 'decrypt',
                'question': ciphertext,
                'answer': plaintext
            }
    
    @staticmethod
    def prompt_func(question_case):
        """动态生成问题描述"""
        if question_case['type'] == 'encrypt':
            return (
                "请加密以下明文，加密规则：\n"
                "1. 反向字母表替换（A→Z，B→Y）\n"
                "2. 前移4位（Z→D）\n"
                "3. 最终替换表：RFDJUHABCEGIKLMNOPQSTVWXYZ\n\n"
                f"明文：{question_case['question']}\n"
                "答案格式：[[大写字母串]] 例如：[[ABC]]"
            )
        else:
            return (
                "请解密密文，解密规则：\n"
                "1. 查找替换表位置\n"
                "2. 后移4位还原\n"
                "3. 逆向反向映射\n\n"
                f"密文：{question_case['question']}\n"
                "答案格式：[[大写字母串]] 例如：[[XYZ]]"
            ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _encrypt_single(self, char):
        """实现加密三步骤的原子操作"""
        # 步骤1：反向映射
        reversed_char = self.reversed_alphabet[self.standard_alphabet.index(char)]
        # 步骤2：前移4位（考虑循环）
        shifted_index = (self.standard_alphabet.index(reversed_char) + 4) % 26
        # 步骤3：替换表转换
        return self.substitution_alphabet[shifted_index]

    def _decrypt_single(self, char):
        """实现解密三步骤的原子操作"""
        # 逆步骤3：查找替换表位置
        sub_index = self.substitution_alphabet.index(char)
        # 逆步骤2：后移4位（考虑循环）
        unshifted_char = self.standard_alphabet[(sub_index - 4) % 26]
        # 逆步骤1：反向映射还原
        return self.standard_alphabet[self.reversed_alphabet.index(unshifted_char)]
