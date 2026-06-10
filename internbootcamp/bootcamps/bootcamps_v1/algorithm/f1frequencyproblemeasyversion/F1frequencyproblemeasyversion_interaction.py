from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.f1frequencyproblemeasyversion.F1frequencyproblemeasyversion_reward_calculator import F1frequencyproblemeasyversionRewardCalculator

# 导入依赖库
from collections import defaultdict
import random
import re




class F1frequencyproblemeasyversionInteraction(BaseInteraction):
    """F1frequencyproblemeasyversion交互管理器"""
    
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
        score = F1frequencyproblemeasyversionRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个F1frequencyproblemeasyversion问题！"""
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
    def _create_multi_max_case(self, n, val1, val2):
        """创建两个最高频次相同的案例"""
        k = random.randint(1, n//2)
        arr = [val1]*k + [val2]*k
        if n > 2*k:
            arr += random.choices([val1, val2], k=n-2*k)
        random.shuffle(arr)
        return {'array': arr, 'answer': n}

    def _create_single_max_case(self, n):
        """创建存在有效子数组的案例"""
        main_val = random.randint(1, self.max_val)
        sec_val = random.choice([x for x in range(1, self.max_val+1) if x != main_val])

        # 确保存在有效子数组
        arr = [main_val]*(n-2) + [sec_val]*2
        random.shuffle(arr)
        return {'array': arr, 'answer': self._optimized_solve(arr)}

    def _optimized_solve(self, array):
        """优化后的求解算法"""
        freq = defaultdict(int)
        for num in array:
            freq[num] += 1

        # 找出前两个最高频元素
        sorted_freq = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
        if len(sorted_freq) >= 2 and sorted_freq[0][1] == sorted_freq[1][1]:
            return len(array)

        if not sorted_freq:
            return 0

        # 仅考虑前两个可能候选元素
        main_val = sorted_freq[0][0]
        candidates = [item[0] for item in sorted_freq[1:min(5, len(sorted_freq))]]
        max_len = 0

        for candidate in candidates:
            current_len = self._find_length(array, main_val, candidate)
            max_len = max(max_len, current_len)

        return max_len if max_len > 0 else 0

    def _find_length(self, arr, val1, val2):
        """优化后的子数组查找算法"""
        prefix_sum = 0
        first_occurrence = {0: -1}
        max_len = 0

        for idx, num in enumerate(arr):
            if num == val1:
                prefix_sum += 1
            elif num == val2:
                prefix_sum -= 1

            if prefix_sum in first_occurrence:
                max_len = max(max_len, idx - first_occurrence[prefix_sum])
            else:
                first_occurrence[prefix_sum] = idx

        return max_len
