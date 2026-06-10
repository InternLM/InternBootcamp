from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.ftokitsukazeandstrangerectangle.Ftokitsukazeandstrangerectangle_reward_calculator import FtokitsukazeandstrangerectangleRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def calculate_answer(points):
    if not points:
        return 0
    
    # 离散化坐标
    x_coords = sorted({x for x, y in points})
    y_coords = sorted({y for x, y in points})
    
    x_map = {x: i for i, x in enumerate(x_coords)}
    y_map = {y: i for i, y in enumerate(y_coords)}
    
    # 按y分层存储x坐标
    y_buckets = [[] for _ in range(len(y_coords))]
    for x, y in points:
        y_idx = y_map[y]
        y_buckets[y_idx].append(x_map[x])
    
    for bucket in y_buckets:
        bucket.sort()
    
    total = 0
    st = SegmentTree(len(x_coords))
    
    # 按y降序处理
    for bucket in reversed(y_buckets):
        # 添加当前层的点
        for x in bucket:
            if st.query_range(x, x+1) == 0:
                st.update(x, 1)
        
        prev_x = -1
        for x in bucket:
            # 计算左区域贡献
            left = st.query_range(prev_x + 1, x + 1)
            # 计算右区域贡献（包括无穷大情况）
            right = st.query_range(x + 1, len(x_coords)) + 1
            total += left * right
            prev_x = x
    
    return total



# === 源文件中的其他类 ===

class SegmentTree:
    def __init__(self, size):
        self.m = 1
        while self.m < size:
            self.m <<= 1
        self.data = [0] * (2 * self.m)
    
    def update(self, index, value):
        index += self.m
        while index > 0:
            self.data[index] += value
            index >>= 1
    
    def query_range(self, l, r):
        res = 0
        l += self.m
        r += self.m
        while l < r:
            if l % 2 == 1:
                res += self.data[l]
                l += 1
            if r % 2 == 1:
                r -= 1
                res += self.data[r]
            l >>= 1
            r >>= 1
        return res


class FtokitsukazeandstrangerectangleInteraction(BaseInteraction):
    """Ftokitsukazeandstrangerectangle交互管理器"""
    
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
        score = FtokitsukazeandstrangerectangleRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ftokitsukazeandstrangerectangle问题！"""
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

