from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ecirclingroundtreasures.Ecirclingroundtreasures_reward_calculator import EcirclingroundtreasuresRewardCalculator

# 导入依赖库
import random
import re
from collections import deque




class EcirclingroundtreasuresInteraction(BaseInteraction):
    """Ecirclingroundtreasures交互管理器"""
    
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
        score = EcirclingroundtreasuresRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ecirclingroundtreasures问题！"""
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
    def compute_max_profit(identity):
        n, m = identity['n'], identity['m']
        grid = identity['grid']
        treasure_values = identity['treasure_values']
        sx = sy = None
        treasures = []
        bombs = []
        for i in range(n):
            for j in range(m):
                c = grid[i][j]
                if c == 'S':
                    sx, sy = i+1, j+1
                elif c.isdigit():
                    treasures.append((int(c), i+1, j+1))
                elif c == 'B':
                    bombs.append((i+1, j+1))
        treasures.sort()
        gx, gy, val = [], [], []
        for num, x, y in treasures:
            gx.append(x)
            gy.append(y)
            val.append(treasure_values[num-1])
        for x, y in bombs:
            gx.append(x)
            gy.append(y)
            val.append(-10000)
        m_objects = len(gx)
        tot = 1 << m_objects
        w = [0] * tot
        for mask in range(tot):
            total = 0
            for j in range(m_objects):
                if mask & (1 << j):
                    total += val[j]
            w[mask] = total
        INF = float('inf')
        dp = [[[INF]*tot for _ in range(m+2)] for __ in range(n+2)]
        dp[sx][sy][0] = 0
        q = deque([(sx, sy, 0)])
        max_profit = -INF
        dx = [-1, 1, 0, 0]
        dy = [0, 0, -1, 1]
        while q:
            x, y, mask = q.popleft()
            if x == sx and y == sy:
                current_profit = w[mask] - dp[x][y][mask]
                max_profit = max(max_profit, current_profit)
            for i in range(4):
                tx, ty = x + dx[i], y + dy[i]
                if tx < 1 or tx > n or ty < 1 or ty > m:
                    continue
                cell = grid[tx-1][ty-1]
                if cell not in ('.', 'S'):
                    continue
                new_mask = mask
                for j in range(m_objects):
                    nx, ny = x, y
                    obj_x, obj_y = gx[j], gy[j]
                    if nx == obj_x and ny < obj_y:
                        if tx < obj_x:
                            new_mask ^= (1 << j)
                    elif tx == obj_x and ty < obj_y:
                        if nx < obj_x:
                            new_mask ^= (1 << j)
                if dp[tx][ty][new_mask] > dp[x][y][mask] + 1:
                    dp[tx][ty][new_mask] = dp[x][y][mask] + 1
                    q.append((tx, ty, new_mask))
        return max(max_profit, 0)
