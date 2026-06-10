from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cvulnerablekerbals.Cvulnerablekerbals_reward_calculator import CvulnerablekerbalsRewardCalculator

# 导入依赖库
import re
import math
import random
from collections import defaultdict

# === 源文件中的全局函数 ===

def exgcd(a, b):
    if b == 0:
        return (a, 1, 0)
    else:
        g, x, y = exgcd(b, a % b)
        return (g, y, x - (a // b) * y)

def generate_solution_for_m(m):
    vis = set()
    g = defaultdict(list)
    for i in range(m):
        if i not in vis:
            g_val = math.gcd(i, m)
            g[g_val].append(i)
    
    divisors = [d for d in range(1, m + 1) if m % d == 0]
    divisors.sort()
    
    dp = {d: 0 for d in divisors}
    pre = {d: None for d in divisors}
    
    for d in divisors:
        dp[d] = len(g.get(d, []))
        j = 2 * d
        while j <= m:
            if j not in divisors:
                j += d
                continue
            if dp[j] < dp[d]:
                dp[j] = dp[d]
                pre[j] = d
            elif dp[j] == dp[d]:
                if pre[j] is None or pre[j] < d:
                    pre[j] = d
            j += d
    
    current_d = m
    w = []
    while True:
        w.extend(g.get(current_d, []))
        if current_d == 1:
            break
        current_d = pre.get(current_d)
        if current_d is None:
            break
    
    if not w:
        return 0, []
    
    sequence = []
    sequence.append(w[-1])
    for i in range(len(w)-1, 0, -1):
        a = w[i]
        b = w[i-1]
        g_val, x, y = exgcd(a, m)
        assert b % g_val == 0, "No solution"
        x0 = (x * (b // g_val)) % (m // g_val)
        sequence.append(x0)
    
    current = 1
    prefix_products = []
    for num in sequence:
        current = (current * num) % m
        prefix_products.append(current)
    
    return len(sequence), prefix_products


class CvulnerablekerbalsInteraction(BaseInteraction):
    """Cvulnerablekerbals交互管理器"""
    
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
        score = CvulnerablekerbalsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cvulnerablekerbals问题！"""
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

