#!/usr/bin/env python3
"""
工具函数
"""

import socket
import traceback
import yaml
from pathlib import Path
from typing import Dict, List, Optional

import random
import time

try:
    import ray
    RAY_AVAILABLE = True
except ImportError:
    RAY_AVAILABLE = False


def load_tools_config(yaml_path: str) -> List[Dict]:
    """加载工具配置文件"""
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if 'tools' not in config:
            raise ValueError("配置文件中没有找到'tools'字段")
        
        return config['tools']
    except Exception as e:
        raise RuntimeError(f"加载配置文件失败: {e}")


def get_external_ip() -> str:
    """获取外网可访问的IP地址"""
    try:
        # 优先使用ray获取节点IP
        if RAY_AVAILABLE:
            try:
                return ray.util.get_node_ip_address().strip("[]")
            except:
                pass
        
        # 备用方法：通过连接外部服务器获取本地IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def is_port_available(host: str, port: int) -> bool:
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return sock.connect_ex((host, port)) != 0
    except Exception as e:
        traceback.print_exc()
        return False


def find_available_port(host: str, start_port: int, max_port: int = 65535, 
                       randomize: bool = True, max_retries: int = 50) -> int:
    """查找可用端口（改进版）
    
    Args:
        host: 主机地址
        start_port: 起始端口
        max_port: 最大端口号，默认65535
        randomize: 是否在端口范围内随机选择，默认True
        max_retries: 最大重试次数，默认50
        
    Returns:
        可用的端口号
        
    Raises:
        RuntimeError: 在指定范围内没有找到可用端口
    """
    port_range = max_port - start_port + 1 
    
    for attempt in range(max_retries):
        if randomize:
            # 随机选择端口以减少冲突
            port = start_port + random.randint(0, min(port_range - 1, 1000))
        else:
            # 顺序查找
            port = start_port + (attempt % port_range)
        
        while not is_port_available(host, port):
            port = start_port + (attempt % port_range)
            attempt += 1
            time.sleep(random.uniform(0.01, 0.1))
            if attempt >= max_retries:
                raise RuntimeError(f"在端口范围 {start_port}-{max_port} 内尝试{max_retries}次后没有找到可用端口")
        return port


def find_available_port_range(host: str, worker_id: str, base_port: int = 8000, 
                             range_size: int = 10000) -> int:
    """为特定worker_id分配端口范围内的可用端口
    
    Args:
        host: 主机地址
        worker_id: worker标识符
        base_port: 基础端口号
        range_size: 每个worker的端口范围大小
        
    Returns:
        可用的端口号
    """
    # 基于worker_id生成hash，确定该worker的端口范围
    worker_hash = hash(worker_id) % 1000  # 限制在1000个范围内
    start_port = base_port + worker_hash
    
    return find_available_port(host, start_port)


def update_tools_config_with_urls(original_yaml_path: str, server_url: str, 
                                 output_yaml_path: str, updated_tool_class: Optional[str] = None, 
                                 timeout_per_query: Optional[int] = None) -> str:
    """更新工具配置文件，添加mcp_server_url字段"""
    try:
        # 加载原始配置
        with open(original_yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 更新每个工具的配置
        for tool_config in config['tools']:
            class_name = tool_config["class_name"]
            tool_name = class_name.split(".")[-1]
            
            # 确保config字段存在
            if 'config' not in tool_config:
                tool_config['config'] = {}
            
            # 添加mcp_server_url字段 - 使用Master服务器URL + 工具名
            tool_config['config']['mcp_server_url'] = f"{server_url}/{tool_name}"
            
            # 添加timeout_per_query字段
            if timeout_per_query:
                tool_config['config']['timeout_per_query'] = timeout_per_query  

            # 如果指定了新的tool class，则更新class_name
            if updated_tool_class:
                tool_config['class_name'] = updated_tool_class
        
        # 保存更新的配置
        with open(output_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, 
                     sort_keys=False, indent=2)
        
        return output_yaml_path
    except Exception as e:
        raise RuntimeError(f"更新配置文件失败: {e}")


def extract_tool_names_from_config(tools_config: List[Dict]) -> List[str]:
    """从配置中提取工具名称"""
    tool_names = []
    for tool_config in tools_config:
        tool_name = tool_config["class_name"].split(".")[-1]
        tool_names.append(tool_name)
    return tool_names 