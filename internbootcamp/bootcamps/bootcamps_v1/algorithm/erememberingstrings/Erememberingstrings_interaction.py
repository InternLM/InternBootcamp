from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.erememberingstrings.Erememberingstrings_reward_calculator import ErememberingstringsRewardCalculator

# 导入依赖库
import random
import re




class ErememberingstringsInteraction(BaseInteraction):
    """Erememberingstrings交互管理器"""
    
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
        score = ErememberingstringsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Erememberingstrings问题！"""
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
    def _generate_valid_case(self, n, m):
        # 生成目标字符串：每个字符串至少有一个唯一特征位
        target_strings = []
        pos_pool = list(range(m)) * ((n // m) + 1)
        random.shuffle(pos_pool)

        for i in range(n):
            s = ['x'] * m
            unique_pos = pos_pool[i]
            # 确保该位置字符唯一
            used_chars = set()
            for ts in target_strings:
                used_chars.add(ts[unique_pos])
            while True:
                c = random.choice('abcdefghijklmnopqrstuvwxyz')
                if c not in used_chars:
                    s[unique_pos] = c
                    break
            # 其他位置随机生成
            for j in range(m):
                if j != unique_pos:
                    s[j] = random.choice('abcdefghijklmnopqrstuvwxyz')
            target_strings.append(''.join(s))

        # 构造原始字符串（通过修改目标字符串得到）
        original_strings = []
        cost_matrix = []
        for idx, target in enumerate(target_strings):
            original = list(target)
            modify_pos = random.sample(range(m), k=random.randint(0, m//2))
            costs = []
            for j in range(m):
                if j in modify_pos:
                    # 生成修改成本并改变字符
                    original[j] = random.choice('abcdefghijklmnopqrstuvwxyz'.replace(target[j], ''))
                    costs.append(random.randint(1, 1000))
                else:
                    costs.append(0)
            original_strings.append(''.join(original))
            cost_matrix.append(costs)

        return original_strings, cost_matrix

    @staticmethod
    def calculate_min_cost(n, m, strings, cost_matrix):
        INF = float('inf')
        dp = [INF] * (1 << n)
        dp[0] = 0

        for state in range(1 << n):
            if dp[state] == INF:
                continue

            # Find first unset bit
            bit = None
            for i in range(n):
                if not (state & (1 << i)):
                    bit = i
                    break
            if bit is None:
                continue

            # Try all possible positions
            for j in range(m):
                # Option 1: change current string's j-th character
                new_state = state | (1 << bit)
                cost = dp[state] + cost_matrix[bit][j]
                if dp[new_state] > cost:
                    dp[new_state] = cost

                # Option 2: group change
                same_chars = [bit]
                for k in range(n):
                    if k != bit and strings[k][j] == strings[bit][j]:
                        same_chars.append(k)

                sum_cost = sum(cost_matrix[x][j] for x in same_chars)
                max_cost = max(cost_matrix[x][j] for x in same_chars)
                total_cost = sum_cost - max_cost
                new_state_group = state
                for x in same_chars:
                    new_state_group |= (1 << x)

                if dp[new_state_group] > dp[state] + total_cost:
                    dp[new_state_group] = dp[state] + total_cost

        return dp[(1 << n) - 1]
