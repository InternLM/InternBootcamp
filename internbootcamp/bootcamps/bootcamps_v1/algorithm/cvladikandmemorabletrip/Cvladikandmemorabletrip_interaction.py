from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cvladikandmemorabletrip.Cvladikandmemorabletrip_reward_calculator import CvladikandmemorabletripRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def compute_max_comfort(n, a):
    # 预处理每个城市的最左和最右出现位置
    lmost = {}
    rmost = {}
    for i in range(n):
        city = a[i]
        if city not in lmost:
            lmost[city] = i
        rmost[city] = i
    
    dp = [0] * (n + 1)
    
    for i in range(n):
        dp[i+1] = dp[i]  # 默认不选当前段
        
        segment_cities = set()
        current_xor = 0
        min_l = n  # 当前段最小左边界
        valid = True
        
        # 从i往左扫描
        for j in range(i, -1, -1):
            city = a[j]
            
            # 检查该城市是否违反右边界约束
            if rmost.get(city, -1) > i:
                valid = False
                break
            
            # 更新当前段最小左边界
            min_l = min(min_l, lmost[city])
            
            # 仅当j到达当前段理论最小左边界时进行状态转移
            if j == min_l and valid:
                # 计算当前段的XOR
                if city not in segment_cities:
                    segment_cities.add(city)
                    current_xor ^= city
                
                # 状态转移
                dp[i+1] = max(dp[i+1], dp[j] + current_xor)
    
    return dp[n]


class CvladikandmemorabletripInteraction(BaseInteraction):
    """Cvladikandmemorabletrip交互管理器"""
    
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
        score = CvladikandmemorabletripRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cvladikandmemorabletrip问题！"""
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
    def _rule_description():
        return """## 规则详解
    *分段规则**：选择的各分段必须满足：若某分段包含城市x的乘客，则该城市所有乘客必须在同一分段
    *舒适度计算**：每个分段的舒适度是该段内不同城市代码的异或(XOR)值
    *目标**：选择若干不相交分段，使总舒适度最大"""
