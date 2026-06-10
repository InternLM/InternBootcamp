from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.celections.Celections_reward_calculator import CelectionsRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict




class CelectionsInteraction(BaseInteraction):
    """Celections交互管理器"""
    
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
        score = CelectionsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Celections问题！"""
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
    @staticmethod
    def calculate_min_cost(voters):
        c0 = sum(1 for ai, _ in voters if ai == 0)
        candidate_bribes = defaultdict(list)

        # 收集贿赂成本并按候选人分组
        for ai, bi in voters:
            if ai != 0:
                candidate_bribes[ai].append(bi)

        # 对每个候选人的贿赂成本排序（降序，便于后续处理）
        for k in candidate_bribes:
            candidate_bribes[k].sort(reverse=True)

        # 预处理所有可能的贿赂方案
        all_costs = []
        total_available = 0
        for cand in candidate_bribes.values():
            all_costs.extend(cand)
            total_available += len(cand)

        # 处理无需贿赂的情况
        if not candidate_bribes:
            return 0

        # 预处理每个候选人的前缀和
        prefix_sums = {}
        for cand, costs in candidate_bribes.items():
            prefix = [0]
            s = 0
            for cost in costs:
                s += cost
                prefix.append(s)
            prefix_sums[cand] = prefix

        min_cost = float('inf')
        max_possible = c0 + total_available

        # 确定s的范围优化：s只需要到达最大候选人的当前票数+1
        max_current_votes = max(len(v) for v in candidate_bribes.values())
        s_candidates = range(max(1, max_current_votes - c0 + 1), max_possible + 1)
        if not s_candidates:
            return float('inf')

        # 计算所有可能的s值
        for s in s_candidates:
            required = s - c0
            if required <= 0:
                current_cost = 0
                if all(len(v) < s for v in candidate_bribes.values()):
                    current_cost = 0
                else:
                    continue
            else:
                total_bribes = 0
                total_obtained = 0
                remaining_costs = []

                # 第一部分：必须贿赂的选票
                for cand, costs in candidate_bribes.items():
                    needed = max(len(costs) - (s - 1), 0)
                    if needed > len(costs):
                        break
                    total_bribes += prefix_sums[cand][needed]
                    total_obtained += needed
                    remaining_costs.extend(costs[needed:])
                else:  # 正常完成循环时才执行后续逻辑
                    # 第二部分：补充需要的额外选票
                    if total_obtained >= required:
                        current_cost = total_bribes
                    else:
                        additional_needed = required - total_obtained
                        if len(remaining_costs) < additional_needed:
                            continue
                        remaining_sorted = sorted(remaining_costs)
                        current_cost = total_bribes + sum(remaining_sorted[:additional_needed])

                    if current_cost < min_cost:
                        min_cost = current_cost

        return min_cost if min_cost != float('inf') else None
