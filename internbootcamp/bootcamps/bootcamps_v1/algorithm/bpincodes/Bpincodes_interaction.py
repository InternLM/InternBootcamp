from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bpincodes.Bpincodes_reward_calculator import BpincodesRewardCalculator

# 导入依赖库
import string
import random
import itertools




class BpincodesInteraction(BaseInteraction):
    """Bpincodes交互管理器"""
    
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
        score = BpincodesRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Bpincodes问题！"""
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
    def solve_puzzle(pins):
        unique_set = set()
        modified = []
        changes = 0

        for idx, pin in enumerate(pins):
            if pin not in unique_set:
                modified.append(pin)
                unique_set.add(pin)
                continue

            # 生成所有可能的一位修改候选
            candidates = []
            for pos in range(4):
                for digit in string.digits:
                    if digit == pin[pos]:
                        continue
                    candidate = pin[:pos] + digit + pin[pos+1:]
                    if candidate not in unique_set and candidate not in pins[idx+1:]:
                        candidates.append(candidate)

            # 选择最早不冲突的候选
            for candidate in candidates:
                if candidate not in unique_set:
                    modified.append(candidate)
                    unique_set.add(candidate)
                    changes += 1
                    break
            else:
                # 回退机制：生成全新PIN
                for _ in range(1000):
                    new_pin = ''.join(random.choices(string.digits, k=4))
                    if new_pin not in unique_set and new_pin not in pins[idx+1:]:
                        modified.append(new_pin)
                        unique_set.add(new_pin)
                        changes += 1
                        break
                else:
                    raise RuntimeError("Failed to find solution")

        # 验证解决方案有效性
        assert len(modified) == len(pins), "Length mismatch"
        assert len(set(modified)) == len(pins), "Duplicate found"
        return changes, modified
