from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bminimization.Bminimization_reward_calculator import BminimizationRewardCalculator

# 导入依赖库
import random
import re




class BminimizationInteraction(BaseInteraction):
    """Bminimization交互管理器"""
    
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
        score = BminimizationRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Bminimization问题！"""
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
    def compute_min_sum(n, k, A):
        numbers = sorted(A)
        if n == 0:
            return 0
        if k == 0:
            return numbers[-1] - numbers[0]

        adding_one = n % k
        part_length = n // k
        total_groups = k + 1

        # 构建差分数组（注意索引偏移）
        diff = []
        for i in range(n-1):
            diff.append(numbers[i+1] - numbers[i])

        # 动态规划初始化
        dp = [[0]*(k+1) for _ in range(adding_one+1)]

        # 预处理第一个分割点
        for e in range(1, k+1):
            pos = (e-1)*part_length
            if pos >= len(diff):
                val = 0
            else:
                val = diff[pos]
            dp[0][e] = dp[0][e-1] + val

        # 处理添加额外元素的分割
        for a in range(1, adding_one+1):
            for e in range(1, k+1):
                if e < a: continue
                pos = (e-1)*part_length + a
                if pos >= len(diff):
                    val = 0
                else:
                    val = diff[pos]

                if a == e:
                    dp[a][e] = dp[a-1][e-1] + val
                else:
                    dp[a][e] = max(dp[a-1][e-1], dp[a][e-1]) + val

        max_sum_diff = dp[adding_one][k]
        total_range = numbers[-1] - numbers[0]
        return total_range - max_sum_diff
