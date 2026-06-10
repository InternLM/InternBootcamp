from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cnetworkmask.Cnetworkmask_reward_calculator import CnetworkmaskRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def compute_mask(ip_list, net_count):
    mask_elem = (128, 64, 32, 16, 8, 4, 2, 1)
    for i in range(4):
        diff = set()
        for ip in ip_list:
            diff.add(tuple(ip[:i+1]))
        if len(diff) >= net_count:
            cur_mask_block = 0
            for j in range(8):
                cur_mask_block += mask_elem[j]
                abs_diff = set()
                for ip in ip_list:
                    cip = list(ip[:i])
                    current_octet = ip[i] & cur_mask_block
                    cip.append(current_octet)
                    abs_diff.add(tuple(cip))
                current_network_count = len(abs_diff)
                if current_network_count == net_count:
                    mask_parts = ['255'] * i
                    mask_parts.append(str(cur_mask_block))
                    mask_parts.extend(['0'] * (3 - i))
                    return '.'.join(mask_parts)
                elif current_network_count > net_count:
                    return '-1'
            return '-1'
    return '-1'


class CnetworkmaskInteraction(BaseInteraction):
    """Cnetworkmask交互管理器"""
    
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
        score = CnetworkmaskRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cnetworkmask问题！"""
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
    def _gen_unsolvable_case(self):
        ips = [
            [255, random.randint(0,255), random.randint(0,255), random.randint(0,255)],
            [0,   random.randint(0,255), random.randint(0,255), random.randint(0,255)]
        ]
        while ips[0] == ips[1]:
            ips[1] = [0, random.randint(0,255), random.randint(0,255), random.randint(0,255)]
        return {
            'n': 2,
            'k': 1,
            'ips': ips
        }

    def _gen_solvable_case(self):
        mask_m = random.randint(8, 28)
        network_prefixes = set()
        while len(network_prefixes) < self.net_count:
            prefix = random.getrandbits(mask_m)
            network_prefixes.add(prefix)

        ips = []
        ips_set = set()

        # Generate unique IPs for network prefixes
        for prefix in network_prefixes:
            while True:
                new_ip = self.generate_ip(prefix, mask_m)
                ip_tuple = tuple(new_ip)
                if ip_tuple not in ips_set:
                    ips.append(new_ip)
                    ips_set.add(ip_tuple)
                    break

        # Generate remaining IPs
        remaining = self.ip_count - self.net_count
        while remaining > 0:
            prefix = random.choice(list(network_prefixes))
            new_ip = self.generate_ip(prefix, mask_m)
            ip_tuple = tuple(new_ip)
            if ip_tuple not in ips_set:
                ips.append(new_ip)
                ips_set.add(ip_tuple)
                remaining -= 1

        random.shuffle(ips)
        return {
            'n': self.ip_count,
            'k': self.net_count,
            'ips': ips
        }

    def generate_ip(self, prefix, mask_m):
        prefix_bits = bin(prefix)[2:].zfill(mask_m)
        remaining_bits = ''.join(random.choices(['0', '1'], k=32 - mask_m))
        full_bits = prefix_bits + remaining_bits
        octets = [int(full_bits[i:i+8], 2) for i in range(0, 32, 8)]
        return octets
