from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.galaxies.galaxies_reward_calculator import GalaxiesRewardCalculator

# 导入依赖库
import re
from ast import literal_eval
from collections import deque




class GalaxiesInteraction(BaseInteraction):
    """Galaxies交互管理器"""
    
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
        score = GalaxiesRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个galaxies问题！"""
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
    def _validate_structure(solution):
        """Validate basic solution structure"""
        if not isinstance(solution, list):
            return False
        for g in solution:
            if not isinstance(g, dict) or 'center' not in g or 'cells' not in g:
                return False
            if not isinstance(g['cells'], list) or len(g['cells']) == 0:
                return False
        return True

    @staticmethod
    def _check_centers(solution, expected_centers):
        """Verify all expected centers are present"""
        solution_centers = {tuple(g['center']) for g in solution}
        expected_set = {tuple(c) for c in expected_centers}
        return solution_centers == expected_set

    @staticmethod
    def _check_coverage(solution, rows, cols):
        """Verify complete grid coverage without overlaps"""
        all_cells = []
        for g in solution:
            all_cells.extend(map(tuple, g['cells']))
        expected = {(r, c) for r in range(rows) for c in range(cols)}
        return len(all_cells) == len(expected) and set(all_cells) == expected

    @classmethod
    def _validate_galaxy(cls, galaxy):
        """Validate individual galaxy constraints"""
        cells = [tuple(c) for c in galaxy['cells']]
        center = tuple(galaxy['center'])

        # Check center presence
        if center not in cells:
            return False

        # Check symmetry
        cx, cy = center
        for (x, y) in cells:
            sym = (2*cx - x, 2*cy - y)
            if sym not in cells:
                return False

        # Check connectivity
        return cls._is_connected(cells)

    @staticmethod
    def _is_connected(cells):
        """BFS check for region connectivity"""
        if not cells:
            return False

        visited = set()
        q = deque([cells[0]])
        visited.add(cells[0])

        while q:
            x, y = q.popleft()
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                neighbor = (x+dx, y+dy)
                if neighbor in cells and neighbor not in visited:
                    visited.add(neighbor)
                    q.append(neighbor)

        return len(visited) == len(cells)
