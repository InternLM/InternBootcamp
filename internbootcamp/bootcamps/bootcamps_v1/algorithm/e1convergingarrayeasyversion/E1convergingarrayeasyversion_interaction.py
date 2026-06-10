from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.e1convergingarrayeasyversion.E1convergingarrayeasyversion_reward_calculator import E1convergingarrayeasyversionRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class E1convergingarrayeasyversionInteraction(BaseInteraction):
    """E1convergingarrayeasyversion交互管理器"""
    
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
        score = E1convergingarrayeasyversionRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个E1convergingarrayeasyversion问题！"""
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
    def _generate_simple_case(self):
        n = random.randint(2, 3)
        c = [random.randint(5, 10) for _ in range(n)]
        b = [random.randint(0, 2) for _ in range(n-1)]
        x = random.randint(-10, 0)
        return {'n':n, 'c':c, 'b':b, 'x':x}

    def _generate_zero_c_case(self):
        n = 3
        c = [0] + [random.randint(0, 5) for _ in range(n-1)]
        b = [random.randint(0, 5) for _ in range(n-1)]
        x = random.randint(-5, 0)
        return {'n':n, 'c':c, 'b':b, 'x':x}

    def _generate_max_b_case(self):
        n = random.randint(2, 4)
        c = [random.randint(50, 100) for _ in range(n)]
        b = [100] * (n-1)
        x = random.randint(-100, 0)
        return {'n':n, 'c':c, 'b':b, 'x':x}

    def _generate_negative_x_case(self):
        n = random.randint(2, 3)
        c = [random.randint(10, 100) for _ in range(n)]
        b = [random.randint(0, 10) for _ in range(n-1)]
        x = random.randint(-1000, -100)
        return {'n':n, 'c':c, 'b':b, 'x':x}

    def _validate_case(self, case):
        try:
            result = self._get_r(case['x'], case['n'], case['c'], case['b'])
            return result >= 0
        except:
            return False

    def _default_case(self):
        return {
            'n': 3,
            'c': [2, 3, 4],
            'b': [2, 1],
            'x': -1
        }

    @staticmethod
    def _check_0(x, n, b):
        d = s = 0
        for i in range(n):
            if i > 0:
                d += b[i-1]
                s += d
            if x*(i+1) + s > 0:
                return False
        return True

    @staticmethod
    def _check_1(x, n, c, b):
        sum_s = 0
        d = s = 0
        for i in range(n):
            sum_s += c[i]
            if i > 0:
                d += b[i-1]
                s += d
            if sum_s < x*(i+1) + s:
                return True
        return False

    @classmethod
    def _compute_dp(cls, x, n, c, b):
        maxN = 10210
        dp = [[0]*maxN for _ in range(n+1)]
        dp[0][0] = 1
        d = s = 0

        for i in range(n):
            if i > 0:
                d += b[i-1]
                s += d
            current_v = x*(i+1) + s
            max_c = c[i]

            # 动态规划优化
            for j in range(maxN):
                if dp[i][j] == 0:
                    continue

                min_val = max(current_v, j)
                max_val = min(j + max_c, maxN-1)

                if min_val > max_val:
                    continue

                # 批量更新区间
                dp[i+1][min_val] = (dp[i+1][min_val] + dp[i][j]) % MOD
                if max_val + 1 < maxN:
                    dp[i+1][max_val+1] = (dp[i+1][max_val+1] - dp[i][j]) % MOD

            # 前缀和优化
            prefix = 0
            for j in range(maxN):
                prefix = (prefix + dp[i+1][j]) % MOD
                dp[i+1][j] = prefix

        return sum(dp[n]) % MOD

    @classmethod
    def _get_r(cls, x, n, c, b):
        # 添加输入验证
        if any(ci < 0 for ci in c):
            raise ValueError("Invalid c array")
        if any(bi < 0 for bi in b):
            raise ValueError("Invalid b array")

        if cls._check_0(x, n, b):
            product = 1
            for ci in c:
                product = (product * (ci + 1)) % MOD
            return product
        if cls._check_1(x, n, c, b):
            return 0
        return cls._compute_dp(x, n, c, b)
