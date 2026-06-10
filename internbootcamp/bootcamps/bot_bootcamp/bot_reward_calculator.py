import re
import math
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator
from internbootcamp.bootcamps.bot_bootcamp.ip import ips

import numpy as np

import random

import requests


class BotRewardCalculator(BaseRewardCalculator):
    @staticmethod
    def extract_output(output_str: str) -> Optional[Dict[str, Any]]:
        if not output_str:
            return None

        # 模式 1: 匹配 Markdown 代码块 ```json ... ```
        # re.DOTALL 让 . 可以匹配换行符
        code_block_pattern = r"```json\s*(\{.*?\})\s*```"
        match = re.search(code_block_pattern, output_str, re.DOTALL)
        
        if match:
            json_str = match.group(1)
        else:
            # 模式 2: 如果没有代码块，尝试寻找第一个 { 和最后一个 } 之间的内容
            # 这种方式比较激进，假设整个字符串中最大的 { ... } 块就是 JSON
            brace_pattern = r"\{.*\}"
            match = re.search(brace_pattern, output_str, re.DOTALL)
            if match:
                json_str = match.group(0)
            else:
                return None

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
        
    @classmethod
    def _verify_correction(cls, extracted_output, identity: dict, **kwargs) -> float:
        try:
            # judge
            PAYLOAD = {
                "case_id": identity["case_id"],
                "pin": extracted_output["pin"],
                "joint_angles": extracted_output["joint_angles"]}
            try:           
                response = requests.post(f"{random.choice(ips)}/check_collision", 
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

            if result["success"]:
                is_collision, coord = result["is_collision"], result["coord"]
                dist = np.linalg.norm(np.array(coord) - np.array(identity['target']))
            else:
                is_collision, coord, dist = True, -1, -1

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
            if is_collision:
                return 0.0
            else:
                return float(dist <= 0.05)
            
        except Exception as e:
            print(f"[DEBUG BotRewardManager] 验证时出错: {str(e)}")
            # import traceback
            # print(f"[DEBUG BotRewardManager] 异常堆栈:\n{traceback.format_exc()}")
            return 0.0
