from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.apbinary.Apbinary_reward_calculator import ApbinaryRewardCalculator

# 导入依赖库
import random
import re




class ApbinaryInteraction(BaseInteraction):
    """Apbinary交互管理器"""
    
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
        score = ApbinaryRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Apbinary问题！"""
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
    def _generate_edge_case(self):  # 修正：添加正确的缩进
        """生成边界测试案例"""
        edge_types = [
            {'p': 0},  # 常规二进制
            {'p': -1000, 'n': 10**9},  # 最小p值
            {'p': 1000, 'n': 1},       # 无解情况
            {'n': 1, 'p': 1},          # 样例5
            {'p': -1, 'n': 2**20 + 1}  # 大数值案例
        ]
        case = random.choice(edge_types)
        p = case.get('p', random.randint(-1000, 1000))
        n = case.get('n', random.randint(1, 10**9))
        return {'n': n, 'p': p}

    @staticmethod
    def solve(n, p):
        if p == 0:  # 优化常规二进制情况
            if (n & (n-1)) == 0:
                return 1
            return bin(n).count('1')

        max_i = 10**6 if p < 0 else min(10**6, n//abs(p)+2)
        for i in range(1, max_i+1):
            s = n - p * i
            if s <= 0:
                continue
            if s.bit_length() > 60:  # 处理极大数值溢出
                continue
            if bin(s).count('1') <= i and s >= i:
                return i
        return -1
