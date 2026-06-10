from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cpackagedelivery.Cpackagedelivery_reward_calculator import CpackagedeliveryRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_min_cost(d, n, m, stations):
    sorted_stations = sorted(stations + [(d, 0)], key=lambda x: x[0])
    prev_pos = 0
    for x, _ in sorted_stations:
        if x - prev_pos > n:
            return -1
        prev_pos = x
    
    stack = []
    next_lower = [None] * len(sorted_stations)
    
    # Preprocess next_lower using monotonic stack
    for i in reversed(range(len(sorted_stations))):
        while stack and sorted_stations[stack[-1]][1] >= sorted_stations[i][1]:
            stack.pop()
        if stack:
            next_lower[i] = stack[-1]
        else:
            next_lower[i] = None
        stack.append(i)
    
    current_pos = 0
    current_fuel = n
    total_cost = 0
    
    for i, (x, p) in enumerate(sorted_stations):
        distance = x - current_pos
        current_fuel -= distance
        if current_fuel < 0:
            return -1
        current_pos = x
        
        if x == d:
            break
        
        j = next_lower[i]
        if j is None:
            max_reach = min(current_pos + n, d)
            buy = min(n - current_fuel, max_reach - x)
            if buy < 0:
                continue
            total_cost += buy * p
            current_fuel += buy
        else:
            max_reach = sorted_stations[j][0]
            required = max(0, (max_reach - x) - current_fuel)
            buy = min(required, n - current_fuel)
            total_cost += buy * p
            current_fuel += buy
        
        if current_fuel < 0:
            return -1
    
    return total_cost if current_pos == d else -1


class CpackagedeliveryInteraction(BaseInteraction):
    """Cpackagedelivery交互管理器"""
    
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
        score = CpackagedeliveryRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cpackagedelivery问题！"""
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

