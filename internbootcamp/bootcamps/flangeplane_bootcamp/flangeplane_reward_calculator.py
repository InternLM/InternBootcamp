import re
import math
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator
from internbootcamp.bootcamps.flangeplane_bootcamp.utils.cost_cal import cost_analysis
from internbootcamp.bootcamps.flangeplane_bootcamp.ip import ips

import requests

import random


class FlangeplaneRewardCalculator(BaseRewardCalculator):
    @staticmethod
    def extract_output(output_str: str):
        if output_str:
            mark = "```json"
            left_brace_idx = output_str.rfind(mark)
            if left_brace_idx < 0:
                return None
            left_brace_idx += len(mark)

            right_brace_idx = output_str[left_brace_idx:].find("```")

            if right_brace_idx < 0:
                return None
            right_brace_idx += left_brace_idx

            try:
                return json.loads(output_str[left_brace_idx: right_brace_idx])
            except:
                return None
        else:
            return None
        
    @classmethod
    def _verify_correction(cls, extracted_output, identity: dict, **kwargs) -> float:
        try:
            if not extracted_output:
                return 0.0

            mat_ext = None
            for mat in identity["mats"]:
                if mat["Name"] == extracted_output["材料"]:
                    mat_ext = mat

            if not mat:
                print("{} 不是有效材料".format(extracted_output["材料"]))
                return 0.0

            PAYLOAD = {
                    "D": float(extracted_output["外圆半径(mm)"]), 
                    "B1": identity["B1"], 
                    "L": float(extracted_output["螺栓孔半径(mm)"]), 
                    "BoltCenterRadius": float(extracted_output["螺栓孔圆心分布的圆周半径(mm)"]), 
                    "thickness": float(extracted_output["厚度(mm)"]), 
                    "bolt_count_edit": float(extracted_output["螺栓孔数目"]), 
                    "Name": mat_ext["Name"], 
                    "YoungsModulus": mat_ext["YoungsModulus"], 
                    "PoissonRatio": mat_ext["PoissonRatio"], 
                    "Density": mat_ext["Density"], 
                    "pressure": identity["pressure"]
                    }
            try:           
                response = requests.post(f"{random.choice(ips)}/cae_analysis", 
                                        headers={"Content-Type": "application/json"}, 
                                        json=PAYLOAD, 
                                        timeout=200)     
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
                print(result["info"])
                return 0.0

            cost = cost_analysis(float(extracted_output["厚度(mm)"]), float(extracted_output["外圆半径(mm)"]), identity["B1"], float(extracted_output["螺栓孔数目"]), float(extracted_output["螺栓孔半径(mm)"]), mat_ext["Density"], mat_ext["price"])

            if (result["disp_max"] - result["unit"] <= identity["disp_max"]) and (cost <= identity["cost"]):
                return 1.0
            else:
                return 0.0
            
        except Exception as e:
            print(f"[DEBUG FlangeplaneRewardCalculator] 验证时出错: {str(e)}")
            import traceback
            print(f"[DEBUG FlangeplaneRewardCalculator] 异常堆栈:\n{traceback.format_exc()}")
            return 0.0
