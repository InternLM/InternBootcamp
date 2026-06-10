from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.cmatrixsorting.Cmatrixsorting_reward_calculator import CmatrixsortingRewardCalculator

# 导入依赖库
import random
import re
from copy import deepcopy
from typing import List
from typing import Union




class CmatrixsortingInteraction(BaseInteraction):
    """Cmatrixsorting交互管理器"""
    
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
        score = CmatrixsortingRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cmatrixsorting问题！"""
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
    def _generate_matrix(self):
        return [[random.randint(1, self.n) for _ in range(self.m)] 
                for _ in range(self.n)]

    def _generate_sorting_columns(self):
        return random.choices(range(1, self.m+1), 
                            k=random.randint(0, self.m))

    def _apply_sorting(self, matrix, columns):
        sorted_mat = deepcopy(matrix)
        for col in columns:
            sorted_mat.sort(key=lambda row: row[col-1])
        return sorted_mat

    def _corrupt_matrix(self, A, B):  # 统一方法名称
        B_prime = deepcopy(B)
        A_rows = {tuple(row) for row in A}

        # 确保至少存在一个非法行
        for i in range(self.n):
            if tuple(B_prime[i]) not in A_rows:
                continue

            for j in range(self.m):
                for v in range(1, self.n+2):
                    new_row = list(B_prime[i])
                    new_row[j] = v
                    if tuple(new_row) not in A_rows:
                        B_prime[i] = new_row
                        return B_prime

        # 最终保护：随机生成全新行
        while True:
            new_row = [random.randint(1, self.n+1) for _ in range(self.m)]
            if tuple(new_row) not in A_rows:
                B_prime[random.randint(0, self.n-1)] = new_row
                return B_prime
