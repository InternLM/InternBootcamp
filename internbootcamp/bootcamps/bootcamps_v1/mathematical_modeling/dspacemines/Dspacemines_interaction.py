from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.dspacemines.Dspacemines_reward_calculator import DspaceminesRewardCalculator

# 导入依赖库
import math
import random




class DspaceminesInteraction(BaseInteraction):
    """Dspacemines交互管理器"""
    
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
        score = DspaceminesRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dspacemines问题！"""
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
    def generate_random_A(self):
        return (
            random.randint(-10000, 10000),
            random.randint(-10000, 10000),
            random.randint(-10000, 10000)
        )

    def generate_random_v(self):
        while True:
            v = (random.randint(-10, 10), random.randint(-10, 10), random.randint(-10, 10))
            if any(v):
                return v

    def generate_mine(self, A, R, existing_mines):
        max_attempts = 1000
        for _ in range(max_attempts):
            # 生成随机方向和距离
            theta = random.uniform(0, math.pi)
            phi = random.uniform(0, 2*math.pi)
            dx = math.sin(theta)*math.cos(phi)
            dy = math.sin(theta)*math.sin(phi)
            dz = math.cos(theta)

            r_i = random.randint(1, R-1)
            min_dist = R + r_i + 1
            distance = random.uniform(min_dist, 2*min_dist)  # 生成适中距离

            ox = A[0] + dx*distance
            oy = A[1] + dy*distance
            oz = A[2] + dz*distance
            ox, oy, oz = int(round(ox)), int(round(oy)), int(round(oz))

            # 检查与已有地雷的间距
            valid = True
            for mine in existing_mines:
                mo = mine['O']
                mr = mine['r']
                dist_sq = (ox-mo[0])**2 + (oy-mo[1])**2 + (oz-mo[2])**2
                if dist_sq < (r_i + mr)**2:
                    valid = False
                    break
            if valid:
                return {
                    'O': [ox, oy, oz],
                    'r': r_i,
                    'm': random.randint(0, 10),
                    'spikes': [[random.randint(-10,10) for _ in range(3)] 
                              for _ in range(random.randint(0, 10))]
                }
        return None
