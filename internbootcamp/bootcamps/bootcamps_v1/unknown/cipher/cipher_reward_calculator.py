import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import ast
import re
import json
import distance
from internbootcamp.bootcamps.bootcamps_v1.unknown.cipher.lib.bootcamp_utils import catch_print

# === 源文件中的全局变量 ===

cipher_env_dict = {}


class CipherRewardCalculator(BaseRewardCalculator):
    """Cipher奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        Extract the output from the solution.
        
        Args:
            output: Model output to be processed.
        
        Returns:
            The processed output.
        """
        pattern = pattern = r'```text\s*([\s\S]*?)\s*```'
        matches = re.findall(pattern, output)

        if matches:
            # 获取 JSON 字符串
            json_str = matches[-1]
            # print('match?', json_str)
            # print('solution generated? first lines', output[:200])
            # print('solution generated? last lines', output[-200:])
            # 替换单引号为双引号，将元组表示改为列表表示
            json_str = json_str.replace("'", '"').replace("(", "[").replace(")", "]")
            try:
                # 解析 JSON 字符串为 Python 字典
                result_dict = json.loads(json_str) if type(json_str) == dict else json_str
                return result_dict
            except json.JSONDecodeError as e:
                # print(f"JSON 解析错误: {e}")
                return json_str
        else:
            return None
    
    @staticmethod 
    def _verify_correction(solution, identity)->bool:
        
        input_str = identity.pop('input')
        cipher_source = identity.pop('source_filename')
        cipher_name = identity.pop('cipher_name')
        extra_args = identity.pop('extra_args',{})
        
        this_cipher_env = None
        for cipher_env_name,cipher_env in cipher_env_dict.items():
            if cipher_env_name == cipher_name:
                this_cipher_env = cipher_env
                break
        if not this_cipher_env:
            raise ValueError(f"cipher_source {cipher_source} is not supported")
        else:
            this_cipher = this_cipher_env()
            
        # 将solution转为小写
        solution = solution.lower()
        
            
        if 'encode' in cipher_source:
            this_cipher.generator(plaintext=input_str, **extra_args)
            # ground_truth 小写
            ground_truth = str(this_cipher.ciphertext).lower()
            score = 1 - min(distance.levenshtein(solution, ground_truth) / len(ground_truth), 1.0)
        elif 'decode' in cipher_source:
            # if 'ASCII' in cipher_source:
            #     input_str = ast.literal_eval(input_str)
            _,ground_truth = catch_print(this_cipher.decode,text=input_str, **extra_args)
            ground_truth = str(ground_truth).lower()
            score = 1 - min(distance.levenshtein(solution, ground_truth) / len(ground_truth), 1.0)
            
        return score*score
    
    # 其他额外方法

