from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.cproblemfornazar.Cproblemfornazar_reward_calculator import CproblemfornazarRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class CproblemfornazarInteraction(BaseInteraction):
    """Cproblemfornazar交互管理器"""
    
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
        score = CproblemfornazarRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cproblemfornazar问题！"""
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
    def _find_max_stage(self):
        """动态计算最大可能的阶段数"""
        total, stage = 0, 0
        while True:
            add = 1 << stage
            if total + add > self.max_lr:
                return stage
            total += add
            stage += 1

    def _build_case_around(self, pos):
        """生成围绕特定位置的测试案例"""
        if random.choice([True, False]):
            l = max(1, pos - random.randint(0, 100))
            r = min(self.max_lr, pos + random.randint(0, 100))
        else:
            r = min(self.max_lr, pos + random.randint(0, 1000))
            l = max(1, r - random.randint(0, 1000))
        return {'l': l, 'r': r}

    def _generate_normal_case(self):
        """生成覆盖不同范围的普通案例"""
        range_type = random.choice([
            'tiny', 'small', 'medium', 'large', 'huge'
        ])

        ranges = {
            'tiny': (1, 100),
            'small': (100, 10**6),
            'medium': (10**6, 10**12),
            'large': (10**12, 10**15),
            'huge': (10**15, self.max_lr)
        }
        min_r, max_r = ranges[range_type]
        r = self._get_random_in_range(min_r, max_r)
        l = random.randint(1, r)
        return {'l': l, 'r': r}

    def _get_random_in_range(self, min_val, max_val):
        """高效生成指定范围的随机数"""
        span = max_val - min_val
        if span < 0:
            return min_val
        return min_val + random.randint(0, span)

    @staticmethod
    def _calculate_sum(x):
        sum_total = 0
        stage_size = 1  # 当前阶段元素个数
        is_odd = True    # 当前阶段奇偶性
        next_odd = 1     # 下一个奇数起始值
        next_even = 2    # 下一个偶数起始值
        remaining = x

        while remaining > 0:
            take = min(stage_size, remaining)

            if is_odd:
                start = next_odd
                end = start + 2*(take-1)
                segment_sum = take * (start + end) // 2
                next_odd = end + 2
            else:
                start = next_even
                end = start + 2*(take-1)
                segment_sum = take * (start + end) // 2
                next_even = end + 2

            sum_total = (sum_total + segment_sum) % MOD
            remaining -= take
            stage_size *= 2
            is_odd = not is_odd

        return sum_total
