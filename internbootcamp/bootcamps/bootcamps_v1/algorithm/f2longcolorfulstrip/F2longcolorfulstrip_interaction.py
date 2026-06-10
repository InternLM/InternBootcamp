from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.f2longcolorfulstrip.F2longcolorfulstrip_reward_calculator import F2longcolorfulstripRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 998244353



# === 源文件中的全局函数 ===

def compute_answer(n_input, m_input, c_list):
    # Correctly map problem's n (number of colors) and m (strip length) to reference code's variables
    m_code = n_input  # Reference code's m represents problem's n (number of colors)
    n_code = m_input  # Reference code's n represents problem's m (strip length)

    C = [x - 1 for x in c_list]
    
    # Compress consecutive duplicates
    if not C:
        return 0
    C2 = [C[0]]
    for c in C[1:]:
        if C2[-1] != c:
            C2.append(c)
    new_n = len(C2)
    
    # Check if compressed length exceeds 2*m_code (problem's n)
    if new_n > 2 * m_code:
        return 0
    
    pos = [[] for _ in range(m_code)]
    for i in range(new_n):
        c = C2[i]
        if c >= m_code or c < 0:
            return 0
        pos[c].append(i)
    
    # Verify all colors are present
    for color in range(m_code):
        if not pos[color]:
            return 0
    
    DP = [[1] * (new_n + 1) for _ in range(new_n + 1)]
    
    for le in range(1, new_n + 1):
        for i in range(new_n - le + 1):
            j = i + le
            min_color = min(C2[i:j])
            min_indices = [p for p in range(i, j) if C2[p] == min_color]
            if not min_indices:
                DP[i][j] = 0
                continue
            
            first = min(min_indices)
            last = max(min_indices)
            
            # Calculate left part
            left = 0
            for k in range(i, first + 1):
                left = (left + DP[i][k] * DP[k][first]) % MOD
            
            # Calculate right part
            right = 0
            for k in range(last + 1, j + 1):
                right = (right + DP[last + 1][k] * DP[k][j]) % MOD
            
            # Calculate middle parts between occurrences of min_color
            middle = 1
            color_positions = pos[min_color]
            for idx in range(len(color_positions) - 1):
                prev = color_positions[idx]
                next_p = color_positions[idx + 1]
                if prev < i or next_p >= j:
                    continue
                middle = (middle * DP[prev + 1][next_p]) % MOD
            
            DP[i][j] = (left * right % MOD) * middle % MOD
    
    return DP[0][new_n]


class F2longcolorfulstripInteraction(BaseInteraction):
    """F2longcolorfulstrip交互管理器"""
    
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
        score = F2longcolorfulstripRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个F2longcolorfulstrip问题！"""
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

