from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.daliceandthedoll.Daliceandthedoll_reward_calculator import DaliceandthedollRewardCalculator

# 导入依赖库
import random
import bisect

# === 源文件中的全局函数 ===

def solve(n, m, obstacles):
    if n == 0 or m == 0:
        return "No"
    
    obstacles_x = [[-1, m] for _ in range(n)]
    obstacles_y = [[-1, n] for _ in range(m)]
    
    for x, y in obstacles:
        x0 = x - 1
        y0 = y - 1
        bisect.insort(obstacles_x[x0], y0)
        bisect.insort(obstacles_y[y0], x0)

    for row in obstacles_x:
        row.sort()
    for col in obstacles_y:
        col.sort()

    flag = 1
    traversed = 0
    turn = 1
    curr_x, curr_y = 0, -1
    lower_x, upper_x = 0, n
    lower_y, upper_y = -1, m

    while flag == 1:
        flag = 0
        if turn == 1:
            idx = bisect.bisect_right(obstacles_x[curr_x], curr_y)
            next_y = min(upper_y-1, obstacles_x[curr_x][idx]-1)
            if next_y > curr_y:
                traversed += next_y - curr_y
                flag = 1
                turn = 2
                curr_y, upper_y = next_y, next_y
        elif turn == 2:
            idx = bisect.bisect_right(obstacles_y[curr_y], curr_x)
            next_x = min(upper_x-1, obstacles_y[curr_y][idx]-1)
            if next_x > curr_x:
                traversed += next_x - curr_x
                flag = 1
                turn = 3
                curr_x, upper_x = next_x, next_x
        elif turn == 3:
            idx = bisect.bisect_right(obstacles_x[curr_x], curr_y) - 1
            next_y = max(lower_y+1, obstacles_x[curr_x][idx]+1)
            if next_y < curr_y:
                traversed += curr_y - next_y
                flag = 1
                turn = 4
                curr_y, lower_y = next_y, next_y
        else:
            idx = bisect.bisect_left(obstacles_y[curr_y], curr_x) - 1
            next_x = max(lower_x+1, obstacles_y[curr_y][idx]+1)
            if next_x < curr_x:
                traversed += curr_x - next_x
                flag = 1
                turn = 1
                curr_x, lower_x = next_x, next_x

    total_cells = n * m - len(obstacles)
    return "Yes" if traversed == total_cells else "No"


class DaliceandthedollInteraction(BaseInteraction):
    """Daliceandthedoll交互管理器"""
    
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
        score = DaliceandthedollRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Daliceandthedoll问题！"""
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

