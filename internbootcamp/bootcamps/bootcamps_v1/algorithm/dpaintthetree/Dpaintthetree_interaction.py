from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dpaintthetree.Dpaintthetree_reward_calculator import DpaintthetreeRewardCalculator

# 导入依赖库
import re
import random
from itertools import permutations
from collections import defaultdict




class DpaintthetreeInteraction(BaseInteraction):
    """Dpaintthetree交互管理器"""
    
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
        score = DpaintthetreeRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dpaintthetree问题！"""
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
    def _solve_puzzle(n, c1, c2, c3, edges):
        # 验证树结构合法性
        adj = defaultdict(list)
        degrees = defaultdict(int)
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
            degrees[u] += 1
            degrees[v] += 1

        if any(d > 2 for d in degrees.values()):
            return (-1, None)

        # 寻找路径端点
        start = next((node for node in adj if len(adj[node]) == 1), None)
        if not start:
            return (-1, None)

        # 动态规划求解
        min_cost = float('inf')
        best_pattern = []

        for pattern in permutations([0, 1, 2]):
            current = start
            prev = None
            total = 0
            color_seq = [0]*(n+1)
            color_idx = 0

            while True:
                color = pattern[color_idx%3]
                total += [c1[current-1], c2[current-1], c3[current-1]][color]
                color_seq[current] = color + 1

                # 移动到下一个节点
                next_nodes = [n for n in adj[current] if n != prev]
                if not next_nodes:
                    break
                prev = current
                current = next_nodes[0]
                color_idx += 1

            if total < min_cost:
                min_cost = total
                best_pattern = color_seq[1:]  # 去除0索引

        return (min_cost, best_pattern) if min_cost != float('inf') else (-1, None)
