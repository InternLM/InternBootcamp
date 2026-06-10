import re
import math
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator
from internbootcamp.bootcamps.escape_bootcamp.ip import ips

import random

import requests


class EscapeRewardCalculator(BaseRewardCalculator):
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
                response = requests.post(f"{random.choice(ips)}/get_result", 
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

            success, turns = result["success"], result["turns"]

            
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
            if success:
                if turns <= identity["max_turns"]:
                    return 1.0
                else:
                    return 1.0 - 0.1 * (turns - identity["max_turns"])
            else:
                return 0.0
            
        except Exception as e:
            print(f"[DEBUG EscapeRewardManager] 验证时出错: {str(e)}")
            import traceback
            print(f"[DEBUG EscapeRewardManager] 异常堆栈:\n{traceback.format_exc()}")
            return 0.0
