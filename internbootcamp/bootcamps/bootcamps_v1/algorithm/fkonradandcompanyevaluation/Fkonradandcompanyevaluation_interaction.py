from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.fkonradandcompanyevaluation.Fkonradandcompanyevaluation_reward_calculator import FkonradandcompanyevaluationRewardCalculator

# 导入依赖库
from collections import defaultdict
import re
import random

# === 源文件中的全局函数 ===

def compute_expected_outputs(n, m, edges, queries):
    vert = defaultdict(list)
    indeg = defaultdict(int)
    outdeg = defaultdict(int)
    
    # 修正边处理逻辑：u为较大编号的员工（初始薪金更高）
    for a, b in edges:
        u = max(a, b)
        v = min(a, b)
        vert[u].append(v)
        indeg[u] += 1
        outdeg[v] += 1
    
    ans = 0
    for i in range(1, n+1):
        ans += indeg[i] * outdeg[i]
    expected = [ans]
    
    for v in queries:
        # 移除当前节点贡献
        ans -= indeg[v] * outdeg[v]
        
        # 处理所有指向v的边（反向边）
        sons = list(vert[v])
        for son in sons:
            # 移除son节点原有贡献
            ans -= indeg[son]
            # 增加反转边后的贡献
            ans += (outdeg[son] - 1)
            
            # 调整度数
            indeg[v] -= 1
            outdeg[v] += 1
            indeg[son] += 1
            outdeg[son] -= 1
            
            # 添加反向边
            vert[son].append(v)
        
        # 清空原边
        vert[v].clear()
        # 添加新贡献
        ans += indeg[v] * outdeg[v]
        expected.append(ans)
    
    return expected


class FkonradandcompanyevaluationInteraction(BaseInteraction):
    """Fkonradandcompanyevaluation交互管理器"""
    
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
        score = FkonradandcompanyevaluationRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Fkonradandcompanyevaluation问题！"""
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

