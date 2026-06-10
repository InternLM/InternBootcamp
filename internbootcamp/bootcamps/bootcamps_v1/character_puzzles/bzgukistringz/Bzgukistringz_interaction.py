from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.character_puzzles.bzgukistringz.Bzgukistringz_reward_calculator import BzgukistringzRewardCalculator

# 导入依赖库
from collections import Counter
import random
import string
import re

# === 源文件中的全局函数 ===

def compute_max_counts(a, b, c):
    a_counts = [0] * 26
    for char in a:
        a_counts[ord(char) - ord('a')] += 1

    b_counts = [0] * 26
    for char in b:
        b_counts[ord(char) - ord('a')] += 1

    c_counts = [0] * 26
    for char in c:
        c_counts[ord(char) - ord('a')] += 1

    best_bs = 0
    best_cs = 0
    max_total = 0

    # 模拟原题代码，枚举bs到a的长度+1
    max_bs = len(a)
    for bs in range(0, max_bs + 1):
        possible = True
        a_clone = a_counts.copy()
        for i in range(26):
            required = bs * b_counts[i]
            if a_clone[i] < required:
                possible = False
                break
            a_clone[i] -= required
        if not possible:
            continue

        # 计算c的最大次数
        cs = float('inf')
        for i in range(26):
            if c_counts[i] == 0:
                continue
            available = a_clone[i]
            if available < c_counts[i]:
                cs = 0
                break
            cs = min(cs, available // c_counts[i])
        if cs == float('inf'):
            cs = 0

        total = bs + cs
        if total > max_total or (total == max_total and cs > best_cs):
            max_total = total
            best_bs = bs
            best_cs = cs

    return best_bs, best_cs

def count_max_substrings(k_str, b, c):
    subs = []
    len_b, len_c = len(b), len(c)
    if len_b > 0:
        subs.append((len_b, b))
    if len_c > 0 and b != c:
        subs.append((len_c, c))

    n = len(k_str)
    dp = [0] * (n + 1)

    for i in range(n):
        dp[i + 1] = max(dp[i + 1], dp[i])
        for length, sub in subs:
            if i + length > n:
                continue
            if k_str[i:i + length] == sub:
                dp[i + length] = max(dp[i + length], dp[i] + 1)
    return dp[n]


class BzgukistringzInteraction(BaseInteraction):
    """Bzgukistringz交互管理器"""
    
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
        score = BzgukistringzRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Bzgukistringz问题！"""
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

