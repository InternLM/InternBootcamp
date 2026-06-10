from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ejohnnyandgrandmaster.Ejohnnyandgrandmaster_reward_calculator import EjohnnyandgrandmasterRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def compute_min_difference(n, p, k_list):
    if p == 1:
        return (n % 2) % MOD
    
    val = defaultdict(int)
    for k in k_list:
        val[k] += 1

    v = sorted(val.keys())
    F = []
    S = []

    # 计算最大有效指数差
    lg = 0
    x = 1
    while x < 1e6 and p > 1:
        x *= p
        lg += 1

    rr = len(v) - 1
    while rr >= 0:
        current_k = v[rr]
        if val[current_k] <= 0:
            rr -= 1
            continue
        
        # 处理偶数情况
        if val[current_k] % 2 == 0:
            val[current_k] = 0
            rr -= 1
            continue
        
        # 处理奇数情况
        val[current_k] = 0
        lp = rr - 1
        while lp >= 0 and val[v[lp]] <= 0:
            lp -= 1
        
        # 没有可配对元素
        if lp < 0:
            F.append((current_k, 1))
            break
        
        # 判断指数差是否可合并
        need_steps = current_k - v[lp]
        if need_steps > lg:
            F.append((current_k, 1))
            break
        
        # 计算需要合并的数量
        need = p ** need_steps
        flag = True
        original_lp = lp
        
        # 合并操作
        while lp >= 0 and flag:
            current_lp_k = v[lp]
            
            if need > 1e6:
                flag = False
                break
            
            if val[current_lp_k] >= need:
                val[current_lp_k] -= need
                need = 0
                break
            else:
                need -= val[current_lp_k]
                val[current_lp_k] = 0
                
                if lp == 0:
                    flag = False
                    break
                
                # 计算下一级指数差
                step = current_lp_k - v[lp-1]
                if step > lg:
                    flag = False
                    break
                
                need *= p ** step
                lp -= 1
        
        if not flag or lp < 0:
            F.append((current_k, 1))
            break
        
        # 清理中间元素
        for j in range(lp + 1, original_lp + 1):
            val[v[j]] = 0
    
    # 收集剩余元素
    for k in v:
        if val[k] > 0:
            S.append((k, val[k]))
    
    # 计算最终结果
    sum_F = sum(pow(p, k, MOD) * cnt % MOD for k, cnt in F) % MOD
    sum_S = sum(pow(p, k, MOD) * cnt % MOD for k, cnt in S) % MOD
    return abs(sum_F - sum_S) % MOD


class EjohnnyandgrandmasterInteraction(BaseInteraction):
    """Ejohnnyandgrandmaster交互管理器"""
    
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
        score = EjohnnyandgrandmasterRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ejohnnyandgrandmaster问题！"""
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

