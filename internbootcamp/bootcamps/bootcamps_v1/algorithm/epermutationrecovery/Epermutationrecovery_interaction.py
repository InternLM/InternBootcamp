from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.epermutationrecovery.Epermutationrecovery_reward_calculator import EpermutationrecoveryRewardCalculator

# 导入依赖库
import random
import re
from collections import deque




class EpermutationrecoveryInteraction(BaseInteraction):
    """Epermutationrecovery交互管理器"""
    
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
        score = EpermutationrecoveryRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Epermutationrecovery问题！"""
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
    def _generate_solvable_case(self):
        n = random.randint(*self.n_range)
        p = list(range(1, n+1))
        random.shuffle(p)
        next_list = self.compute_next(p)
        masked_next = [
            x if random.random() < self.mask_prob else -1
            for x in next_list
        ]
        return {'n': n, 'next': masked_next}

    def _generate_unsolvable_case(self):
        conflict_types = [
            self._create_cycle_conflict,
            self._create_order_conflict,
            self._create_range_conflict
        ]
        for _ in range(50):
            creator = random.choice(conflict_types)
            case = creator()
            if case and not self.check_solvable(case['n'], case['next']):
                return case
        return {'n': 3, 'next': [3, 4, -1]}

    def _create_cycle_conflict(self):
        n = random.randint(3, 6)
        next_list = [-1]*n
        for i in range(n-1):
            next_list[i] = i+2  # 创建循环依赖
        next_list[-1] = 1
        return {'n': n, 'next': next_list}

    def _create_order_conflict(self):
        n = random.randint(4, 6)
        next_list = [-1]*n
        next_list[0] = n+1  # 无效的next值
        for i in range(1, n-1):
            next_list[i] = i+2
        return {'n': n, 'next': next_list}

    def _create_range_conflict(self):
        n = 5
        return {'n': n, 'next': [3, 6, 4, 6, -1]}

    @staticmethod
    def compute_next(p):
        n = len(p)
        next_arr = []
        for i in range(n):
            min_j = n + 1
            for j in range(i+1, n):
                if p[j] > p[i]:
                    min_j = j + 1
                    break
            next_arr.append(min_j)
        return next_arr

    @staticmethod
    def check_solvable(n, next_list):
        next_array = [x-1 if x != -1 else -1 for x in next_list]
        graph = [[] for _ in range(n)]
        stack = []

        # 构建图结构
        for i in range(n):
            if 0 <= next_array[i] < n:
                graph[i].append(next_array[i])

            while stack and (next_array[stack[-1]] == -1 or next_array[stack[-1]] <= i):
                stack.pop()
            if stack:
                graph[i].append(stack[-1])
            if next_array[i] != -1 and next_array[i] != n:
                stack.append(i)

        # 拓扑排序检测
        in_degree = [0]*n
        for u in range(n):
            for v in graph[u]:
                if 0 <= v < n:
                    in_degree[v] += 1

        queue = deque([u for u in range(n) if in_degree[u] == 0])
        visited = 0

        while queue:
            u = queue.popleft()
            visited += 1
            for v in graph[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        return visited == n
