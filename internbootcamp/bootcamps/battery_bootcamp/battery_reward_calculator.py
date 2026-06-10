import re
from typing import Optional, Dict, Any

from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

from internbootcamp.bootcamps.battery_bootcamp.battery_utils import execute_pybamm_logic


class BatteryRewardCalculator(BaseRewardCalculator):
    """电池设计奖励计算器，用于评估电池参数优化任务"""
    
    @staticmethod
    def extract_output(output_str: str):
        """
        从模型输出中提取电池设计参数
        
        Args:
            output_str: 模型的原始输出
            
        Returns:
            Optional[tuple]: 提取的设计参数 (thickness, porosity)，如果提取失败返回None
        """
        if not output_str: 
            return None
        
        # 匹配 \boxed{thickness, porosity} 格式
        # \s* : 允许花括号内有空格
        # [-\d\.eE+]+ : 允许数字、负号、小数点、e/E(科学计数法)、+(指数的正号)
        pattern = r"\\boxed\{\s*([-\d\.eE+]+),\s*([-\d\.eE+]+)\s*\}"
        
        match = re.search(pattern, output_str)
        if match:
            try:
                # 尝试将捕获的字符串转换为 float，Python 的 float() 原生支持科学计数法
                val1 = float(match.group(1))
                val2 = float(match.group(2))
                return (val1, val2)
            except ValueError:
                # 如果捕获到了类似 "1.2.e.4" 这种符合正则但无法转数字的情况
                return None
        return None
    
    @classmethod
    def _verify_correction(cls, extract_solution, identity: dict, **kwargs) -> float:
        """
        验证提取的解决方案并计算正确性分数
        
        Args:
            extract_solution: 从extract_output()提取的参数 (thickness, porosity)
            identity: 任务标准答案信息（来自InstructionGenerator.case_generator()）
            kwargs: 额外关键字参数
            
        Returns:
            float: 正确性分数（0-1之间）
        """
        if not extract_solution: 
            return 0.0
        
        try:
            thickness, porosity = extract_solution
            
            # 使用提取的参数执行仿真验证
            res = execute_pybamm_logic(thickness, porosity, identity)
            
            if res["status"] != "success":
                return 0.0
            
            # 检查是否满足目标条件
            target_wh_kg = identity.get("target_specific_energy", 0)
            target_temp = identity.get("target_max_temp", 9999)
            
            actual_wh_kg = res["specific_energy"]
            actual_temp = res["max_temp"]
            
            # 如果同时满足两个条件，返回满分
            if actual_wh_kg >= target_wh_kg and actual_temp <= target_temp:
                return 1.0
            
            # 否则返回0分
            return 0.0
            
        except Exception as e:
            print(f"[DEBUG BatteryRewardCalculator] 验证时出错: {str(e)}")
            import traceback
            print(f"[DEBUG BatteryRewardCalculator] 异常堆栈:\n{traceback.format_exc()}")
            return 0.0


# 与 bootcamp_registry、评测脚本中使用的名称一致
BatteryDesignRewardCalculator = BatteryRewardCalculator
