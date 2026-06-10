from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.enumbertransformation.Enumbertransformation_reward_calculator import EnumbertransformationRewardCalculator

# 导入依赖库
import random
import re
import math

# === 源文件中的全局函数 ===

def lcm(a, b):
    return a * b // math.gcd(a, b)

def compute_mod(k):
    mod = 1
    for x in range(2, k+1):
        mod = lcm(mod, x)
    return mod

def dynamic_get(r1, r2, k):
    x_list = list(range(2, k+1))
    max_r = r2
    d = [float('inf')] * (max_r + 1)
    d[r1] = 0

    current_mods = [r1 % x for x in x_list]

    for i in range(r1 + 1, r2 + 1):
        new_mods = []
        min_steps = d[i-1] + 1
        for idx, x in enumerate(x_list):
            new_mod = current_mods[idx] + 1
            if new_mod >= x:
                new_mod = 0
            new_mods.append(new_mod)
            if new_mod != 0 and i - new_mod >= r1:
                candidate = d[i - new_mod] + 1
                if candidate < min_steps:
                    min_steps = candidate
        current_mods = new_mods
        d[i] = min_steps
    return d[r2]

def solve(a, b, k):
    if a == b:
        return 0
    mod = compute_mod(k)
    ra = a % mod
    rb = b % mod

    if a - b < mod and ra >= rb:
        return dynamic_get(rb, ra, k)
    else:
        part1 = dynamic_get(rb, mod - 1, k) + 1  # 上升到模的倍数
        part2 = dynamic_get(0, ra, k)
        cycle_num = (a - ra - (b - rb + mod)) // mod
        part3 = (dynamic_get(0, mod-1, k) + 1) * cycle_num
        return part1 + part2 + part3


class EnumbertransformationInteraction(BaseInteraction):
    """Enumbertransformation交互管理器"""
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

    async def start_interaction(self, instance_id: Optional[str] = None, identity: dict[str, Any] = None, **kwargs) -> str:
        """开始交互会话"""
        return await super().start_interaction(instance_id, identity, **kwargs)

    async def generate_response(self, instance_id: str, messages: list[dict[str, Any]], **kwargs) -> tuple[bool, str, float, dict[str, Any]]:
        """
        生成交互反馈响应
        
        Args:
            instance_id: 实例ID
            messages: 对话历史消息列表
            
        Returns:
            should_terminate_sequence: 是否终止交互序列
            response_content: 反馈内容
            current_turn_score: 当前轮次得分
            additional_data: 额外数据
        """
        # 获取最近的assistant消息
        assistant_content = ""
        for i in range(len(messages) - 1, -1, -1):
            item = messages[i]
            if item.get("role") == "assistant":
                assistant_content = item.get("content", "")
                break
        
        if not assistant_content:
            return False, "请提供你的解决方案。", 0.0, {}
        
        # 使用奖励计算器评估解决方案
        identity = self._instance_dict[instance_id]['identity']
        score = EnumbertransformationRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Enumbertransformation问题！"""
            should_terminate = True
            
        elif score > 0.0:
            response = f"""⚠️ 你的解决方案部分正确（得分: {score:.2f}/1.0），但仍有一些问题需要解决。

请检查并修正你的解决方案。"""
            should_terminate = False
            
        else:
            response = f"""❌ 你的解决方案存在错误（得分: {score:.2f}/1.0）。

请重新思考并提供新的解决方案。"""
            should_terminate = False
        
        return should_terminate, response, score, {}

    async def calculate_score(self, instance_id: str, **kwargs) -> float:
        """计算交互得分"""
        return await super().calculate_score(instance_id, **kwargs)

    async def finalize_interaction(self, instance_id: str, **kwargs) -> bool:
        """结束交互并释放资源"""
        return await super().finalize_interaction(instance_id, **kwargs)
    
    # 其他额外方法

