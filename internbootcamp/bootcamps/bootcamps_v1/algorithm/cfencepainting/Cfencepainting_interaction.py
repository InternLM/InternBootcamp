from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cfencepainting.Cfencepainting_reward_calculator import CfencepaintingRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict




class CfencepaintingInteraction(BaseInteraction):
    """Cfencepainting交互管理器"""
    
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
        score = CfencepaintingRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cfencepainting问题！"""
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
    def solve_case(case):
        a, b, c = case['a'], case['b'], case['c']
        n, m = case['n'], case['m']

        # 构建需要修改的位置
        required = defaultdict(list)
        for i in range(n):
            if a[i] != b[i]:
                required[b[i]].append(i)

        # 检查最后一个颜色是否有效
        last_valid = False
        if c:
            last_color = c[-1]
            if last_color in required:
                last_valid = True
            else:
                for i in range(n):
                    if b[i] == last_color:
                        last_valid = True
                        break

        if not last_valid:
            return ('NO', None)

        # 逆向构建解决方案
        solution = []
        temp_required = {k: v.copy() for k, v in required.items()}
        required_list = [(b[i], i) for i in range(n) if a[i] != b[i]]

        for color in reversed(c):
            found = False
            # 优先使用必须修改的位置
            if color in temp_required and temp_required[color]:
                plank = temp_required[color].pop()
                solution.append(plank)
                found = True
                if not temp_required[color]:
                    del temp_required[color]
            # 使用任意有效位置
            if not found:
                for i in range(n):
                    if b[i] == color:
                        solution.append(i)
                        found = True
                        break
            # 使用最后保留的位置
            if not found:
                solution.append(solution[-1] if solution else 0)

        # 检查是否所有需求都被满足
        if any(len(v) > 0 for v in temp_required.values()):
            return ('NO', None)

        # 反转并转换为1-based索引
        final_solution = [x+1 for x in reversed(solution)]
        return ('YES', final_solution)
