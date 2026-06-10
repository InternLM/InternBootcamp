from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ckingspath.Ckingspath_reward_calculator import CkingspathRewardCalculator

# 导入依赖库
import re
import random
from collections import deque
from collections import defaultdict




class CkingspathInteraction(BaseInteraction):
    """Ckingspath交互管理器"""
    
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
        score = CkingspathRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ckingspath问题！"""
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
    def _generate_king_path(self, start, end):
        """生成国王移动的合法路径"""
        path = [start]
        x, y = start
        tx, ty = end

        while (x, y) != (tx, ty):
            dx = 0 if x == tx else (1 if tx > x else -1)
            dy = 0 if y == ty else (1 if ty > y else -1)
            x += dx
            y += dy
            path.append((x, y))
        return path

    def _merge_segments(self, path):
        """合并连续列形成线段"""
        row_dict = defaultdict(list)
        for x, y in path:
            row_dict[x].append(y)

        segments = []
        for row in row_dict:
            cols = sorted(row_dict[row])
            start = cols[0]
            for i in range(1, len(cols)):
                if cols[i] > cols[i-1] + 1:
                    segments.append([row, start, cols[i-1]])
                    start = cols[i]
            segments.append([row, start, cols[-1]])
        return segments

    def _generate_disjoint_segments(self, start, end):
        """生成隔离区域确保无解"""
        segments = []
        # 单独包裹起点
        segments.append([start[0], start[1]-1, start[1]+1])
        # 单独包裹终点（不同行）
        segments.append([end[0]+2, end[1]-1, end[1]+1])
        # 添加干扰线段
        for _ in range(random.randint(1,3)):
            r = random.randint(1, self.max_coord)
            a = random.randint(1, self.max_coord//2)
            b = random.randint(a+2, self.max_coord)
            segments.append([r, a, b])
        return segments
