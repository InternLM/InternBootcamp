from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cfancynumber.Cfancynumber_reward_calculator import CfancynumberRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def solve_beautiful_number(n, k, original_number):
    s = list(original_number)
    c = [0] * 10
    for i in range(n):
        digit = int(s[i])
        c[digit] += 1

    def choosevalue(m):
        nonlocal c, n, k, s
        if c[m] >= k:
            return (0, original_number)
        p = s.copy()
        total_cost = 0
        remain = k - c[m]
        for i in range(1, 10):
            R = m + i
            L = m - i
            # Process R direction (higher digits)
            if R <= 9 and remain > 0:
                for j in range(n):
                    if remain <= 0:
                        break
                    if int(p[j]) == R:
                        p[j] = str(m)
                        total_cost += i
                        remain -= 1
            # Process L direction (lower digits)
            if L >= 0 and remain > 0:
                for j in range(n-1, -1, -1):
                    if remain <= 0:
                        break
                    if int(p[j]) == L:
                        p[j] = str(m)
                        total_cost += i
                        remain -= 1
            if remain <= 0:
                break
        new_number = ''.join(p)
        return (total_cost, new_number)

    best_cost = float('inf')
    best_number = None
    for m in range(10):
        current_cost, current_number = choosevalue(m)
        if current_cost < best_cost:
            best_cost = current_cost
            best_number = current_number
        elif current_cost == best_cost:
            if current_number < best_number:
                best_number = current_number
    return (best_cost, best_number)


class CfancynumberInteraction(BaseInteraction):
    """Cfancynumber交互管理器"""
    
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
        score = CfancynumberRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cfancynumber问题！"""
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

