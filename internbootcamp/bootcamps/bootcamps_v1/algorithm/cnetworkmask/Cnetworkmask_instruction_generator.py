import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class CnetworkmaskInstructionGenerator(BaseInstructionGenerator):
    """Cnetworkmask Bootcamp指令生成器"""
    
    def __init__(self, ip_count=5, net_count=3, max_octet=255, allow_unsolvable=True):
        """
        初始化Cnetworkmask指令生成器
        
        Args:
            ip_count: 参数描述
            net_count: 参数描述
            max_octet: 参数描述
            allow_unsolvable: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.ip_count = ip_count
        self.net_count = net_count
        self.max_octet = max_octet
        self.allow_unsolvable = allow_unsolvable
    
    def case_generator(self):
        if self.allow_unsolvable and random.random() < 0.3:
            return self._gen_unsolvable_case()
        else:
            return self._gen_solvable_case()
    
    @staticmethod
    def prompt_func(question_case):
        ips = question_case['ips']
        k = question_case['k']
        ips_str = "\n".join(".".join(map(str, ip)) for ip in ips)
        prompt = f"""You are a system administrator. You have {len(ips)} distinct IP addresses. Your task is to find a valid subnet mask that groups these IPs into exactly {k} distinct networks. The subnet mask must be a valid IP address where the binary representation consists of consecutive 1's followed by consecutive 0's. If multiple masks are possible, choose the one with the fewest 1's. If impossible, output -1.

The IP addresses are:
{ips_str}

Format your answer as [answer]<subnet_mask_or_-1>[/answer]. Example:
[answer]255.255.254.0[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
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
