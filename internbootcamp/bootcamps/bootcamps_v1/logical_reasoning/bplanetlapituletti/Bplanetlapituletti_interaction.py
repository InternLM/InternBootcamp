from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.bplanetlapituletti.Bplanetlapituletti_reward_calculator import BplanetlapitulettiRewardCalculator

# 导入依赖库
import random




class BplanetlapitulettiInteraction(BaseInteraction):
    """Bplanetlapituletti交互管理器"""
    
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
        score = BplanetlapitulettiRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Bplanetlapituletti问题！"""
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
    def _nums(cls):
        return {'0':'0','1':'1','2':'5','5':'2','8':'8'}

    @classmethod
    def _is_valid_time(cls, hh, mm, h, m):
        hh_str = f"{hh:02d}"
        mm_str = f"{mm:02d}"
        nums = cls._nums()

        # 检查原始数字有效性
        for c in hh_str + mm_str:
            if c not in nums:
                return False

        # 构建镜像时间
        try:
            mirrored_hh = int(nums[mm_str[1]] + nums[mm_str[0]])
            mirrored_mm = int(nums[hh_str[1]] + nums[hh_str[0]])
        except KeyError:
            return False

        # 验证镜像时间范围
        return 0 <= mirrored_hh < h and 0 <= mirrored_mm < m

    @classmethod
    def _find_valid_time(cls, h, m, start_time):
        current_hh, current_mm = map(int, start_time.split(':'))
        for _ in range(h * m):
            if cls._is_valid_time(current_hh, current_mm, h, m):
                return f"{current_hh:02d}:{current_mm:02d}"

            # 时间递增逻辑
            current_mm += 1
            if current_mm >= m:
                current_mm = 0
                current_hh += 1
                if current_hh >= h:
                    current_hh = 0
        return f"{current_hh:02d}:{current_mm:02d}"  # 理论上不会执行到这
