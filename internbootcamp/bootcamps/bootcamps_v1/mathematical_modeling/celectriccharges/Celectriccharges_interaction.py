from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.celectriccharges.Celectriccharges_reward_calculator import CelectricchargesRewardCalculator

# 导入依赖库
import random
import re




class CelectricchargesInteraction(BaseInteraction):
    """Celectriccharges交互管理器"""
    
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
        score = CelectricchargesRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Celectriccharges问题！"""
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
    def _compute_min_diameter(points):
        # 转换为按x排序的列表，确保与case_generator中的排序一致
        points_sorted = sorted(points, key=lambda p: (p[0], p[1]))
        n = len(points_sorted)
        if n == 0:
            return 0
        if n == 1:
            return 0

        # 预处理前缀和后缀的y的min和max
        pre_min = [0] * n
        pre_max = [0] * n
        pre_min[0] = points_sorted[0][1]
        pre_max[0] = points_sorted[0][1]
        for i in range(1, n):
            pre_min[i] = min(pre_min[i-1], points_sorted[i][1])
            pre_max[i] = max(pre_max[i-1], points_sorted[i][1])

        suf_min = [0] * n
        suf_max = [0] * n
        suf_min[-1] = points_sorted[-1][1]
        suf_max[-1] = points_sorted[-1][1]
        for i in range(n-2, -1, -1):
            suf_min[i] = min(suf_min[i+1], points_sorted[i][1])
            suf_max[i] = max(suf_max[i+1], points_sorted[i][1])

        # 辅助函数计算最大平方距离
        def max_sq_distance(electrons, protons):
            max_sq = 0
            # 电子移动到 (x,0)
            e_points = [(x, 0) for x in electrons]
            # 质子移动到 (0,y)
            p_points = [(0, y) for y in protons]
            all_points = e_points + p_points
            for i in range(len(all_points)):
                for j in range(i, len(all_points)):
                    dx = all_points[i][0] - all_points[j][0]
                    dy = all_points[i][1] - all_points[j][1]
                    sq = dx*dx + dy*dy
                    if sq > max_sq:
                        max_sq = sq
            return max_sq

        # 穷举所有可能的电子和质子的选择组合
        min_sq = float('inf')
        # 优化：对每个点，可以选择电子或质子，但n较大时穷举不适用，但此处假设n较小
        from itertools import product
        for choices in product([0, 1], repeat=n):
            electrons_x = []
            protons_y = []
            for i in range(n):
                if choices[i] == 0:
                    electrons_x.append(points_sorted[i][0])
                else:
                    protons_y.append(points_sorted[i][1])
            current_sq = max_sq_distance(electrons_x, protons_y)
            if current_sq < min_sq:
                min_sq = current_sq
        return min_sq
