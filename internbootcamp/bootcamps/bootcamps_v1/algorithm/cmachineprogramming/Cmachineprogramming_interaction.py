from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cmachineprogramming.Cmachineprogramming_reward_calculator import CmachineprogrammingRewardCalculator

# 导入依赖库
import random
import re




class CmachineprogrammingInteraction(BaseInteraction):
    """Cmachineprogramming交互管理器"""
    
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
        score = CmachineprogrammingRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cmachineprogramming问题！"""
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
    def calculate_optimal(tasks, k):
        if not tasks:
            return 0

        sorted_tasks = sorted(tasks, key=lambda x: x['si'] + x['ti'])
        n = len(sorted_tasks)
        dp = [[0]*(k+1) for _ in range(n+1)]

        for i in range(1, n+1):
            current = sorted_tasks[i-1]
            s_i = current['si']
            end_i = s_i + current['ti']

            j = i-2
            while j >= 0 and (sorted_tasks[j]['si'] + sorted_tasks[j]['ti']) > s_i:
                j -= 1

            for m in range(1, k+1):
                include_profit = current['ci']
                if j >= 0:
                    include_profit += dp[j+1][m-1]
                dp[i][m] = max(dp[i-1][m], include_profit)

        return max(dp[n])

    @staticmethod
    def calculate_overlap(solution_tasks, k):
        timeline = []
        for task in solution_tasks:
            start = task['si']
            end = start + task['ti']
            timeline.append((start, 1))
            timeline.append((end, -1))

        timeline.sort()
        current = 0
        peak = 0
        for t, delta in timeline:
            current += delta
            peak = max(peak, current)
        return peak <= k
