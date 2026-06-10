from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.ehelpingpeople.Ehelpingpeople_reward_calculator import EhelpingpeopleRewardCalculator

# 导入依赖库
import random
import re




class EhelpingpeopleInteraction(BaseInteraction):
    """Ehelpingpeople交互管理器"""
    
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
        score = EhelpingpeopleRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ehelpingpeople问题！"""
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
    def _calculate(self, n, a, recommendations):
        class Segment:
            def __init__(self, a, b, p):
                self.a = a-1  # 0-based
                self.b = b-1
                self.p = p
                self.children = []
                self.maxv = 0
                self.dist = {}

            def solve(self, values):
                # Calculate base maximum
                self.maxv = max(values[self.a:self.b+1])

                # Process children
                prev_end = self.a-1
                for child in self.children:
                    # Left gap
                    if prev_end+1 <= child.a-1:
                        self.maxv = max(self.maxv, max(values[prev_end+1:child.a]))
                    # Child's maximum (after solving)
                    child.solve(values)
                    self.maxv = max(self.maxv, child.maxv)
                    prev_end = child.b
                # Right gap
                if prev_end+1 <= self.b:
                    self.maxv = max(self.maxv, max(values[prev_end+1:self.b+1]))

                # Initialize distribution
                self.dist = {self.maxv: 1.0}

                # Merge children distributions
                for child in self.children:
                    new_dist = {}
                    for k1, p1 in self.dist.items():
                        for k2, p2 in child.dist.items():
                            key = max(k1, k2)
                            prob = p1 * p2
                            new_dist[key] = new_dist.get(key, 0.0) + prob
                    self.dist = new_dist

                # Apply current probability
                if self.p > 0:
                    new_dist = {}
                    for k, p in self.dist.items():
                        new_dist[k+1] = new_dist.get(k+1, 0.0) + p * self.p
                        new_dist[k] = new_dist.get(k, 0.0) + p * (1 - self.p)
                    self.dist = new_dist
                    self.maxv += 1

        # Build interval tree
        segs = [Segment(1, n, 0.0)] + [Segment(l, r, p) for l, r, p in recommendations]
        segs.sort(key=lambda x: (x.a, -(x.b - x.a)))

        # Build hierarchy
        stack = [segs[0]]
        for s in segs[1:]:
            while stack and not (stack[-1].a <= s.a and s.b <= stack[-1].b):
                stack.pop()
            if stack:
                stack[-1].children.append(s)
            stack.append(s)

        # Solve root
        segs[0].solve(a)
        expectation = sum(k * p for k, p in segs[0].dist.items())
        return expectation
