from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ctravellingsalesmanproblem.Ctravellingsalesmanproblem_reward_calculator import CtravellingsalesmanproblemRewardCalculator

# 导入依赖库
from heapq import heappush
from heapq import heappop
import random
import re




class CtravellingsalesmanproblemInteraction(BaseInteraction):
    """Ctravellingsalesmanproblem交互管理器"""
    
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
        score = CtravellingsalesmanproblemRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ctravellingsalesmanproblem问题！"""
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
    def calculate_min_cost(n, a):
        a.sort()
        to = [0] * n
        d = [float('inf')] * n
        d[0] = 0
        q = [(0, 0)]
        total_c = sum(c for _, c in a)

        # 预计算每个城市的可达范围
        for i in range(n):
            x, y = a[i]
            l, r = i, n
            while l < r:
                m = (l + r) // 2
                if a[m][0] <= x + y:
                    l = m + 1
                else:
                    r = m
            to[i] = l - 1

        # 动态规划推进
        while q:
            cost, p = heappop(q)
            if cost > d[p]:
                continue

            # 向左扩展
            if p > 0 and d[p-1] > cost:
                d[p-1] = cost
                heappush(q, (cost, p-1))

            # 向右扩展
            if to[p] < n and d[to[p]] > cost:
                d[to[p]] = cost
                heappush(q, (cost, to[p]))

            # 跳跃扩展
            if to[p] + 1 < n:
                new_cost = cost + (a[to[p]+1][0] - a[p][0] - a[p][1])
                if new_cost < d[to[p]+1]:
                    d[to[p]+1] = new_cost
                    heappush(q, (new_cost, to[p]+1))

        return total_c + d[-1]
