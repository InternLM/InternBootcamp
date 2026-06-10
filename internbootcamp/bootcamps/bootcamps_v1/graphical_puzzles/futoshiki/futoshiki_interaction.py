from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.futoshiki.futoshiki_reward_calculator import FutoshikiRewardCalculator

# 导入依赖库
import random
import re
import ast
from typing import List
from typing import Dict
from typing import Any




class FutoshikiInteraction(BaseInteraction):
    """Futoshiki交互管理器"""
    
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
        score = FutoshikiRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个futoshiki问题！"""
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
    def _generate_latin_square(self) -> List[List[int]]:
        """生成随机拉丁方阵作为解"""
        n = self.size
        base_row = list(range(1, n+1))
        random.shuffle(base_row)
        rows = [base_row[i:] + base_row[:i] for i in range(n)]
        random.shuffle(rows)
        perm = list(range(1, n+1))
        random.shuffle(perm)
        return [[perm[x-1] for x in row] for row in rows]

    def _generate_inequalities(self, solution: List[List[int]]) -> List[Dict]:
        """根据解生成不等式约束"""
        inequalities = []
        for i in range(self.size):
            for j in range(self.size):
                if j+1 < self.size and random.random() < self.inequality_prob:
                    a, b = solution[i][j], solution[i][j+1]
                    inequalities.append({
                        'cell1': [i, j],
                        'cell2': [i, j+1],
                        'symbol': '>' if a > b else '<'
                    })
                if i+1 < self.size and random.random() < self.inequality_prob:
                    a, b = solution[i][j], solution[i+1][j]
                    inequalities.append({
                        'cell1': [i, j],
                        'cell2': [i+1, j],
                        'symbol': '>' if a > b else '<'
                    })
        return inequalities

    def _generate_initial_grid(self, solution: List[List[int]]) -> List[List[int]]:
        """生成初始谜题网格"""
        n = self.size
        indices = [(i, j) for i in range(n) for j in range(n)]
        retain_num = int(len(indices) * self.retain_ratio)
        selected = random.sample(indices, retain_num)
        grid = [[0]*n for _ in range(n)]
        for i, j in selected:
            grid[i][j] = solution[i][j]
        return grid
