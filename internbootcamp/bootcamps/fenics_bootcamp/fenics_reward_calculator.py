import re
import requests
import random
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator
from internbootcamp.bootcamps.fenics_bootcamp.ip import ips


class FenicsRewardCalculator(BaseRewardCalculator):
    """热控制奖励计算器，用于评估热通量参数优化任务"""
    
    @staticmethod
    def extract_output(output_str: str):
        """
        从模型输出中提取热通量参数
        
        Args:
            output_str: 模型的原始输出
            
        Returns:
            Optional[tuple]: 提取的参数 (flux_left, flux_bottom)，如果提取失败返回None
        """
        if not output_str: 
            return None
        
        # 匹配 \boxed{flux_left, flux_bottom} 格式
        pattern = r"\\boxed\{\s*([-\d\.eE+]+),\s*([-\d\.eE+]+)\s*\}"
        
        match = re.search(pattern, output_str)
        if match:
            try:
                val1 = float(match.group(1))
                val2 = float(match.group(2))
                return (val1, val2)
            except ValueError:
                return None
        return None
    
    @classmethod
    def _verify_correction(cls, extract_solution, identity: dict, **kwargs) -> float:
        """
        验证提取的解决方案并计算正确性分数
        
        Args:
            extract_solution: 从extract_output()提取的参数 (flux_left, flux_bottom)
            identity: 任务标准答案信息（来自InstructionGenerator.case_generator()）
            kwargs: 额外关键字参数（可以包含 use_api=True 来使用 API 验证）
            
        Returns:
            float: 正确性分数（0-1之间）
        """
        if not extract_solution: 
            return 0.0
        
        try:
            flux_left, flux_bottom = extract_solution
            
            # 构建配置字典
            config = {
                "length": identity["length"],
                "width": identity["width"],
                "kappa_base": identity["kappa_base"],
                "alpha": identity["alpha"],
                "source_amp": identity["source_amp"]
            }
            
            m1 = (identity["monitor1_x"], identity["monitor1_y"])
            m2 = (identity["monitor2_x"], identity["monitor2_y"])
            
            # 使用 API 进行验证
            payload = {
                "length": config["length"],
                "width": config["width"],
                "kappa_base": config["kappa_base"],
                "alpha": config["alpha"],
                "source_amp": config["source_amp"],
                "flux_left": flux_left,
                "flux_bottom": flux_bottom,
                "monitor1_x": m1[0],
                "monitor1_y": m1[1],
                "monitor2_x": m2[0],
                "monitor2_y": m2[1]
            }
            
            try:
                response = requests.post(
                    f"{random.choice(ips)}/run_thermal_simulation",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=200
                )
                
                if not response.ok:
                    print(f"  [验证失败] API 返回状态码 {response.status_code}")
                    return 0.0
                
                result = response.json()
                if not result.get("success"):
                    print(f"  [验证失败] API 错误: {result.get('message', 'Unknown error')}")
                    return 0.0
                
                res = {
                    "status": "success",
                    "temp_monitor1": result["temp_monitor1"],
                    "temp_monitor2": result["temp_monitor2"],
                    "max_temp": result["max_temp"]
                }
                
            except requests.exceptions.RequestException as e:
                print(f"  [验证失败] API 请求失败: {str(e)}")
                return 0.0
            
            if res["status"] != "success":
                print(f"  [验证失败] 仿真出错: {res.get('message', 'Unknown error')}")
                return 0.0
            
            # 检查是否满足目标条件
            target1 = identity["target_temp1"]
            target2 = identity["target_temp2"]
            tolerance = identity["tolerance"]
            max_temp_limit = identity["max_temp_limit"]
            
            actual_t1 = res["temp_monitor1"]
            actual_t2 = res["temp_monitor2"]
            actual_max = res["max_temp"]
            
            # 判断各项指标
            success_1 = abs(actual_t1 - target1) <= tolerance
            success_2 = abs(actual_t2 - target2) <= tolerance
            success_safety = actual_max <= max_temp_limit
            
            # 如果同时满足所有条件，返回满分
            if success_1 and success_2 and success_safety:
                return 1.0
            elif success_1 and success_2 and not success_safety:
                return 0.5
            elif (success_1 or success_2) and success_safety:
                return 0.25
            else:
                return 0.0
            
        except Exception as e:
            print(f"[DEBUG FenicsRewardCalculator] 验证时出错: {str(e)}")
            import traceback
            print(f"[DEBUG FenicsRewardCalculator] 异常堆栈:\n{traceback.format_exc()}")
            return 0.0
