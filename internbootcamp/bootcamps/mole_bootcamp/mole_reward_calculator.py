import re
import json
import requests
import random
from typing import Optional, Dict, Any

from internbootcamp.src.base_reward_calculator import BaseRewardCalculator
from internbootcamp.bootcamps.mole_bootcamp.ip import ips
from scipy.optimize import differential_evolution
import openmm.unit as unit


class MoleRewardCalculator(BaseRewardCalculator):
    """分子景观优化奖励计算器"""
    
    @staticmethod
    def extract_output(output_str: str) -> Optional[Dict[str, Any]]:
        """
        从模型输出中提取答案（JSON格式：{"pin": "...", "coords": [x, y]}）
        
        Args:
            output_str: 模型的原始输出
            
        Returns:
            Optional[Dict]: 提取的答案字典，包含 pin 和 coords，如果提取失败返回None
        """
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
            parsed = json.loads(json_str)
            # 验证必要字段存在
            if "pin" in parsed and "coords" in parsed:
                return parsed
            return None
        except json.JSONDecodeError:
            return None
    
    @classmethod
    def _verify_correction(cls, extract_solution, identity: dict, **kwargs) -> float:
        """
        验证提取的解决方案并计算正确性分数
        
        Args:
            extract_solution: 从extract_output()提取的字典 {"pin": "...", "coords": [x, y]}
            identity: 任务标准答案信息（来自InstructionGenerator.case_generator()）
            kwargs: 额外关键字参数
            
        Returns:
            float: 正确性分数（0-1之间）
        """
        if extract_solution is None:
            return 0.0

        try:
            # 从字典中提取坐标
            if not isinstance(extract_solution, dict):
                print(f"    [验证失败] 提取的答案不是字典格式")
                return 0.0
            
            coords = extract_solution.get("coords")
            if not coords or not isinstance(coords, list) or len(coords) != 2:
                print(f"    [验证失败] coords 字段无效: {coords}")
                return 0.0
            
            x, y = coords[0], coords[1]
            
            # 检查坐标是否在有效范围内
            if not (0 <= x <= 10 and 0 <= y <= 10):
                print(f"    [验证失败] 坐标超出范围: ({x:.2f}, {y:.2f})")
                return 0.0

            env_id = identity.get('env_id')
            
            # 通过 HTTP API 验证
            return cls._verify_via_api(env_id, x, y, identity)
                
        except Exception as e:
            print(f"    [验证错误] {e}")
            import traceback
            print(f"    [验证错误] 异常堆栈:\n{traceback.format_exc()}")
            return 0.0
    
    @classmethod
    def _verify_via_api(cls, env_id: str, x: float, y: float, identity: dict) -> float:
        """通过 API 验证解决方案"""
        try:
            # 调用 API 获取能量
            response = requests.post(
                f"{random.choice(ips)}/get_energy",
                headers={"Content-Type": "application/json"},
                json={
                    "env_id": env_id,
                    "x": x,
                    "y": y
                },
                timeout=120
            )
            
            if response.status_code != 200:
                print(f"    [验证错误] API 错误: {response.status_code}")
                return 0.0
            
            result = response.json()
            if not result.get("success"):
                print(f"    [验证错误] API 调用失败: {result.get('message')}")
                return 0.0
            
            pred_energy = result.get("energy")
            
            # 获取真实最小能量
            true_min_energy = identity['global_min_energy']
            diff = abs(pred_energy - true_min_energy)
            
            # 获取容差
            tolerance = identity.get('tolerance', 1.5)

            if diff <= tolerance:
                return 1.0
            else:
                return 0.0
                
        except requests.exceptions.Timeout:
            print("    [验证错误] API 请求超时")
            return 0.0
        except Exception as e:
            print(f"    [验证错误] {e}")
            import traceback
            print(f"    [验证错误] 异常堆栈:\n{traceback.format_exc()}")
            return 0.0
