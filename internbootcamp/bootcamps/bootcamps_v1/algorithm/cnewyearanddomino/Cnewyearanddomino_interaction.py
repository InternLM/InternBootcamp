from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cnewyearanddomino.Cnewyearanddomino_reward_calculator import CnewyearanddominoRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict




class CnewyearanddominoInteraction(BaseInteraction):
    """Cnewyearanddomino交互管理器"""
    
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
        score = CnewyearanddominoRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cnewyearanddomino问题！"""
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
    def compute_answer(self, grid, query):
        h, w = len(grid), len(grid[0])
        r1, c1, r2, c2 = query

        # Build prefix sums for vertical dominoes
        d1 = defaultdict(int)
        for i in range(h+1):
            for j in range(w+1):
                if i <= 1 or j == 0:
                    d1[(i, j)] = 0
                else:
                    term = 1 if (i >= 2 and 
                                grid[i-1][j-1] == '.' and 
                                grid[i-2][j-1] == '.') else 0
                    d1[(i, j)] = d1[(i-1, j)] + d1[(i, j-1)] - d1[(i-1, j-1)] + term

        # Build prefix sums for horizontal dominoes
        d2 = defaultdict(int)
        for i in range(h+1):
            for j in range(w+1):
                if j <= 1 or i == 0:
                    d2[(i, j)] = 0
                else:
                    term = 1 if (j >= 2 and 
                                grid[i-1][j-1] == '.' and 
                                grid[i-1][j-2] == '.') else 0
                    d2[(i, j)] = d2[(i-1, j)] + d2[(i, j-1)] - d2[(i-1, j-1)] + term

        # Calculate sum for vertical dominoes
        def sum_vertical(r1, c1, r2, c2):
            a = d1.get((r1-1, c1-1), 0)
            b = d1.get((r1-1, c2), 0)
            c_val = d1.get((r2, c1-1), 0)
            d_val = d1.get((r2, c2), 0)
            return d_val - b - c_val + a

        # Calculate sum for horizontal dominoes
        def sum_horizontal(r1, c1, r2, c2):
            a = d2.get((r1-1, c1-1), 0)
            b = d2.get((r1-1, c2), 0)
            c_val = d2.get((r2, c1-1), 0)
            d_val = d2.get((r2, c2), 0)
            return d_val - b - c_val + a

        total = 0
        # Vertical dominoes (need at least 2 rows)
        if r2 >= r1 + 1:
            total += sum_vertical(r1+1, c1, r2, c2)
        # Horizontal dominoes (need at least 2 columns)
        if c2 >= c1 + 1:
            total += sum_horizontal(r1, c1+1, r2, c2)

        return total
