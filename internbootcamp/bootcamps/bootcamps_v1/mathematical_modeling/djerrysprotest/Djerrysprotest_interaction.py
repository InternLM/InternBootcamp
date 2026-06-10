from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.djerrysprotest.Djerrysprotest_reward_calculator import DjerrysprotestRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def calculate_probability(n, a_list):
    a = {}
    for i in range(n-1):
        for j in range(i+1, n):
            x = abs(a_list[i] - a_list[j])
            a[x] = a.get(x, 0) + 1

    d = list(a.keys())
    b = [0] * 10005

    for i in range(len(d)):
        for j in range(i, len(d)):
            key_i = d[i]
            key_j = d[j]
            sum_key = key_i + key_j
            contribution = a[key_i] * a[key_j]
            if key_i != key_j:
                contribution *= 2
            if sum_key < len(b):
                b[sum_key] += contribution

    for i in range(1, len(b)):
        b[i] += b[i-1]

    ans = 0
    for i in range(n-1):
        for j in range(i+1, n):
            s = abs(a_list[i] - a_list[j])
            if s - 1 >= 0 and s - 1 < len(b):
                ans += b[s - 1]

    den = (n * (n-1) // 2) ** 3
    return ans / den if den != 0 else 0.0

def is_close(a, b, rel_tol=1e-6, abs_tol=1e-6):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class DjerrysprotestInteraction(BaseInteraction):
    """Djerrysprotest交互管理器"""
    
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
        score = DjerrysprotestRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Djerrysprotest问题！"""
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

