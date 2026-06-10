#!/usr/bin/env python3
"""
分布式工具服务器命令行界面

支持Master和Worker在不同机器上部署，Worker可以动态注册到Master。

使用方法:
1. 启动Master服务器：
   python cli.py --mode master --tools_yaml_path config.yaml --port 8000

2. 在其他机器上启动Worker：
   python cli.py --mode worker --tools_yaml_path config.yaml --master_url http://master_ip:8000 --port 8001 --num_workers 3

3. 启动统一服务器（单机模式）：
   python cli.py --mode unified --tools_yaml_path config.yaml --port 8000 --num_workers 5
"""

import argparse
import json
import jsonlines
import multiprocessing
import os
import re
import signal
import socket
import sys
import time
import uuid
import yaml
import random
from datetime import datetime
from pathlib import Path

import requests

from .master_server import DistributedMasterServer
from .worker_server import DistributedWorkerServer
from .utils import (
    load_tools_config, 
    get_external_ip, 
    find_available_port, 
    update_tools_config_with_urls
)


def sanitize_log_message(message: str) -> str:
    """
    过滤日志中的 base64 图片数据，避免超长 image_url 写入日志。
    """
    if not isinstance(message, str):
        message = str(message)

    message = re.sub(
        r'(data:image/[a-zA-Z0-9.+-]+;base64,)[A-Za-z0-9+/=]+',
        r'\1[BASE64_IMAGE_OMITTED]',
        message
    )
    return message


def redirect_output_to_log(log_file_path, process_name):
    """重定向stdout和stderr到日志文件，并过滤超长base64图片数据"""
    if log_file_path:
        try:
            log_file = open(log_file_path, 'a', encoding='utf-8')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_file.write(f"[{timestamp}] === {process_name} 进程启动 ===\n")
            log_file.flush()

            class SanitizedWriter:
                def __init__(self, file_obj):
                    self.file_obj = file_obj

                def write(self, data):
                    if data:
                        data = sanitize_log_message(data)
                        self.file_obj.write(data)
                        self.file_obj.flush()

                def flush(self):
                    self.file_obj.flush()

            sys.stdout = SanitizedWriter(log_file)
            sys.stderr = SanitizedWriter(log_file)

        except Exception as e:
            print(f"警告：无法重定向日志到 {log_file_path}: {e}")


def start_master_process(tools_config, host, port, log_file=None, zombie_instance_timeout=300):
    """在子进程中启动Master服务器"""
    # 重定向输出到日志文件
    redirect_output_to_log(log_file, f"Master-{host}:{port}")
    
    master = DistributedMasterServer(host, port, tools_config, log_file=log_file, zombie_instance_timeout=zombie_instance_timeout)
    master.run()


def start_worker_process(tools_config, host, port, worker_id, master_url, log_file=None):
    """在子进程中启动Worker服务器"""
    # 设置无缓冲输出
    sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
    sys.stderr.reconfigure(line_buffering=True) if hasattr(sys.stderr, 'reconfigure') else None
    
    # 重定向输出到日志文件（如果指定）
    if log_file:
        redirect_output_to_log(log_file, f"Worker-{worker_id}")
    else:
        # 如果没有指定日志文件，创建一个临时日志文件
        temp_log_file = f"/tmp/worker_{worker_id}.log"
        try:
            # 确保日志目录存在
            os.makedirs(os.path.dirname(temp_log_file), exist_ok=True)
            # 创建日志文件
            with open(temp_log_file, 'w') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] Worker {worker_id} 子进程启动\n")
            
            # 重定向到该日志文件，同时输出到控制台
            class TeeOutput:
                def __init__(self, *files):
                    self.files = files

                def write(self, data):
                    if data:
                        data = sanitize_log_message(data)
                        for f in self.files:
                            f.write(data)
                            f.flush()

                def flush(self):
                    for f in self.files:
                        f.flush()
            
            log_file_obj = open(temp_log_file, 'a', buffering=1)  # 行缓冲
            sys.stdout = TeeOutput(sys.__stdout__, log_file_obj)
            sys.stderr = TeeOutput(sys.__stderr__, log_file_obj)
            
            print(f"📝 Worker {worker_id} 日志: {temp_log_file}")
        except Exception as e:
            print(f"⚠️  无法创建日志文件 {temp_log_file}: {e}")
    
    worker = DistributedWorkerServer(tools_config, host, port, worker_id, master_url, log_file=log_file)
    worker.run()


def create_merged_yaml_from_bootcamp_registry(bootcamp_registry_path, output_yaml_path):
    """
    从bootcamp注册表创建合并的工具配置yaml文件
    
    Args:
        bootcamp_registry_path: bootcamp注册表文件路径(.jsonl格式)
        output_yaml_path: 输出的合并yaml文件路径
        
    Returns:
        str: 创建的合并yaml文件路径
    """
    if not os.path.exists(bootcamp_registry_path):
        raise FileNotFoundError(f"Bootcamp注册表文件不存在: {bootcamp_registry_path}")
    
    merged_tools = []
    
    try:
        with jsonlines.open(bootcamp_registry_path, 'r') as reader:
            for entry in reader:
                yaml_tool_path = entry.get('yaml_tool_path')
                if not yaml_tool_path:
                    print(f"⚠️  警告: 注册表条目缺少yaml_tool_path字段: {entry}")
                    continue
                
                # # 处理相对路径 - 相对于注册表文件的目录
                # if not os.path.isabs(yaml_tool_path):
                #     registry_dir = os.path.dirname(bootcamp_registry_path)
                #     yaml_tool_path = os.path.join(registry_dir, yaml_tool_path)
                
                if not os.path.exists(yaml_tool_path):
                    print(f"⚠️  警告: 工具配置文件不存在: {yaml_tool_path}")
                    raise FileNotFoundError(f"工具配置文件不存在: {yaml_tool_path}")
                
                # 加载yaml文件中的tools配置
                try:
                    with open(yaml_tool_path, 'r', encoding='utf-8') as f:
                        yaml_config = yaml.safe_load(f)
                    
                    tools = yaml_config.get('tools', [])
                    if tools:
                        merged_tools.extend(tools)
                        print(f"✅ 从 {yaml_tool_path} 加载了 {len(tools)} 个工具")
                    else:
                        print(f"⚠️  警告: {yaml_tool_path} 中没有找到tools配置")
                        
                except Exception as e:
                    print(f"❌ 加载工具配置文件失败: {yaml_tool_path}, 错误: {e}")
                    continue
    
    except Exception as e:
        raise RuntimeError(f"读取bootcamp注册表失败: {e}")
    
    # 创建合并的yaml文件
    merged_yaml_content = {'tools': merged_tools}
    os.makedirs(os.path.dirname(output_yaml_path), exist_ok=True)
    with open(output_yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(merged_yaml_content, f, default_flow_style=False, allow_unicode=True)
    
    print(f"📋 总共从bootcamp注册表加载了 {len(merged_tools)} 个工具配置")
    print(f"📝 已创建合并的工具配置文件: {output_yaml_path}")
    return output_yaml_path


def start_multiple_workers(tools_config, host, start_port, master_url, num_workers, log_file=None):
    """启动多个Worker进程"""
    worker_processes = []
    worker_urls = []
    current_port = start_port
    
    print(f"--- 启动 {num_workers} 个Worker进程 ---")
    
    for i in range(num_workers):
        worker_port = current_port
        # Generate a random short id for the worker
        worker_id = f"{uuid.uuid4().hex[:8]}"
        worker_url = f"http://{get_external_ip()}:{worker_port}"
        worker_urls.append(worker_url)
        
        process = multiprocessing.Process(
            target=start_worker_process, 
            args=(tools_config, host, worker_port, worker_id, master_url, log_file)
        )
        process.start()
        worker_processes.append(process)
        current_port = worker_port + 1
    
    return worker_processes, worker_urls


def test_servers(server_url, tool_names, test_timeout=10, connectivity_only=False):
    """测试服务器功能"""
    print(f"🧪 测试服务器: {server_url}")
    
    try:
        # 基础连通性测试
        print(f"🔍 测试Master连通性: {server_url}/health")
        response = requests.get(f"{server_url}/health", timeout=test_timeout)
        if response.status_code == 200:
            data = response.json()
            print("  ✅ Master健康检查通过")
            print(f"    - 支持工具: {data.get('tools', [])}")
            print(f"    - 注册Worker数: {data.get('registered_workers', 0)}")
            print(f"    - 活跃Worker数: {len([w for w in data.get('workers', {}).values() if w.get('status') == 'alive'])}")
            
            if not connectivity_only:
                # 详细端点测试
                print(f"\n🧪 测试工具端点...")
                
                for tool_name in tool_names:
                    print(f"\n--- 测试工具: {tool_name} ---")
                    success = True
                    
                    # 测试创建端点
                    try:
                        create_url = f"{server_url}/{tool_name}/create"
                        test_data = {"instance_id": f"test_instance_{tool_name}", "identity": {"test": True}}
                        response = requests.post(create_url, json=test_data, timeout=test_timeout)
                        if response.status_code == 200 and response.json().get("success"):
                            print(f"  ✅ 创建端点测试通过: {create_url}")
                        else:
                            print(f"  ❌ 创建端点测试失败: 状态码 {response.status_code}")
                            success = False
                    except Exception as e:
                        print(f"  ❌ 创建端点请求失败: {e}")
                        success = False

                    # 测试执行端点
                    try:
                        execute_url = f"{server_url}/{tool_name}/execute"
                        test_data = {"instance_id": f"test_instance_{tool_name}", "test_param": "value"}
                        response = requests.post(execute_url, json=test_data, timeout=test_timeout)
                        if response.status_code == 200:
                            print(f"  ✅ 执行端点测试通过: {execute_url}")
                        else:
                            print(f"  ❌ 执行端点测试失败: 状态码 {response.status_code}")
                            success = False
                    except Exception as e:
                        print(f"  ❌ 执行端点请求失败: {e}")
                        success = False

                    # 测试释放端点
                    try:
                        release_url = f"{server_url}/{tool_name}/release"
                        test_data = {"instance_id": f"test_instance_{tool_name}"}
                        response = requests.post(release_url, json=test_data, timeout=test_timeout)
                        if response.status_code == 200 and response.json().get("success"):
                            print(f"  ✅ 释放端点测试通过: {release_url}")
                        else:
                            print(f"  ⚠️  释放端点测试失败: 状态码 {response.status_code}")
                    except Exception as e:
                        print(f"  ⚠️  释放端点请求失败: {e}")
                    
                    status = "✅ 通过" if success else "❌ 失败"
                    print(f"  工具 {tool_name}: {status}")
            
            print("🎉 服务器测试完成！")
        else:
            print(f"  ❌ Master健康检查失败: 状态码 {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ 服务器测试失败: {e}")


def log_message(message: str, log_path=None):
    """记录日志消息到文件和控制台，并过滤base64图片数据"""
    sanitized_message = sanitize_log_message(message)
    log_line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {sanitized_message}"
    if log_path:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    print(log_line)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="分布式Master-Worker服务器架构",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:

1. 启动Master服务器 (动态工具发现):
   python cli.py --mode master --port 8000

2. 启动Master服务器 (预配置工具):
   python cli.py --mode master --tools_yaml_path config.yaml --port 8000

3. 在其他机器上启动Worker:
   python cli.py --mode worker --tools_yaml_path config.yaml --master_url http://master_ip:8000 --port 8001 --num_workers 3

4. 启动统一服务器（单机Master+多Worker模式）:
   python cli.py --mode unified --tools_yaml_path config.yaml --port 8000 --num_workers 8
   python cli.py --mode unified --tools_yaml_path config.yaml --port 8000 --keep_running --num_workers 8
   python cli.py --mode unified --tools_yaml_path config.yaml --port 8000 --test_servers --keep_running --timeout_per_query 600 --num_workers 5
        """
    )
    
    parser.add_argument(
        "--mode", 
        choices=["master", "worker", "unified"],
        required=True,
        help="运行模式: master(Master服务器), worker(Worker服务器), unified(统一服务器)"
    )
    parser.add_argument(
        "--tools_yaml_path", 
        required=False,
        help="工具配置YAML文件路径"
    )
    parser.add_argument(
        "--bootcamp_registry",
        required=False,
        help="bootcamp注册表，提供后可将注册表里所有bootcamp的tool挂载到woker server"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=None,
        help="服务器端口号 (默认: 随机分配可用端口)"
    )
    parser.add_argument(
        "--host", 
        default="0.0.0.0",
        help="服务器主机地址 (默认: 0.0.0.0)"
    )
    parser.add_argument(
        "--master_url", 
        help="Master服务器URL (Worker模式必需)"
    )
    parser.add_argument(
        "--worker_id", 
        help="Worker ID (Worker模式使用，默认自动生成)"
    )
    parser.add_argument(
        "--output_dir", 
        default=None,
        help="输出目录 (默认: 与输入配置文件同目录)"
    )
    parser.add_argument(
        "--updated_tool_class", 
        default="internbootcamp.src.base_mcp_tool.BaseMCPTool",
        help="更新后的tool class名称 (默认: internbootcamp.src.base_mcp_tool.BaseMCPTool)"
    )
    parser.add_argument(
        "--timeout_per_query",
        type=int,
        default=600,
        help="每个查询的超时时间(秒) (默认: 600)"
    )
    parser.add_argument(
        "--num_workers", 
        type=int,
        default=1,
        help="Worker服务器数量 (默认: 3) - Worker和unified模式使用"
    )
    # unified模式参数
    parser.add_argument(
        "--keep_running", 
        action="store_true",
        help="保持服务器运行 (默认: 创建后立即退出) - unified模式使用"
    )
    parser.add_argument(
        "--log_dir", 
        default=None,
        help="日志目录路径，用于保存服务器日志 (默认: 不记录日志) - unified模式使用"
    )
    parser.add_argument(
        "--test_servers", 
        action="store_true",
        help="启动后测试所有服务器 (默认: 不测试) - unified模式使用"
    )
    parser.add_argument(
        "--test_timeout", 
        type=int,
        default=10,
        help="测试超时时间(秒) (默认: 10) - unified模式使用"
    )
    parser.add_argument(
        "--connectivity_only", 
        action="store_true",
        help="仅测试连通性，不测试具体端点 (默认: 测试所有功能) - unified模式使用"
    )
    parser.add_argument(
        "--zombie_instance_timeout",
        type=int,
        default=600,
        help="僵尸实例超时时间(秒) - 实例空闲超过此时间将被自动清理 (默认: 600秒) - master和unified模式使用"
    )
    
    args = parser.parse_args()

    # 如果未指定端口，随机分配一个可用端口
    if args.port is None:
        args.port = find_available_port("0.0.0.0", 49152)
        print(f"🔌 未指定端口，自动分配可用端口: {args.port}")
    
    # 验证输入文件
    if not args.bootcamp_registry and not args.tools_yaml_path and args.mode != "master":
        print("❌ 错误: Worker和Unified模式必须指定 --tools_yaml_path 或 --bootcamp_registry 其中之一")
        sys.exit(1)
    
    if args.bootcamp_registry and not os.path.exists(args.bootcamp_registry):
        print(f"❌ 错误: bootcamp注册表文件不存在: {args.bootcamp_registry}")
        sys.exit(1)
        
    if args.tools_yaml_path and not os.path.exists(args.tools_yaml_path):
        print(f"❌ 错误: 工具配置文件不存在: {args.tools_yaml_path}")
        sys.exit(1)
    
    # 验证Worker模式参数
    if args.mode == "worker" and not args.master_url:
        print("❌ 错误: Worker模式必须指定 --master_url")
        sys.exit(1)
    
    temp_yaml_file = None  # 用于跟踪需要清理的临时文件
    try:
        # 加载工具配置
        tools_config = []
        if args.bootcamp_registry:
            print(f"📖 从bootcamp注册表合并工具配置: {args.bootcamp_registry}")
            # 创建临时合并yaml文件
            temp_yaml_path = os.path.join(os.path.dirname(args.bootcamp_registry), "merged_tools_temp.yaml")
            args.tools_yaml_path = create_merged_yaml_from_bootcamp_registry(args.bootcamp_registry, temp_yaml_path)
            temp_yaml_file = temp_yaml_path
            
        if args.tools_yaml_path:
            print(f"📖 加载工具配置: {args.tools_yaml_path}")
            tools_config = load_tools_config(args.tools_yaml_path)
            print(f"找到 {len(tools_config)} 个工具配置")
        elif args.mode == "master":
            print("📖 Master模式: 未提供工具配置，将使用动态工具发现")
        else:
            # 这种情况应该在前面的验证中被拦截
            raise ValueError("Worker和Unified模式必须提供工具配置")
        
        # 信号处理
        def signal_handler(signum, frame):
            print(f"\n收到信号 {signum}，正在退出...")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if args.mode == "master":
            # 启动Master服务器
            print(f"\n🚀 启动分布式Master服务器...")
            server = DistributedMasterServer(
                args.host, 
                args.port, 
                tools_config if tools_config else None,
                zombie_instance_timeout=args.zombie_instance_timeout
            )
            
            master_url = f"http://{get_external_ip()}:{args.port}"
            
            # 创建输出配置文件（仅当有工具配置时）
            if args.tools_yaml_path:
                if args.output_dir is None:
                    args.output_dir = os.path.dirname(args.tools_yaml_path)
                os.makedirs(args.output_dir, exist_ok=True)
                
                original_name = Path(args.tools_yaml_path).stem
                updated_yaml_path = os.path.join(args.output_dir, f"{original_name}_with_server_urls.yaml")
                
                print(f"📝 创建配置文件: {updated_yaml_path}")
                update_tools_config_with_urls(args.tools_yaml_path, master_url, updated_yaml_path, 
                                            args.updated_tool_class, args.timeout_per_query)
                
                print(f"📄 Master配置文件: {updated_yaml_path}")
            else:
                print("📄 未提供工具配置，Master将通过Worker注册动态发现工具")
            
            print(f"🌐 Master URL: {master_url}")
            print(f"📋 Worker注册地址: {master_url}/register_worker")
            
            server.run()
            
        elif args.mode == "worker":
            # 检查是否在分布式环境中（rjob等）
            node_rank = int(os.getenv("NODE_RANK", "0"))
            node_count = int(os.getenv("NODE_COUNT", "1"))
            hostname = socket.gethostname()
            
            # 随机偏置调整端口，避免端口冲突
            adjusted_port = args.port + random.randint(0, 100) + node_rank % 256
            
            # 输出节点信息
            print("\n" + "=" * 50)
            print("🖥️  Worker 节点信息")
            print("=" * 50)
            print(f"  NODE_RANK:    {node_rank}")
            print(f"  NODE_COUNT:   {node_count}")
            print(f"  HOSTNAME:     {hostname}")
            print(f"  Start Port:     {args.port}")
            print(f"  Adjusted Port:   {adjusted_port}")
            print(f"  Master URL:   {args.master_url}")
            print(f"  Worker Nums:   {args.num_workers}")
            print("=" * 50 + "\n")
            
            # 检查 Master 服务是否可用
            if args.master_url:
                print(f"🔍 检查 Master 服务: {args.master_url}")
                for attempt in range(1, 11):
                    try:
                        response = requests.get(
                            f"{args.master_url}/health",
                            timeout=3
                        )
                        if response.status_code == 200:
                            print(f"✅ Master 服务可用")
                            break
                    except Exception as e:
                        if attempt < 10:
                            print(f"⏳ 等待 Master 服务... (尝试 {attempt}/10)")
                            time.sleep(2)
                        else:
                            print(f"⚠️  警告: Master 服务可能不可用: {e}")
                            print(f"⚠️  将继续启动 Worker，但注册可能失败")
                
                print()  # 空行
            
            # 启动Worker服务器（支持多个Worker）
            print(f"🚀 启动 {args.num_workers} 个分布式Worker服务器...")
            
            # 使用调整后的端口
            worker_processes, worker_urls = start_multiple_workers(
                tools_config, args.host, adjusted_port, args.master_url, args.num_workers
            )
            
            print(f"🆔 启动了 {len(worker_processes)} 个Worker进程")
            print(f"📋 Worker URLs: {worker_urls}")
            print(f"💾 日志提示: 子进程日志可能在 /tmp/worker_*.log\n")
            
            try:
                # 等待所有进程
                for process in worker_processes:
                    process.join()
            except KeyboardInterrupt:
                print(f"\n⚠️  用户中断操作，正在停止所有Worker...")
                for process in worker_processes:
                    if process.is_alive():
                        process.terminate()
                        process.join(timeout=5)
            
        elif args.mode == "unified":
            # 启动统一服务器（Master + 多个Worker）
            print(f"\n🚀 启动统一服务器（Master + {args.num_workers} 个Worker）...")
            
            external_ip = get_external_ip()
            
            # 创建配置文件
            if args.output_dir is None:
                args.output_dir = os.path.dirname(args.tools_yaml_path)
            os.makedirs(args.output_dir, exist_ok=True)
            
            original_name = Path(args.tools_yaml_path).stem
            updated_yaml_path = os.path.join(args.output_dir, f"{original_name}_with_server_urls.yaml")
            server_url = f"http://{external_ip}:{args.port}"
            
            print(f"📝 创建配置文件: {updated_yaml_path}")
            update_tools_config_with_urls(args.tools_yaml_path, server_url, updated_yaml_path, 
                                        args.updated_tool_class, args.timeout_per_query)
            
            print(f"📄 配置文件: {updated_yaml_path}")
            print(f"🌐 Master服务器URL: {server_url}")
            
            # 创建日志文件
            unified_log_path = None
            if args.log_dir:
                os.makedirs(args.log_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unified_log_path = os.path.join(args.log_dir, f"unified_server_{timestamp}.log")
                print(f"📄 统一日志文件: {unified_log_path}")
                
                # 写入启动信息
                with open(unified_log_path, 'w', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 开始启动统一服务器\n")
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Worker数量: {args.num_workers}\n")
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Master端口: {args.port}\n")
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] IP: {external_ip}\n")
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 配置文件: {updated_yaml_path}\n")
            
            # 存储进程引用以便清理
            worker_processes = []
            master_process = None
            
            try:
                # 1. 启动Master进程
                log_message("--- 启动Master服务器 ---", unified_log_path)
                
                master_process = multiprocessing.Process(
                    target=start_master_process,
                    args=(tools_config, args.host, args.port, unified_log_path, args.zombie_instance_timeout)
                )
                master_process.start()
                
                # 等待Master启动
                log_message("⏳ 等待Master启动完成...", unified_log_path)
                time.sleep(3)
                
                if not master_process.is_alive():
                    raise RuntimeError("Master服务器启动失败")
                
                log_message(f"✅ Master服务器启动成功于端口 {args.port}", unified_log_path)
                
                # 2. 启动Worker进程
                worker_processes, worker_urls = start_multiple_workers(
                    tools_config, args.host, args.port + 1, server_url, args.num_workers, unified_log_path
                )
                
                # 等待Worker启动并注册
                log_message("⏳ 等待所有Worker启动并注册到Master...", unified_log_path)
                time.sleep(5)
                
                # 验证Worker是否启动成功
                alive_workers = []
                for i, process in enumerate(worker_processes):
                    if process.is_alive():
                        alive_workers.append(worker_urls[i])
                        log_message(f"  ✅ Worker {i+1} 启动进程运行正常", unified_log_path)
                    else:
                        log_message(f"  ❌ Worker {i+1} 启动进程运行失败", unified_log_path)
                
                if not alive_workers:
                    raise RuntimeError("没有Worker成功启动")
                
                # 测试服务器功能（如果启用）
                if args.test_servers:
                    from .utils import extract_tool_names_from_config
                    tool_names = extract_tool_names_from_config(tools_config)
                    
                    log_message("🧪 测试统一服务器...", unified_log_path)
                    time.sleep(3)  # 等待完全启动
                    
                    test_servers(server_url, tool_names, args.test_timeout, args.connectivity_only)
                    
                    if not args.keep_running:
                        print(f"\n⚠️  测试完成，服务器将停止")
                        return
                
                log_message("🎉 统一服务器架构启动完成！", unified_log_path)
                log_message(f"   - Master: {server_url}", unified_log_path)
                log_message(f"   - Workers: {len(alive_workers)} 个", unified_log_path)
                if args.log_dir:
                    log_message(f"📊 日志保存到: {unified_log_path}", unified_log_path)
                
                if args.keep_running:
                    log_message("🔄 服务器将持续运行... (按 Ctrl+C 停止)", unified_log_path)
                    
                    try:
                        # 监控所有进程
                        while True:
                            time.sleep(10)
                            
                            # 检查Master进程
                            if not master_process.is_alive():
                                print(f"⚠️  Master进程已停止")
                                break
                            
                            # 检查Worker进程
                            dead_workers = []
                            for i, process in enumerate(worker_processes):
                                if not process.is_alive():
                                    dead_workers.append(i+1)
                            
                            if dead_workers:
                                print(f"⚠️  Worker进程已停止: {dead_workers}")
                                break
                                
                    except KeyboardInterrupt:
                        print(f"\n⚠️  用户中断操作")
                else:
                    print(f"\n⚠️  注意: 使用 --keep_running 参数来保持服务器运行")
                    print(f"⚠️  服务器进程将在脚本退出后继续运行")
                
            finally:
                # 清理进程
                if not args.keep_running:
                    log_message("清理进程...", unified_log_path)
                    
                    if master_process and master_process.is_alive():
                        master_process.terminate()
                        master_process.join(timeout=5)
                        log_message("✅ Master进程已停止", unified_log_path)
                    
                    for i, process in enumerate(worker_processes):
                        if process.is_alive():
                            process.terminate()
                            process.join(timeout=5)
                            log_message(f"✅ Worker {i+1} 进程已停止", unified_log_path)
                    
                    # 记录最终清理完成
                    if unified_log_path:
                        with open(unified_log_path, 'a', encoding='utf-8') as f:
                            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🏁 统一服务器已停止\n")
            
    except Exception as e:
        print(f"❌ 脚本执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # 清理临时文件
        if temp_yaml_file and os.path.exists(temp_yaml_file):
            try:
                os.remove(temp_yaml_file)
                print(f"🧹 已清理临时文件: {temp_yaml_file}")
            except Exception as e:
                print(f"⚠️  清理临时文件失败: {e}")


if __name__ == "__main__":
    if __name__ == '__main__':
        multiprocessing.set_start_method('spawn') 
    main() 