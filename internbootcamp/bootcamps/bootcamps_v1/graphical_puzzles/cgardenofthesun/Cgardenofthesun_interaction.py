from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.cgardenofthesun.Cgardenofthesun_reward_calculator import CgardenofthesunRewardCalculator

# 导入依赖库
import random
from collections import deque
import re




class CgardenofthesunInteraction(BaseInteraction):
    """Cgardenofthesun交互管理器"""
    
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
        score = CgardenofthesunRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cgardenofthesun问题！"""
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
    def generate_tree(self, n, m):
        """使用Prim算法生成生成树结构"""
        grid = [[False for _ in range(m)] for _ in range(n)]
        directions = [(-1,0), (0,1), (1,0), (0,-1)]

        # 随机选择起点
        start = (random.randint(0, n-1), random.randint(0, m-1))
        grid[start[0]][start[1]] = True
        frontier = []

        # 初始化边界
        for dx, dy in directions:
            nx, ny = start[0]+dx, start[1]+dy
            if 0 <= nx < n and 0 <= ny < m:
                frontier.append((nx, ny))

        while frontier:
            # 随机选择边界点
            idx = random.randint(0, len(frontier)-1)
            x, y = frontier.pop(idx)

            # 寻找相邻的已选节点
            neighbors = []
            for dx, dy in directions:
                nx, ny = x+dx, y+dy
                if 0 <= nx < n and 0 <= ny < m and grid[nx][ny]:
                    neighbors.append((nx, ny))

            if neighbors:
                # 随机选择一个邻居连接
                parent = random.choice(neighbors)
                grid[x][y] = True

                # 添加新边界
                for dx, dy in directions:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < n and 0 <= ny < m and not grid[nx][ny]:
                        if (nx, ny) not in frontier:
                            frontier.append((nx, ny))

        return grid

    def create_valid_initial_x(self, solution):
        """生成满足条件的初始X集合"""
        n, m = len(solution), len(solution[0])
        candidates = [(i,j) for i in range(n) for j in range(m) if solution[i][j]]
        initial = set()
        banned = set()

        # 随机打乱候选顺序
        random.shuffle(candidates)

        for x, y in candidates:
            # 检查8邻域是否冲突
            conflict = False
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if (x+dx, y+dy) in initial:
                        conflict = True
                        break
                if conflict:
                    break
            if not conflict:
                initial.add((x, y))
                # 将周围8格标记为禁止区
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        banned.add((x+dx, y+dy))

        return initial

    def create_initial_grid(self, n, m, initial_x):
        grid = [['.' for _ in range(m)] for _ in range(n)]
        for x, y in initial_x:
            grid[x][y] = 'X'
        return [''.join(row) for row in grid]
