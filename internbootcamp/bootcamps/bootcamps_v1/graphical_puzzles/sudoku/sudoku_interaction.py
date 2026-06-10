from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.sudoku.sudoku_reward_calculator import SudokuRewardCalculator

# 导入依赖库
import math
import random
from typing import List
from typing import Optional




class SudokuInteraction(BaseInteraction):
    """Sudoku交互管理器"""
    
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
        score = SudokuRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个sudoku问题！"""
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
    def _generate_full_sudoku(self) -> List[List[int]]:
        """生成有效完整数独的核心算法"""
        size = self.size
        region_size = self.sqrt_n
        grid = [[0]*size for _ in range(size)]

        # 填充对角线子区域
        for i in range(0, size, region_size):
            nums = list(range(1, size+1))
            random.shuffle(nums)
            for x in range(region_size):
                for y in range(region_size):
                    grid[i+x][i+y] = nums[x*region_size + y]

        # 解数独
        self._solve_sudoku(grid)
        return grid

    def _solve_sudoku(self, grid: List[List[int]]) -> bool:
        """回溯法解数独"""
        size = self.size
        region_size = self.sqrt_n
        empty = self._find_empty(grid)

        if not empty:
            return True

        row, col = empty
        for num in random.sample(range(1, size+1), size):  # 随机尝试增加多样性
            if self._is_safe(grid, row, col, num):
                grid[row][col] = num
                if self._solve_sudoku(grid):
                    return True
                grid[row][col] = 0
        return False

    def _find_empty(self, grid: List[List[int]]) -> Optional[tuple]:
        """寻找下一个空单元格"""
        for i in range(self.size):
            for j in range(self.size):
                if grid[i][j] == 0:
                    return (i, j)
        return None

    def _is_safe(self, grid: List[List[int]], row: int, col: int, num: int) -> bool:
        """检查数字是否可以安全填入"""
        size = self.size
        region_size = self.sqrt_n

        # 检查行和列
        if num in grid[row] or num in [grid[i][col] for i in range(size)]:
            return False

        # 检查子区域
        start_row, start_col = row - row%region_size, col - col%region_size
        for i in range(region_size):
            for j in range(region_size):
                if grid[start_row+i][start_col+j] == num:
                    return False
        return True

    def _dig_holes(self, grid: List[List[int]], dig_prob: float) -> List[List[int]]:
        """挖洞生成谜题（保证至少有一个解）"""
        size = self.size
        for i in range(size):
            for j in range(size):
                if random.random() < dig_prob:
                    grid[i][j] = 0
        return grid
