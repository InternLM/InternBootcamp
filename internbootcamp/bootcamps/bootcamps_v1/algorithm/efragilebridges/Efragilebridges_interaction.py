from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.efragilebridges.Efragilebridges_reward_calculator import EfragilebridgesRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def solve(n_platforms, a):
    """动态规划解法，包含完整边界校验"""
    if n_platforms < 2:
        return 0
    if len(a) != n_platforms - 1:
        raise ValueError("Bridge count mismatch")
    
    n = n_platforms - 1
    x = a.copy()
    
    # 右侧DP初始化
    r = [[0, 0] for _ in range(n_platforms)]
    for i in range(n-1, -1, -1):
        # 计算r[i][1]
        if x[i] == 1:
            r[i][1] = 0
        else:
            next_i = i + 1
            r_next_1 = r[next_i][1] if next_i < n_platforms else 0
            sum_val = r_next_1 + x[i]
            r[i][1] = sum_val & (~1)
        
        # 计算r[i][0]
        next_i = i + 1
        r_next_0 = r[next_i][0] if next_i < n_platforms else 0
        if x[i] % 2 == 1:
            r[i][0] = max(r[i][1], x[i] + r_next_0)
        else:
            r[i][0] = max(r[i][1], (x[i]-1) + r_next_0)
    
    # 左侧DP初始化
    l = [[0, 0] for _ in range(n_platforms)]
    for i in range(1, n_platforms):
        bridge_idx = i-1
        if bridge_idx < 0:
            continue
            
        x_val = x[bridge_idx]
        # 计算l[i][1]
        if x_val == 1:
            l[i][1] = 0
        else:
            prev_i = i-1
            l_prev_1 = l[prev_i][1] if prev_i >= 0 else 0
            sum_val = l_prev_1 + x_val
            l[i][1] = sum_val & (~1)
        
        # 计算l[i][0]
        prev_i = i-1
        l_prev_0 = l[prev_i][0] if prev_i >= 0 else 0
        if x_val % 2 == 1:
            l[i][0] = max(l[i][1], x_val + l_prev_0)
        else:
            l[i][0] = max(l[i][1], (x_val-1) + l_prev_0)
    
    # 计算最大值
    max_score = 0
    for i in range(n_platforms):
        current = r[i][0] + l[i][0]
        max_score = max(max_score, current)
    return max_score


class EfragilebridgesInteraction(BaseInteraction):
    """Efragilebridges交互管理器"""
    
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
        score = EfragilebridgesRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Efragilebridges问题！"""
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

