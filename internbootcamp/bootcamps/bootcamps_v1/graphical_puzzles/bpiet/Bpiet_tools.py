import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
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

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class BpietVerificationTool(BaseTool):
    """Bpiet验证工具"""
    
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        
    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例"""
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "identity": identity,
            "verification_history": [],
            "verification_count": 0
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """执行验证"""
        try:
            solution = parameters.get("solution", {})
            
            if not solution:
                return "错误: 缺少解决方案", -0.1, {}
            
            # 获取任务身份信息
            identity = self._instance_dict[instance_id]["identity"]
            
            # 使用奖励计算器验证解决方案
            score = BpietRewardCalculator.verify_score(
                model_output=json.dumps(solution), 
                identity=identity
            )
            
            # 更新实例状态
            self._instance_dict[instance_id]["verification_count"] += 1
            verification_result = {
                "solution": solution,
                "score": score,
                "timestamp": self._instance_dict[instance_id]["verification_count"]
            }
            self._instance_dict[instance_id]["verification_history"].append(verification_result)
            
            # 构建响应
            if score == 1.0:
                response = "✓ 解决方案验证成功！所有约束条件均满足。"
                reward = 1.0
            elif score > 0.0:
                response = f"⚠ 解决方案部分正确，得分: {score:.2f}/1.0"
                reward = score * 0.5
            else:
                response = f"✗ 解决方案验证失败，得分: {score:.2f}/1.0"
                reward = -0.1
            
            metrics = {
                "solution": solution,
                "verification_score": score,
                "verification_count": self._instance_dict[instance_id]["verification_count"],
                "is_correct": score == 1.0
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"BpietVerificationTool执行错误: {str(e)}")
            return f"验证执行错误: {str(e)}", -0.1, {"error": str(e)}

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        """计算累计工具奖励"""
        if instance_id not in self._instance_dict:
            return 0.0
        
        history = self._instance_dict[instance_id]["verification_history"]
        if not history:
            return 0.0
        
        # 返回最高验证分数
        max_score = max(item["score"] for item in history)
        return min(max_score, 1.0)
    
    # 其他额外方法

