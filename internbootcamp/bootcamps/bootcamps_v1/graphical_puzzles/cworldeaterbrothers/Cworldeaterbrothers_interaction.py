from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.cworldeaterbrothers.Cworldeaterbrothers_reward_calculator import CworldeaterbrothersRewardCalculator

# 导入依赖库
import random
import re
import sys




class CworldeaterbrothersInteraction(BaseInteraction):
    """Cworldeaterbrothers交互管理器"""
    
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
        score = CworldeaterbrothersRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cworldeaterbrothers问题！"""
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
    def generate_tree(n):
        if n == 1:
            return []
        parents = [random.randint(0, i-1) for i in range(1, n)]
        edges = []
        for i in range(1, n):
            parent = parents[i-1]
            edges.append((parent, i))
        return edges

    @staticmethod
    def compute_answer(n, adj):
        if n == 1:
            return 0

        dp = [0] * n
        ans = n - 1

        def dfs1(v, p):
            for u, f in adj[v]:
                if u == p:
                    continue
                dfs1(u, v)
                dp[v] += dp[u] + (1 - f)

        dfs1(0, -1)

        def dfs2(v, p):
            for u, f in adj[v]:
                if u == p:
                    continue
                dp[u] = dp[v] + (1 if f else -1)
                dfs2(u, v)

        dfs2(0, -1)

        def dfs3(v, p):
            m1, m2 = 0, 0
            for u, f in adj[v]:
                if u == p:
                    continue
                cm1, cm2 = dfs3(u, v)
                current = cm1 + (0 if f else 1)
                if current >= m1:
                    m2 = m1
                    m1 = current
                elif current > m2:
                    m2 = current
            return (m1, m2)

        for i in range(n):
            mx1, mx2 = dfs3(i, -1)
            current_ans = dp[i] - mx1 - mx2
            ans = min(ans, current_ans)

        return ans
