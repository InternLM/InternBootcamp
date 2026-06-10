from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cconstructatree.Cconstructatree_reward_calculator import CconstructatreeRewardCalculator

# 导入依赖库
import random
from collections import defaultdict
import re




class CconstructatreeInteraction(BaseInteraction):
    """Cconstructatree交互管理器"""
    
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
        score = CconstructatreeRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cconstructatree问题！"""
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
    def generate_solution(n, s):
        if s < 2 * n -1 or s > n * (n + 1) // 2:
            return {'possible': False}

        left = 0
        right = n - 1
        d_final = None
        answer_r = None

        while right - left > 1:
            mid = (left + right) // 2
            possible, d = Cconstructatreebootcamp.go(mid, n, s)
            if possible:
                right = mid
            else:
                left = mid

        possible, d = Cconstructatreebootcamp.go(right, n, s)
        if not possible:
            possible_left, d_left = Cconstructatreebootcamp.go(left, n, s)
            if possible_left:
                right = left
                d = d_left
            else:
                return {'possible': False}

        p_array = Cconstructatreebootcamp.construct_p(n, right, d)
        children = defaultdict(list)
        for i in range(2, n + 1):
            parent = p_array[i-2]
            children[parent].append(i)
        max_degree = max(len(v) for v in children.values()) if children else 0

        return {
            'possible': True,
            'p_array': p_array,
            'k': right,
            'max_degree': max_degree
        }

    @staticmethod
    def go(deg, n, s):
        he = 2
        curs = s
        curs -= 1  # Root node's contribution
        already = 0
        can = deg
        d = [0] * (n + 1)
        d[1] = 1  # Depth of root is 1

        for i in range(2, n + 1):
            if already == can:
                he += 1
                already = 0
                can *= deg

            remaining_nodes = n - i
            mx_term = (2 * he + remaining_nodes) * (remaining_nodes) // 2

            if curs <= he + mx_term:
                already += 1
                d[i] = he
                curs -= he
            else:
                he += 1
                d[i] = he
                curs -= he

        return curs == 0, d

    @staticmethod
    def construct_p(n, r, d):
        can = [r] * (n + 2)
        le = 1
        p = [0] * (n + 1)

        for i in range(2, n + 1):
            while le <= n and can[le] == 0:
                le += 1

            while le < i and d[le] + 1 < d[i]:
                le += 1

            p[i] = le
            can[le] -= 1

        return p[2:n+1]
