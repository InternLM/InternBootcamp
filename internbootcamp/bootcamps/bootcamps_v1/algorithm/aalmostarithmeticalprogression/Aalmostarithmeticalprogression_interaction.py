from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.aalmostarithmeticalprogression.Aalmostarithmeticalprogression_reward_calculator import AalmostarithmeticalprogressionRewardCalculator

# 导入依赖库
import random
from collections import defaultdict




class AalmostarithmeticalprogressionInteraction(BaseInteraction):
    """Aalmostarithmeticalprogression交互管理器"""
    
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
        score = AalmostarithmeticalprogressionRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Aalmostarithmeticalprogression问题！"""
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
    def _generate_edge_case(self):
        """生成边界测试用例（全相同元素、交替元素等）"""
        case_type = random.choice([
            'all_same', 
            'alternating',
            'single_element'
        ])

        if case_type == 'all_same':
            n = random.randint(1, self.max_n)
            val = random.randint(self.min_val, self.max_val)
            return {
                "n": n,
                "b": [val]*n,
                "ans": n
            }

        elif case_type == 'alternating':
            n = random.randint(2, self.max_n)
            a, b = random.sample(range(self.min_val, self.max_val+1), 2)
            return {
                "n": n,
                "b": [a, b]*(n//2) + [a]*(n%2),
                "ans": n
            }

        else:  # single_element
            return {
                "n": 1,
                "b": [random.randint(self.min_val, self.max_val)],
                "ans": 1
            }

    def _generate_standard_case(self):
        """标准案例生成逻辑改进"""
        # 构造有效AAP序列
        base_len = random.randint(3, self.max_n)
        aap = self._generate_valid_aap(base_len)

        # 插入噪声元素
        noise_num = random.randint(0, self.max_n - base_len)
        b = self._insert_noise(aap, noise_num)
        random.shuffle(b)  # 保持子序列顺序但不要求连续

        return {
            "n": len(b),
            "b": b,
            "ans": self.calculate_max_aap_length(b)
        }

    def _generate_valid_aap(self, length):
        """生成符合AAP定义的基准序列"""
        p = random.randint(self.min_val, self.max_val)
        q = random.randint(1, (self.max_val - self.min_val)//2)
        sequence = [p]
        for i in range(1, length):
            sign = (-1)**(i+1)
            sequence.append(sequence[i-1] + sign * q)
        return sequence

    def _insert_noise(self, base, noise_num):
        """随机插入噪声元素"""
        for _ in range(noise_num):
            insert_pos = random.randint(0, len(base))
            base.insert(insert_pos, random.randint(self.min_val, self.max_val))
        return base

    @staticmethod
    def calculate_max_aap_length(b):
        """精确实现原题解算法"""
        n = len(b)
        if n <= 1:
            return n

        max_len = 1
        dp = defaultdict(lambda: defaultdict(int))

        for i in range(n):
            for j in range(i+1, n):
                key = (b[i], b[j] - ((-1)**(2+1)) * (b[j] - b[i]))
                dp[j][key] = max(dp[j].get(key, 0), dp[i].get(key, 1) + 1)
                max_len = max(max_len, dp[j][key])

        return max(max_len, 2 if n >=2 else 1)
