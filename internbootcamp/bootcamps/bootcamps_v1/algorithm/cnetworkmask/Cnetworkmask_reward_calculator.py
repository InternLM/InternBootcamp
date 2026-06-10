import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class CnetworkmaskRewardCalculator(BaseRewardCalculator):
    """Cnetworkmask奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        if last_match == '-1':
            return '-1'
        try:
            parts = list(map(int, last_match.split('.')))
            if len(parts) != 4:
                return None
            for p in parts:
                if p < 0 or p > 255:
                    return None
            binary_str = ''.join(f'{p:08b}' for p in parts)
            if not re.match(r'^1+0+$', binary_str):
                return None
            return last_match
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        ips = identity['ips']
        k = identity['k']
        expected = compute_mask(ips, k)
        return solution == expected
    
    # 其他额外方法

