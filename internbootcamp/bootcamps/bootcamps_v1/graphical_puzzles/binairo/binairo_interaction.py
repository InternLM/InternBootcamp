from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.binairo.binairo_reward_calculator import BinairoRewardCalculator

# 导入依赖库
import random
import re




class BinairoInteraction(BaseInteraction):
    """Binairo交互管理器"""
    
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
        score = BinairoRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个binairo问题！"""
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
    def generate_solution(self):
        n = self.size
        possible_rows = self.generate_all_possible_rows(n)
        random.shuffle(possible_rows)

        for _ in range(1000):
            try:
                selected = random.sample(possible_rows, n)
            except ValueError:
                continue

            if len({tuple(r) for r in selected}) != n:
                continue

            if self.check_columns(selected, n):
                return selected

        # Fallback example for 4x4
        return [
            [0, 1, 0, 1],
            [1, 0, 1, 0],
            [0, 1, 1, 0],
            [1, 0, 0, 1]
        ]

    def generate_all_possible_rows(self, n):
        return self.backtrack_row([], n, n//2, n//2)

    def backtrack_row(self, current, n, zeros, ones):
        if len(current) == n:
            return [current.copy()] if zeros == 0 and ones == 0 else []

        solutions = []
        for bit in [0, 1]:
            if (bit == 0 and zeros == 0) or (bit == 1 and ones == 0):
                continue

            if len(current) >= 2 and current[-1] == bit and current[-2] == bit:
                continue

            new_current = current.copy()
            new_current.append(bit)
            new_zeros = zeros - 1 if bit == 0 else zeros
            new_ones = ones - 1 if bit == 1 else ones
            solutions += self.backtrack_row(new_current, n, new_zeros, new_ones)

        return solutions

    def check_columns(self, grid, n):
        columns = list(zip(*grid))
        for col in columns:
            if col.count(0) != n//2 or col.count(1) != n//2:
                return False
            for i in range(len(col)-2):
                if col[i] == col[i+1] == col[i+2]:
                    return False
        return len(set(columns)) == len(columns)
