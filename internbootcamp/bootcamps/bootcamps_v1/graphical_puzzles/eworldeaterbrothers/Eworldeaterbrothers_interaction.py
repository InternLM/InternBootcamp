from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.eworldeaterbrothers.Eworldeaterbrothers_reward_calculator import EworldeaterbrothersRewardCalculator

# 导入依赖库
import re
from random import randint
from random import choice
from collections import defaultdict




class EworldeaterbrothersInteraction(BaseInteraction):
    """Eworldeaterbrothers交互管理器"""
    
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
        score = EworldeaterbrothersRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Eworldeaterbrothers问题！"""
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
    def _calculate_min_reversals(n, edges):
        if n <= 1:
            return 0

        # 构建双向邻接表
        h = defaultdict(list)
        edge_dict = {}
        for idx, (a, b) in enumerate(edges):
            num = idx + 1
            h[a].append({'y':b, 'v':0, 'num':num})
            h[b].append({'y':a, 'v':1, 'num':num})
            edge_dict[num] = (a, b)

        # 第一遍DFS计算层级和初始cost
        floors = [0]*(n+1)
        f = [0]*(n+1)
        stack = [(1, 0, False)]
        while stack:
            node, parent, visited = stack.pop()
            if not visited:
                floors[node] = floors[parent] + 1
                stack.append((node, parent, True))
                # 按随机顺序处理子节点（避免生成链式结构）
                children = [edge for edge in h[node] if edge['y'] != parent]
                for edge in reversed(children):
                    stack.append((edge['y'], node, False))
            else:
                f[node] = 0
                for edge in h[node]:
                    if edge['y'] != parent:
                        f[node] += f[edge['y']] + edge['v']

        min_flips = float('inf')
        processed = set()

        # 遍历所有可能的切割边
        for num in edge_dict:
            if num in processed:
                continue
            processed.add(num)

            a, b = edge_dict[num]
            # 确定父子关系
            if floors[a] > floors[b]:
                parent, child = b, a
                original_dir = 1  # 当前方向是child->parent
            else:
                parent, child = a, b
                original_dir = 0  # 当前方向是parent->child

            # 计算上半部分的最小翻转
            upper_min = f[1] - f[child] - original_dir
            stack = [(1, 0, upper_min)]
            current_min = upper_min
            while stack:
                node, father, cost = stack.pop()
                current_min = min(current_min, cost)
                for edge in h[node]:
                    if edge['y'] != father and edge['num'] != num:
                        new_cost = cost - 1 if edge['v'] else cost + 1
                        stack.append((edge['y'], node, new_cost))

            # 计算下半部分的最小翻转
            lower_min = f[child]
            stack = [(child, parent, lower_min)]
            current_lower = lower_min
            while stack:
                node, father, cost = stack.pop()
                current_lower = min(current_lower, cost)
                for edge in h[node]:
                    if edge['y'] != father and edge['num'] != num:
                        new_cost = cost - 1 if edge['v'] else cost + 1
                        stack.append((edge['y'], node, new_cost))

            min_flips = min(min_flips, current_min + current_lower)

        return min_flips if min_flips != float('inf') else 0
