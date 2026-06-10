from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.chardproblem.Chardproblem_reward_calculator import ChardproblemRewardCalculator

# 导入依赖库
import random
import string
import re




class ChardproblemInteraction(BaseInteraction):
    """Chardproblem交互管理器"""
    
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
        score = ChardproblemRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Chardproblem问题！"""
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
    def _generate_strings_with_edge_cases(self, n):
        """生成包含前缀、相同字符串等边界情况的序列"""
        strings = []
        if random.random() < 0.3:
            base = self._random_string()
            strings.append(base)
            for _ in range(n-1):
                strings.append(base + self._random_string(1))
        elif random.random() < 0.3: 
            s = self._random_string()
            strings = [s] * n
        else:
            total_length = 0
            for _ in range(n):
                max_len = min(self.max_string_length, 100000 - total_length)
                if max_len <=0:
                    s = ''
                else:
                    length = random.randint(1, max_len)
                    s = ''.join(random.choices(string.ascii_lowercase, k=length))
                    total_length += length
                strings.append(s)
        return strings

    def _random_string(self, length=None):
        """生成随机长度的字符串"""
        if length is None:
            length = random.randint(1, self.max_string_length)
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def _solve_case(self, n, c, strings):
        """动态规划求解正确结果 (完整实现)"""
        dp = [[-1] * 2 for _ in range(n)]
        dp[0][0] = 0
        dp[0][1] = c[0]
        possible = True

        for i in range(1, n):
            prev = strings[i-1]
            current = strings[i]
            prev_rev = prev[::-1]
            current_rev = current[::-1]

            dp_i0 = -1
            dp_i1 = -1

            # 处理不反转当前字符串的情况
            if dp[i-1][0] != -1 and current >= prev:
                dp_i0 = dp[i-1][0]
            if dp[i-1][1] != -1 and current >= prev_rev:
                if dp_i0 == -1 or dp[i-1][1] < dp_i0:
                    dp_i0 = dp[i-1][1]

            # 处理反转当前字符串的情况
            cost = c[i]
            if dp[i-1][0] != -1 and current_rev >= prev:
                dp_i1 = dp[i-1][0] + cost
            if dp[i-1][1] != -1 and current_rev >= prev_rev:
                candidate = dp[i-1][1] + cost
                if dp_i1 == -1 or candidate < dp_i1:
                    dp_i1 = candidate

            dp[i][0] = dp_i0
            dp[i][1] = dp_i1

            if dp[i][0] == -1 and dp[i][1] == -1:
                possible = False
                break

        if not possible:
            return -1

        final0 = dp[-1][0]
        final1 = dp[-1][1]
        if final0 == -1 and final1 == -1:
            return -1
        return min(filter(lambda x: x != -1, [final0, final1])) if final0 != -1 and final1 != -1 else max(final0, final1)
