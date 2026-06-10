import re
import math
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator


class ExampleRewardCalculator(BaseRewardCalculator):
    """示例奖励管理器，用于评估算术运算任务"""
    
    @staticmethod
    def extract_output(output_str: str) -> Optional[Dict[str, Any]]:
        """
        从模型输出中提取算术运算结果
        
        Args:
            output_str (str): 模型的原始输出
            
        Returns:
            Optional[Dict[str, Any]]: 提取的运算信息，包含操作符、操作数和结果
        """
        if not output_str:
            return None
        # 如果完整JSON解析失败，尝试匹配JSON中的result字段
        # 支持科学计数法：包括 1e-4, 2.5E+3, -1.23e10 等格式
        pattern = r'"result":\s*([+-]?(?:\d+\.?\d*|\d*\.?\d+)(?:[eE][+-]?\d+)?)'
        matches = list(re.finditer(pattern, output_str))
        if matches:
            # 从右往左匹配，取最后一个匹配的结果
            result = float(matches[-1].group(1))
            return result
        
        return None
        

    @classmethod
    def _verify_correction(cls, extracted_output, identity: dict, **kwargs) -> float:
        """
        验证用户输出并计算得分
        
        Args:
            extracted_output: 提取的运算信息
            identity (dict): 任务信息，包含期望的运算和结果
            score_max (float): 最高分数
            score_min (float): 最低分数
            
        Returns:
            float: 得分
        """
        print_hello_world = kwargs.get('print_hello_world', False)
        soft_reward = kwargs.get('soft_reward', False)
        if print_hello_world:
            print("ExampleRewardCalculator's verify_correction is saying HELLOWORLD!")
        try:
            if not extracted_output:
                return 0.0

            expected_result = identity.get("expected_result")
            
            if expected_result is not None and extracted_output is not None:
                # tolerance 表示最大相对误差比例，例如 0.01 表示允许 1% 的相对误差
                tolerance = float(identity.get("tolerance", 1e-4))
                ref = max(abs(expected_result), 1e-15)  # 避免除零
                relative_error = abs(extracted_output - expected_result) / ref
                if relative_error <= tolerance:
                    return 1.0
                else:
                    return cls._calculate_score(extracted_output, expected_result, tolerance, soft_reward)
        
            # 如果没有匹配的类型，返回最低分
            return 0.0
            
        except Exception as e:
            print(f"[DEBUG ExampleRewardManager] 验证时出错: {str(e)}")
            import traceback
            print(f"[DEBUG ExampleRewardManager] 异常堆栈:\n{traceback.format_exc()}")
            return 0.0

    @classmethod
    def _calculate_score(cls, extracted_output: float, expected_result: float, tolerance: float = 1e-4, soft_reward: bool = False) -> float:
        """
        根据结果匹配度计算得分
        
        Args:
            extracted_output (float): 实际结果
            expected_result (float): 期望结果
            tolerance (float): 最大相对误差比例，例如 0.01 表示 1%
            soft_reward (bool): 是否使用软奖励
            
        Returns:
            float: 得分 [0.0, 1.0]
        """
        if math.isnan(extracted_output) or math.isinf(extracted_output):
            return 0.0
        
        # 计算相对误差
        ref = max(abs(expected_result), 1e-15)  # 避免除零
        relative_error = abs(extracted_output - expected_result) / ref
        
        if relative_error <= tolerance:
            return 1.0
        else:
            if soft_reward:
                # 使用基于 tolerance 的自适应指数衰减 + 洛伦兹函数混合
                # 归一化误差：相对误差超出 tolerance 的倍数
                normalized_error = (relative_error - tolerance) / tolerance
                
                # 方案1: 指数衰减 (适用于误差较小的情况)
                # 当误差为2*tolerance时，得分约为0.61
                # 当误差为5*tolerance时，得分约为0.22
                exp_score = math.exp(-normalized_error / 2.0)
                
                # 方案2: 洛伦兹函数 (重尾分布，对大误差更宽容)
                # 当误差为2*tolerance时，得分约为0.5
                # 当误差为5*tolerance时，得分约为0.2
                lorentzian_score = 1.0 / (1.0 + normalized_error**2)
                
                # 混合策略：小误差时指数衰减更快，大误差时洛伦兹更宽容
                # 使用平滑过渡权重
                alpha = 1.0 / (1.0 + normalized_error)  # 小误差时alpha接近1，大误差时接近0
                final_score = alpha * exp_score + (1 - alpha) * lorentzian_score
                
                return final_score
            else:
                return 0.0
            
if __name__ == "__main__":
    print(ExampleRewardCalculator._calculate_score(10000, 10001, 1e-8, True))