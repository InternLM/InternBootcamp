from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cnastiaandahiddenpermutation.Cnastiaandahiddenpermutation_reward_calculator import CnastiaandahiddenpermutationRewardCalculator

# 导入依赖库
import random




class CnastiaandahiddenpermutationInteraction(BaseInteraction):
    """Cnastiaandahiddenpermutation交互管理器"""
    
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
        score = CnastiaandahiddenpermutationRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cnastiaandahiddenpermutation问题！"""
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
    def simulate_queries(self, p):
        queries = []
        n = len(p)

        def ask(t, i, j, x):
            i_index = i - 1  # Convert to 0-based
            j_index = j - 1
            pi = p[i_index]
            pj = p[j_index]
            if t == 1:
                res = max(min(x, pi), min(x + 1, pj))
            elif t == 2:
                res = min(max(x, pi), max(x + 1, pj))
            else:
                res = -1
            queries.append((t, i, j, x, res))
            return res

        a = [0] * n
        for i in range(0, n - 1, 2):
            x = ask(2, i + 1, (i + 1) + 1, 1)
            y = ask(1, i + 1, (i + 1) + 1, n - 1)

            if x == 2 and ask(1, i + 1, (i + 1) + 1, 1) == 1:
                a[i + 1] = 1
                if y == n - 1 and ask(2, i + 1, (i + 1) + 1, n - 1) == n:
                    a[i] = n
                else:
                    a[i] = y
                continue

            if y == n - 1 and ask(2, i + 1, (i + 1) + 1, n - 1) == n:
                a[i] = n
                a[i + 1] = x
                continue

            check = ask(2, (i + 1) + 1, i + 1, x)
            if check == x + 1:
                a[i] = x
                a[i + 1] = y
            else:
                a[i] = y
                a[i + 1] = x

        if n % 2 == 1:
            last = set(range(1, n + 1)) - set(a[:n-1])
            a[-1] = last.pop()

        return queries
