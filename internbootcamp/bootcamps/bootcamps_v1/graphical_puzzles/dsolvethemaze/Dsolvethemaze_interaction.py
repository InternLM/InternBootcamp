from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.dsolvethemaze.Dsolvethemaze_reward_calculator import DsolvethemazeRewardCalculator

# 导入依赖库
import random
from collections import deque

# === 源文件中的全局函数 ===

def get_adj(x, y, n_rows, m_cols):
    return [(nx, ny) for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)] 
            if 0<=(nx:=x+dx)<m_cols and 0<=(ny:=y+dy)<n_rows]

def solve_maze(n, m, original_grid):
    grid = [row.copy() for row in original_grid]
    good = set()
    bad = []
    
    # 收集所有好人坏人位置
    for y in range(n):
        for x in range(m):
            if grid[y][x] == 'G':
                good.add((y,x))
            elif grid[y][x] == 'B':
                bad.append((y,x))
    
    # 处理坏人周围的墙
    valid = True
    for y, x in bad:
        # 检查坏人是否离出口太近（曼哈顿距离）
        if (n-1 - y) + (m-1 - x) <= 1:
            valid = False
        
        # 将坏人周围的空地变为墙
        for ax, ay in get_adj(x, y, n, m):
            if grid[ay][ax] == '.':
                grid[ay][ax] = '#'
        
        if not valid: break
    
    # 提前终止条件
    if not valid:
        return "Yes" if len(good) == 0 else "No"
    
    # 出口被墙阻挡的情况
    if grid[n-1][m-1] == '#':
        return "Yes" if len(good) == 0 else "No"
    
    # BFS检查可达性
    marked = [[False]*m for _ in range(n)]
    queue = deque([(n-1, m-1)])
    marked[n-1][m-1] = True
    valid = True
    
    while queue:
        y, x = queue.popleft()
        
        # 遇到坏人直接失败
        if grid[y][x] == 'B':
            valid = False
            break
        
        # 处理相邻单元格
        for ax, ay in get_adj(x, y, n, m):
            if not marked[ay][ax] and grid[ay][ax] != '#':
                marked[ay][ax] = True
                queue.append((ay, ax))
                if (ay, ax) in good:
                    good.remove((ay, ax))
    
    return "Yes" if valid and not good else "No"


class DsolvethemazeInteraction(BaseInteraction):
    """Dsolvethemaze交互管理器"""
    
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
        score = DsolvethemazeRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dsolvethemaze问题！"""
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

