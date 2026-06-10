from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ebearandcompany.Ebearandcompany_reward_calculator import EbearandcompanyRewardCalculator

# 导入依赖库
import random
import string
from collections import defaultdict
import re

# === 源文件中的全局函数 ===

def compute_min_swaps(n, s):
    a, b, c = [], [], []
    for i in range(n):
        char = s[i]
        if char == 'V':
            a.append(i)
        elif char == 'K':
            b.append(i)
        else:
            c.append(i)
    
    def count(arr, st, x):
        ret = 0
        i = st
        while i < len(arr) and arr[i] < x:
            ret += 1
            i += 1
        return ret
    
    dp = defaultdict(lambda: float('inf'))
    dp[(0, 0, 0, 0)] = 0
    
    for i in range(len(a)+1):
        for j in range(len(b)+1):
            for k in range(len(c)+1):
                for p in range(2):
                    current_key = (i, j, k, p)
                    current_val = dp[current_key]
                    if current_val == float('inf'):
                        continue
                    
                    # Place V
                    if i < len(a):
                        cost = count(a, i, a[i]) + count(b, j, a[i]) + count(c, k, a[i])
                        new_key = (i+1, j, k, 1)
                        dp[new_key] = min(dp[new_key], current_val + cost)
                    
                    # Place K (only if previous was not V)
                    if j < len(b) and p == 0:
                        cost = count(a, i, b[j]) + count(b, j, b[j]) + count(c, k, b[j])
                        new_key = (i, j+1, k, 0)
                        dp[new_key] = min(dp[new_key], current_val + cost)
                    
                    # Place other characters
                    if k < len(c):
                        cost = count(a, i, c[k]) + count(b, j, c[k]) + count(c, k, c[k])
                        new_key = (i, j, k+1, 0)
                        dp[new_key] = min(dp[new_key], current_val + cost)
    
    return min(dp[(len(a), len(b), len(c), 0)], dp[(len(a), len(b), len(c), 1)])


class EbearandcompanyInteraction(BaseInteraction):
    """Ebearandcompany交互管理器"""
    
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
        score = EbearandcompanyRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ebearandcompany问题！"""
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

