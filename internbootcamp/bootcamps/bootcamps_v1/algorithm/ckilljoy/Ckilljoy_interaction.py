from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ckilljoy.Ckilljoy_reward_calculator import CkilljoyRewardCalculator

# 导入依赖库
import random
import re




class CkilljoyInteraction(BaseInteraction):
    """Ckilljoy交互管理器"""
    
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
        score = CkilljoyRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ckilljoy问题！"""
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
    def _generate_case_0(self):
        n = random.randint(self.n_min, self.n_max)
        x = random.randint(*self.x_range)
        return {'n': n, 'x': x, 'a': [x]*n}

    def _generate_case_1_initial_infect(self):
        n = random.randint(self.n_min, self.n_max)
        x = random.randint(*self.x_range)
        num_infect = random.randint(1, n-1)
        a = [x]*num_infect
        remaining = n - num_infect
        for _ in range(remaining):
            while True:
                ai = random.randint(*self.a_range)
                if ai != x:
                    a.append(ai)
                    break
        random.shuffle(a)
        return {'n': n, 'x': x, 'a': a}

    def _generate_case_1_balance_sum(self):
        for _ in range(100):
            n = random.randint(self.n_min, self.n_max)
            x = random.randint(*self.x_range)
            sum_total = n * x
            a = []
            for _ in range(n-1):
                ai = random.randint(*self.a_range)
                while ai == x:
                    ai = random.randint(*self.a_range)
                a.append(ai)
            last = sum_total - sum(a)
            if last != x and self.a_range[0] <= last <= self.a_range[1]:
                a.append(last)
                return {'n': n, 'x': x, 'a': a}
        return {'n': 2, 'x': 0, 'a': [1, -1]}

    def _generate_case_2(self):
        while True:
            n = random.randint(self.n_min, self.n_max)
            x = random.randint(*self.x_range)
            a = [random.randint(*self.a_range) for _ in range(n)]
            sum_total = sum(a)
            has_x = x in a
            if not has_x and sum_total != n * x:
                return {'n': n, 'x': x, 'a': a}
