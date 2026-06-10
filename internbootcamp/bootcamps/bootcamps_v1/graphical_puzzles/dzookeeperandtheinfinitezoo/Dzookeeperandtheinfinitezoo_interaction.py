from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.dzookeeperandtheinfinitezoo.Dzookeeperandtheinfinitezoo_reward_calculator import DzookeeperandtheinfinitezooRewardCalculator

# 导入依赖库
import random
import re




class DzookeeperandtheinfinitezooInteraction(BaseInteraction):
    """Dzookeeperandtheinfinitezoo交互管理器"""
    
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
        score = DzookeeperandtheinfinitezooRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dzookeeperandtheinfinitezoo问题！"""
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
    def _generate_no_case(self):
        """ 专门生成NO案例的方法 """
        # 首先生成u>v的情况（40%概率）
        if random.random() < 0.4:
            v = random.randint(self.v_min, self.u_max-1)
            u = random.randint(v+1, self.u_max)
            return {'u': u, 'v': v}
        # 生成u<=v但不可达的情况（最多尝试200次）
        for _ in range(200):
            u = random.randint(self.u_min, self.u_max)
            v = random.randint(u, self.v_max)
            if not self.is_reachable(u, v):
                return {'u': u, 'v': v}
        # 最终保障机制：生成u>v的简单案例
        v = random.randint(self.v_min, self.u_max-1)
        u = random.randint(v+1, self.u_max)
        return {'u': u, 'v': v}

    @staticmethod
    def is_reachable(u, v):
        if u > v:
            return False
        x = y = 0
        for _ in range(31):
            x += u & 1
            y += v & 1
            if y > x:
                return False
            u >>= 1
            v >>= 1
        return True
