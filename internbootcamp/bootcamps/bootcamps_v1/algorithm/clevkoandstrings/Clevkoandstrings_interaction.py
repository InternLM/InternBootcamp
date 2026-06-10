from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.clevkoandstrings.Clevkoandstrings_reward_calculator import ClevkoandstringsRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class ClevkoandstringsInteraction(BaseInteraction):
    """Clevkoandstrings交互管理器"""
    
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
        score = ClevkoandstringsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Clevkoandstrings问题！"""
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
    def compute_answer(n, k, s):
        if k > n*(n+1)//2 or k < 0:
            return 0
        MAX_K = 2000
        k = min(k, MAX_K)

        dp = [[0]*(MAX_K+1) for _ in range(n+1)]
        sum1 = [0]*(MAX_K+1)
        dp[n][0] = 1

        for i in range(n-1, -1, -1):
            new_sum1 = [0]*(MAX_K+1)
            for j in range(MAX_K, -1, -1):
                current = 0

                # Case 1: t[i] < s[i]
                if j <= MAX_K:
                    current += (ord(s[i]) - ord('a')) * dp[i+1][j]

                # Case 2: t[i] > s[i]
                delta = n - i
                if delta <= j <= MAX_K:
                    current += (ord('z') - ord(s[i])) * dp[i+1][j - delta]

                # Case 3: Find first differing position
                used = [False]*(n+1)
                # 处理降序
                for l in range(n-1, i, -1):
                    used[l] = True
                    cnt = (n - l) * (l - i + 1)
                    if cnt > j:
                        break
                    rem = j - cnt
                    if 0 <= rem <= MAX_K:
                        current += (ord('z') - ord(s[l])) * dp[l+1][rem]

                # 处理升序
                for l in range(i+1, n):
                    if used[l]:
                        break
                    cnt = (n - l) * (l - i + 1)
                    if cnt > j:
                        break
                    rem = j - cnt
                    if 0 <= rem <= MAX_K:
                        current += (ord('z') - ord(s[l])) * dp[l+1][rem]

                # Add sum from previous steps
                current += sum1[j]
                if j == 0:
                    current += 1  # 全匹配的情况

                dp[i][j] = current % MOD
                # 更新sum1
                new_sum1[j] = (sum1[j] + (ord(s[i]) - ord('a')) * dp[i+1][j]) % MOD

            sum1 = new_sum1

        return dp[0][k] % MOD
