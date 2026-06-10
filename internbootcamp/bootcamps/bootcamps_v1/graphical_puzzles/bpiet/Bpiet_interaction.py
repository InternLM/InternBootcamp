from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.bpiet.Bpiet_reward_calculator import BpietRewardCalculator

# 导入依赖库
import re
import random
from collections import OrderedDict

# === 源文件中的全局函数 ===

def generate_valid_grid(m, k):
    """Generate valid grid with rectangular color blocks"""
    colors = [str(i) for i in range(1, 10)]
    grid = [['0'] * k for _ in range(m)]
    
    # Create main block (ensures starting point)
    grid[0][0] = random.choice(colors)
    main_color = grid[0][0]
    colors.remove(main_color)
    
    # Expand main block randomly
    max_w = 1
    while max_w < k and grid[0][max_w] == '0':
        max_w += 1
    max_h = 1
    while max_h < m and grid[max_h][0] == main_color:
        max_h += 1
    
    w = random.randint(1, max_w)
    h = random.randint(1, max_h)
    for y in range(h):
        for x in range(w):
            grid[y][x] = main_color
    
    # Add other blocks with simple shapes
    for color in colors:
        placed = False
        for _ in range(10):  # Placement attempts
            y = random.randint(0, m-1)
            x = random.randint(0, k-1)
            if grid[y][x] != '0':
                continue
                
            # Find maximum available rectangle
            max_w = 1
            while x + max_w < k and grid[y][x+max_w] == '0':
                max_w += 1
            max_h = 1
            while y + max_h < m:
                if all(c == '0' for c in grid[y+max_h][x:x+max_w]):
                    max_h += 1
                else:
                    break
            
            if max_w > 0 and max_h > 0:
                bw = random.randint(1, min(3, max_w))  # Limit block size
                bh = random.randint(1, min(3, max_h))
                for dy in range(bh):
                    for dx in range(bw):
                        grid[y+dy][x+dx] = color
                placed = True
                break
        if not placed:
            break
    
    return [''.join(row) for row in grid]

def calculate_block_bounds(grid, x, y):
    """Calculate rectangular bounds for the block containing (x,y)"""
    color = grid[y][x]
    # Horizontal expansion
    min_x = x
    while min_x > 0 and grid[y][min_x-1] == color:
        min_x -= 1
    max_x = x
    while max_x < len(grid[0])-1 and grid[y][max_x+1] == color:
        max_x += 1
    # Vertical expansion
    min_y = y
    while min_y > 0 and all(grid[min_y-1][cx] == color for cx in range(min_x, max_x+1)):
        min_y -= 1
    max_y = y
    while max_y < len(grid)-1 and all(grid[max_y+1][cx] == color for cx in range(min_x, max_x+1)):
        max_y += 1
    return (min_x, max_x, min_y, max_y)

def simulate_piet(grid, n_steps):
    if not grid or not grid[0]:
        return '0'
    
    m = len(grid)
    k = len(grid[0])
    DP = 2  # Initial direction: right
    CP = -1  # Initial chooser: left
    x, y = 0, 0
    
    state_cache = OrderedDict()
    step = 0
    
    while step < n_steps:
        # Check for cycles using LRU cache
        state = (x, y, DP, CP)
        if state in state_cache:
            cycle_start = state_cache[state]
            cycle_length = step - cycle_start
            if cycle_length > 0:
                remaining = n_steps - step
                step += (remaining // cycle_length) * cycle_length
                if step >= n_steps:
                    break
                # Reset cache after cycle skip
                state_cache.clear()
        state_cache[state] = step
        if len(state_cache) > 100:
            state_cache.popitem(last=False)
        
        # Get current block bounds
        min_x, max_x, min_y, max_y = calculate_block_bounds(grid, x, y)
        current_color = grid[y][x]
        
        # Move to DP edge using block bounds
        if DP == 0:    # Left
            x = min_x
        elif DP == 2:  # Right
            x = max_x
        elif DP == 1:  # Up
            y = min_y
        elif DP == 3:  # Down
            y = max_y
        
        # Move in CP direction using block bounds
        cp_dir = (DP + CP) % 4
        if cp_dir == 0:    # Left
            x = min_x
        elif cp_dir == 2:  # Right
            x = max_x
        elif cp_dir == 1:  # Up
            y = min_y
        elif cp_dir == 3:  # Down
            y = max_y
        
        # Attempt to move in DP direction
        new_x, new_y = x, y
        if DP == 0:    # Left
            new_x = x - 1
        elif DP == 2:  # Right
            new_x = x + 1
        elif DP == 1:  # Up
            new_y = y - 1
        elif DP == 3:  # Down
            new_y = y + 1
        
        valid = False
        if 0 <= new_x < k and 0 <= new_y < m:
            if grid[new_y][new_x] != '0':
                x, y = new_x, new_y
                valid = True
        
        if not valid:
            if CP == -1:
                CP = 1
            else:
                CP = -1
                DP = (DP + 1) % 4
        
        step += 1
    
    return grid[y][x]


class BpietInteraction(BaseInteraction):
    """Bpiet交互管理器"""
    
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
        score = BpietRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Bpiet问题！"""
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

