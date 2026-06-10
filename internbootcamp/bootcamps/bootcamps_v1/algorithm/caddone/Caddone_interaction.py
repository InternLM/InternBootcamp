from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.caddone.Caddone_reward_calculator import CaddoneRewardCalculator

# 导入依赖库
import re
import random




class CaddoneInteraction(BaseInteraction):
    """Caddone交互管理器"""
    
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
        score = CaddoneRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Caddone问题！"""
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
    @classmethod
    def _precompute_mmap(cls):
        if cls._mmap is not None:
            return
        max_m = 2 * 10**5 + 10
        cls._mmap = [0] * (max_m + 10)  # 覆盖最大可能m+9的情况

        # 初始化状态：0应用0次操作时的位数
        cnts = [0] * 10
        cnts[0] = 1

        # 预处理所有可能的操作次数
        for k in range(0, max_m + 10):
            # 当前状态的总位数即为mmap[k]
            cls._mmap[k] = sum(cnts) % cls.MOD

            # 如果未达到最大次数，准备下一层状态
            if k >= max_m:
                continue

            # 更新下一层状态
            new_cnts = [0] * 10
            for d in range(10):
                next_num = d + 1
                for digit in str(next_num):
                    new_d = int(digit)
                    new_cnts[new_d] = (new_cnts[new_d] + cnts[d]) % cls.MOD
            cnts = new_cnts
