from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dinterestingarray.Dinterestingarray_reward_calculator import DinterestingarrayRewardCalculator

# 导入依赖库
import re
import random




class DinterestingarrayInteraction(BaseInteraction):
    """Dinterestingarray交互管理器"""
    
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
        score = DinterestingarrayRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dinterestingarray问题！"""
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
    def _generate_solvable_case(self, n, m):
        """生成必定有解的案例"""
        a = [random.randint(0, self.qi_max) for _ in range(n)]
        constraints = []
        for _ in range(m-1):
            l = random.randint(1, n)
            r = random.randint(l, n)
            current_and = a[l-1]
            for i in range(l, r):
                current_and &= a[i]
            constraints.append((l, r, current_and))

        # 添加全局约束保证解存在
        constraints.append((1, n, current_and))
        return {
            'n': n,
            'm': m,
            'constraints': constraints,
            'solution_exists': True,
            'possible_a': a
        }

    def _add_conflict_constraint(self, case):
        """添加矛盾约束"""
        # 复制原有约束
        new_constraints = case['constraints'][:]
        l, r = self._find_overlap_interval(new_constraints)

        # 生成矛盾的约束值
        original_q = new_constraints[0][2]
        conflict_q = original_q ^ (1 << random.randint(0, self.bit_width-1))

        # 添加新约束
        new_constraints.append((l, r, conflict_q))
        return {
            'n': case['n'],
            'm': case['m'] + 1,
            'constraints': new_constraints
        }

    def _find_overlap_interval(self, constraints):
        """找到多个约束的重叠区间"""
        intervals = [(l, r) for l, r, _ in constraints]
        max_l = max(l for l, _ in intervals)
        min_r = min(r for _, r in intervals)
        if max_l <= min_r:
            return (max_l, min_r)
        return (1, constraints[0][0])  # 默认返回第一个约束的区间

    def _validate_case(self, case):
        """科学校验案例有效性"""
        n = case['n']
        constraints = case['constraints']

        # 初始化各bit位的允许范围
        bit_masks = [0xFFFFFFFF for _ in range(n)]

        # 应用所有约束
        for l, r, q in constraints:
            for i in range(l-1, r):
                bit_masks[i] &= q

        # 检查所有位置是否可能
        for i in range(n):
            if bit_masks[i] == 0 and not any(
                (l-1 <= i <= r-1 and q == 0) 
                for l, r, q in constraints
            ):
                return False, None

        # 验证约束一致性
        for l, r, q in constraints:
            required_bits = q
            possible_and = 0xFFFFFFFF
            for i in range(l-1, r):
                possible_and &= bit_masks[i]
            if (possible_and & required_bits) != required_bits:
                return False, None

        # 构造可行解
        solution = [random.randint(0, mask) & mask for mask in bit_masks]
        return True, solution
