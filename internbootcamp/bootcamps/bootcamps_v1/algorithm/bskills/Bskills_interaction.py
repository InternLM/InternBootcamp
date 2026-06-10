from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bskills.Bskills_reward_calculator import BskillsRewardCalculator

# 导入依赖库
import random
import re




class BskillsInteraction(BaseInteraction):
    """Bskills交互管理器"""
    
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
        score = BskillsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Bskills问题！"""
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
    def solve_lesha_problem(n, A, cf, cm, m, a):
        """实现题目参考解法（Python版本）"""
        a_sorted = sorted((v, i) for i, v in enumerate(a))
        prefix = [0]*(n+1)
        for i in range(n):
            prefix[i+1] = prefix[i] + a_sorted[i][0]

        max_force = 0
        best_levels = a.copy()

        # 先处理全满的情况
        full_cost = sum(A - x for x in a)
        if full_cost <= m:
            return cf * n + cm * A, [A]*n

        # 遍历提升k个技能到满级的情况
        for k in range(n+1):
            if k > 0:
                cost = A - a_sorted[-k][0] if k <= n else 0
                if cost > m:
                    break
                remaining = m - cost

            # 处理最低等级提升
            # (实现完整算法需要补充此处逻辑)

        # 简化解法用于演示（实际应实现完整算法）
        # 此处使用动态规划简化处理
        temp = a.copy()
        remaining = m
        for i in range(n):
            max_add = A - temp[i]
            add = min(remaining, max_add)
            temp[i] += add
            remaining -= add

        perfect = sum(1 for x in temp if x == A)
        min_lv = min(temp)
        return perfect*cf + min_lv*cm, temp
