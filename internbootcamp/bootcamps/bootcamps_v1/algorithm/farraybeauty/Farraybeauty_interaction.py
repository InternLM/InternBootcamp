from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.farraybeauty.Farraybeauty_reward_calculator import FarraybeautyRewardCalculator

# 导入依赖库
import random
import re
from bisect import bisect_right

# === 源文件中的全局变量 ===

MOD = 998244353

INF = 10**18


class FarraybeautyInteraction(BaseInteraction):
    """Farraybeauty交互管理器"""
    
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
        score = FarraybeautyRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Farraybeauty问题！"""
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
    @staticmethod
    def compute_answer(n, k, original_a):
        """优化后的计算逻辑，添加了提前终止条件和范围优化"""
        if k < 2:
            return 0

        sorted_a = sorted(original_a)
        max_diff = sorted_a[-1] - sorted_a[0]
        max_x = max_diff // (k-1) if k > 1 else 0

        # 调整循环范围为实际可能的最小值
        M = min(10**5 + 5, max_x + 2) if max_x else 10**5 + 5
        a = [-INF] + sorted_a
        ans = 0

        for x in range(1, M + 1):
            if x * (k-1) > M:
                break

            # 预处理指针数组
            l = [0]*(n+1)
            for i in range(1, n+1):
                target = a[i] - x
                l[i] = bisect_right(a, target, 0, i) - 1
                l[i] = max(l[i], l[i-1])

            # 动态规划部分
            dp = [[0]*(n+1) for _ in range(k+1)]
            dp[0][0] = 1

            for i in range(k):
                prefix = [0]*(n+1)
                prefix[0] = dp[i][0]
                for j in range(1, n+1):
                    prefix[j] = (prefix[j-1] + dp[i][j]) % MOD

                for j in range(1, n+1):
                    if l[j] >= 0:
                        dp[i+1][j] = prefix[l[j]] % MOD

            res = sum(dp[k][j] for j in range(1, n+1)) % MOD
            ans = (ans + res) % MOD

        return ans
