from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.character_puzzles.faupontrouge.Faupontrouge_reward_calculator import FaupontrougeRewardCalculator

# 导入依赖库
import re
import math
from itertools import combinations




class FaupontrougeInteraction(BaseInteraction):
    """Faupontrouge交互管理器"""
    
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
        score = FaupontrougeRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Faupontrouge问题！"""
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
    @classmethod
    def find_in_trie(cls, nodes, idx):
        result = []
        cur = 0
        have = 0
        while True:
            have += nodes[cur].interm
            if have > idx:
                return ''.join(result)
            found = False
            for i in range(26):
                next_node = nodes[cur].nxt[i]
                if next_node == -1:
                    continue
                if have + nodes[next_node].have > idx:
                    result.append(chr(ord('a') + i))
                    cur = next_node
                    found = True
                    break
                else:
                    have += nodes[next_node].have
            if not found:
                break
        return ''.join(result)

    @classmethod
    def check_valid(cls, s, k, candidate, m):
        n = len(s)
        l = len(candidate)
        cont = [-1] * n

        # Precompute continuation points
        for i in range(n):
            pos = i
            while pos < n and pos - i < l and s[pos] == candidate[pos - i]:
                pos += 1
            if pos < n and pos - i < l and s[pos] < candidate[pos - i]:
                cont[i] = -1
            elif pos == n or pos - i == l:
                cont[i] = pos
            else:
                cont[i] = pos + 1 if pos < n else -1

        # DP table initialization
        dp = [[0]*m for _ in range(n)]
        if cont[0] != -1 and cont[0] <= n:
            end = cont[0] - 1
            if end < n:
                dp[end][0] = 1

        for i in range(n-1):
            for j in range(m):
                dp[i+1][j] = min(k, dp[i+1][j] + dp[i][j])

            if cont[i+1] == -1:
                continue

            for j in range(m-1):
                if dp[i][j] == 0:
                    continue
                next_pos = cont[i+1] - 1
                if next_pos >= n or j+1 >= m:
                    continue
                dp[next_pos][j+1] = min(k, dp[next_pos][j+1] + dp[i][j])

        return dp[n-1][m-1] >= k
