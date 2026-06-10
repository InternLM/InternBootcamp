from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cnezzarandsymmetricarray.Cnezzarandsymmetricarray_reward_calculator import CnezzarandsymmetricarrayRewardCalculator

# 导入依赖库
import random




class CnezzarandsymmetricarrayInteraction(BaseInteraction):
    """Cnezzarandsymmetricarray交互管理器"""
    
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
        score = CnezzarandsymmetricarrayRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cnezzarandsymmetricarray问题！"""
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
    def _generate_valid_case(self, n):
        min_val, max_val = self.value_range
        positives = []
        while len(positives) < n:
            num = random.randint(min_val, max_val)
            if num not in positives:
                positives.append(num)

        symmetric_array = []
        for num in positives:
            symmetric_array.extend([num, -num])
        random.shuffle(symmetric_array)

        d_array = [sum(abs(num - other) for other in symmetric_array) for num in symmetric_array]
        return {'n': n, 'd': d_array}

    def _generate_robust_invalid_case(self, n, max_attempts=10):
        # 策略1：破坏有效案例的约束条件
        for _ in range(max_attempts):
            valid_case = self._generate_valid_case(n)
            d = valid_case['d'].copy()
            sorted_d = sorted(d)

            # 破坏方法1：打破配对约束
            last_pair_index = 2*n - 2
            if sorted_d[last_pair_index] == sorted_d[last_pair_index + 1]:
                sorted_d[-1] += 1
                shuffled = sorted_d.copy()
                random.shuffle(shuffled)
                if self.check_case(n, shuffled) == 'NO':
                    return {'n': n, 'd': shuffled}

            # 破坏方法2：修改数值导致余数错误
            target_index = random.choice(range(0, 2*n, 2))
            sorted_d[target_index] += 2*n
            shuffled = sorted_d.copy()
            random.shuffle(shuffled)
            if self.check_case(n, shuffled) == 'NO':
                return {'n': n, 'd': shuffled}

        # 策略2：完全随机生成直至找到无效案例
        for _ in range(max_attempts):
            random_d = [random.randint(0, 10**6) for _ in range(2*n)]
            if self.check_case(n, random_d) == 'NO':
                return {'n': n, 'd': random_d}

        # 保底策略：构造必定失败的案例
        return {'n': n, 'd': [0]*(2*n)}

    @staticmethod
    def check_case(n, d_list):
        sorted_d = sorted(d_list)
        su = 0
        current_n = n
        valid = True

        if len(sorted_d) != 2*current_n:
            return 'NO'

        while current_n > 0 and valid:
            i = 2*current_n - 1
            if i < 1 or sorted_d[i] != sorted_d[i-1]:
                valid = False
                break

            if i > 1 and sorted_d[i] == sorted_d[i-2]:
                valid = False
                break

            total = sorted_d[i] - 2*su
            if total % (2*current_n) != 0:
                valid = False
                break

            cur = total // (2*current_n)
            if cur <= 0:
                valid = False
                break

            su += cur
            current_n -= 1

        return 'YES' if valid and current_n == 0 else 'NO'
