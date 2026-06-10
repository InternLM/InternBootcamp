import re
import math
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator
from internbootcamp.bootcamps.holdem_bootcamp.ip import ips

import requests

import numpy as np

import random


class HoldemRewardCalculator(BaseRewardCalculator):
    @staticmethod
    def extract_output(output_str: str) -> Optional[Dict[str, Any]]:        
        if not output_str: 
            return None
        
        # 1. \s* : 允许花括号内有空格
        # 2. [-\d\.eE+]+ : 允许数字、负号、小数点、e/E(科学计数法)、+(指数的正号)
        pattern = r"\\boxed\{\s*([-\d\.eE+]+)\s*\}"
        
        match = re.search(pattern, output_str)
        if match:
            try:
                return match.group(1)
            except ValueError:
                # 如果捕获到了类似 "1.2.e.4" 这种符合正则但无法转数字的情况
                return None
        return None
        
    @classmethod
    def _verify_correction(cls, extracted_output, identity: dict, **kwargs) -> float:
        try:
            # judge
            PAYLOAD = {
                "game_id": identity["game_id"],
                "pin": extracted_output}
            try:           
                response = requests.post(f"{random.choice(ips)}/ScoreBoard", 
                                        headers={"Content-Type": "application/json"}, 
                                        json=PAYLOAD, 
                                        timeout=120)     
            except requests.exceptions.RequestException as e:
                print(f"Request failed, {e}")
                return 0.0

            if not response.ok:
                print(f"Server returned status {response.status_code}")
                return 0.0

            try:
                result = response.json()
            except ValueError:
                print(f"Response is not json format, {response.text}")
                return 0.0
            
            if not result["success"]:
                return 0.0
            actual_return, initial_stack = result["actual_return"], result["initial_stack"]

            # delete
            try:           
                response = requests.post(f"{random.choice(ips)}/remove_game", 
                                        headers={"Content-Type": "application/json"}, 
                                        json=PAYLOAD, 
                                        timeout=120)     
            except requests.exceptions.RequestException as e:
                print(f"Request failed, {e}")

            if not response.ok:
                print(f"Server returned status {response.status_code}")

            try:
                result = response.json()
            except ValueError:
                print(f"Response is not json format, {response.text}")

            # score                
            k = 5
            x = actual_return / initial_stack
            return 1 / (1 + np.exp(-k * x))  # 0.5 * (1 + x) 
            
        except Exception as e:
            print(f"[DEBUG HoldemRewardManager] 验证时出错: {str(e)}")
            import traceback
            print(f"[DEBUG HoldemRewardManager] 异常堆栈:\n{traceback.format_exc()}")
            return 0.0
