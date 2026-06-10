#!/usr/bin/env python3
"""
通用命令行评测脚本

这个脚本提供了一个通用的命令行接口来运行各种评测任务。
支持动态加载评测器、配置工具和数据集，提供灵活的评测框架。
"""

import argparse
import asyncio
import importlib
import os
import ast
import sys
import json
import yaml
import traceback
from typing import Dict, Any, Optional, List


from internbootcamp.src.base_evaluator import BaseEvaluator
from internbootcamp.utils.load_class_from_str import load_class_from_string


def create_evaluator(
    evaluator_class: str = None,
    api_url: str = None,
    api_key: str = None,
    api_model: str = "gpt-3.5-turbo",
    api_proxy: str = "",
    reward_calculator = None,
    max_assistant_turns: int = 10,
    max_user_turns: int = 5,
    api_extra_headers: Optional[Dict] = None,
    api_extra_params: Optional[Dict] = None,
    verify_correction_kwargs: Optional[Dict] = None,
    **kwargs
):
    """
    创建评测器实例
    
    Args:
        evaluator_class: 评测器类路径
        api_url: API URL
        api_key: API 密钥
        api_model: 模型名称
        reward_calculator: 奖励计算器实例
        max_assistant_turns: assistant响应的最大轮次
        max_user_turns: user输入的最大轮次
        api_extra_headers: 额外的API头部
        api_extra_params: 额外的模型参数（如temperature、max_tokens等）
        verify_correction_kwargs: 传递给奖励计算器verify_correction方法的额外参数
        **kwargs: 传递给评测器的额外参数
        
    Returns:
        评测器实例
    """
    if evaluator_class:
        evaluator_cls = load_class_from_string(evaluator_class)
    else:
        evaluator_cls = BaseEvaluator
    
    return evaluator_cls(
        api_url=api_url,
        api_key=api_key,
        api_model=api_model,
        api_proxy=api_proxy,
        reward_calculator=reward_calculator,
        max_assistant_turns=max_assistant_turns,
        max_user_turns=max_user_turns,
        api_extra_headers=api_extra_headers,
        api_extra_params=api_extra_params,
        verify_correction_kwargs=verify_correction_kwargs,
        **kwargs
    )


def parse_extra_headers(headers_str: str) -> Dict[str, str]:
    """
    解析额外的HTTP头部参数
    
    Args:
        headers_str: 格式如 "key1:value1,key2:value2" 的字符串
        
    Returns:
        解析后的头部字典
    """
    headers = {}
    if headers_str:
        for header in headers_str.split(','):
            if ':' in header:
                key, value = header.split(':', 1)
                headers[key.strip()] = value.strip()
    return headers


def parse_extra_params(params_str: str) -> Dict[str, any]:
    """
    解析额外的模型参数
    
    Args:
        params_str: 支持以下两种形式之一：
            1) JSON 字符串（推荐）：例如 '{"temperature":0.7,"max_tokens":2048}' 或嵌套结构
            2) 以 '@' 开头的文件路径：例如 '@/path/to/params.json'（文件内容为 JSON）
        同时保留对旧格式 "k:v,k2:v2" 的兼容作为回退解析。
        
    Returns:
        解析后的参数字典
    """
    if not params_str:
        return {}

    text = params_str.strip()

    # 情况 1：@文件 路径（文件内容为 JSON）
    if text.startswith('@'):
        file_path = text[1:]
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"参数文件不存在: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        try:
            loaded = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"参数文件 JSON 解析失败: {e}")
        if not isinstance(loaded, dict):
            raise ValueError("参数文件的 JSON 根类型必须为对象(dict)")
        return loaded

    # 情况 2：直接作为 JSON 字符串
    try:
        loaded = json.loads(text)
        if isinstance(loaded, dict):
            return loaded
        else:
            raise ValueError("JSON 根类型必须为对象(dict)")
    except json.JSONDecodeError:
        # 继续尝试回退到旧格式解析
        try:
            loaded = ast.literal_eval(text)
            if isinstance(loaded, dict):
                return loaded
        except Exception:
            print(f"Depreciated Warning: {text} 额外参数未能解析为 JSON 格式，将使用旧格式解析。请优先考虑使用 JSON 格式传递参数。")

    # 回退：旧格式 "k:v,k2:v2"（保持向后兼容）
    params: Dict[str, Any] = {}
    for param in text.split(','):
        if ':' not in param:
            continue
        key, value = param.split(':', 1)
        key = key.strip()
        value = value.strip()

        # 自动转换类型（int/float/bool），否则字符串
        try:
            if value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                params[key] = int(value)
            elif '.' in value:
                # 尝试 float；若失败则保留字符串
                params[key] = float(value)
            elif value.lower() in ('true', 'false'):
                params[key] = value.lower() == 'true'
            else:
                params[key] = value
        except ValueError:
            params[key] = value

    return params


def load_yaml(yaml_path: str) -> Optional[Dict[str, Any]]:
        """
        从 YAML 文件加载工具配置，构建 tools 和 tool_registry
        """
        with open(yaml_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config


def main():
    parser = argparse.ArgumentParser(
        description="通用命令行评测脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例: verl/Bootcampv2/example_bootcamp/examples/run_example_evaluation.sh
"""
    )
    
    parser.add_argument('--dataset-path', type=str, help='数据集文件路径 (.json, .jsonl, .parquet)')
    parser.add_argument('--output-dir', type=str, help='评测结果输出目录')
    parser.add_argument('--api-key', type=str, help='API 密钥')
    parser.add_argument('--api-url', type=str, default=None, help='API URL (如果不指定则使用默认的OpenAI API)')
    parser.add_argument('--api-model', type=str, default='gpt-3.5-turbo', help='模型名称 (默认: gpt-3.5-turbo)')
    parser.add_argument('--api-proxy', type=str, default='', help='代理url')
    parser.add_argument('--api-extra-headers', type=str, default=None, help='额外的API头部，格式: "key1:value1,key2:value2"')
    parser.add_argument('--api-start-url', type=str, default=None, help='Start阶段的API URL (用于Bayesian Agent评测器)')
    parser.add_argument('--api-start-key', type=str, default=None, help='Start阶段的API 密钥 (默认使用--api-key)')
    parser.add_argument('--api-start-headers', type=str, default=None, help='Start阶段的额外API头部 (默认使用--api-extra-headers)')
    parser.add_argument('--api-start-model', type=str, default=None, help='Start阶段的模型名称 (默认使用--api-model)')
    parser.add_argument('--api-loop-url', type=str, default=None, help='Loop阶段的API URL (用于Bayesian Agent评测器)')
    parser.add_argument('--api-loop-key', type=str, default=None, help='Loop阶段的API 密钥 (默认使用--api-key)')
    parser.add_argument('--api-loop-headers', type=str, default=None, help='Loop阶段的额外API头部 (默认使用--api-extra-headers)')
    parser.add_argument('--api-loop-model', type=str, default=None, help='Loop阶段的模型名称 (默认使用--api-model)')
    parser.add_argument('--api-extra-params', type=str, default=None, help='额外的模型参数；支持 JSON 字符串或 @文件（JSON）。示例：\n  1) JSON 字符串：\n     --api-extra-params \'{"temperature":0.7, "max_completion_tokens":65536, "extra_body": {"enable_thinking": true}}\'\n  2) 从文件读取（以 @ 开头）：\n     --api-extra-params @/path/to/params.json\n  3) 回退兼容旧格式："temperature:0.7,max_tokens:2048,top_p:0.9"')
    parser.add_argument('--verify-correction-kwargs', type=str, default=None, help='额外的奖励计算函数参数；支持格式同api-extra-params(该参数解包传递给reward calculator的verify correction方法)')
    parser.add_argument('--evaluator-class', type=str, default=None, help='评测器类路径 (如: verl.Bootcampv2.example_bootcamp.example_evaluator.ExampleEvaluator)')
    parser.add_argument('--reward-calculator-class', type=str, default=None, help='奖励计算器类路径（可选，优先级低于 --reward-config）')
    parser.add_argument('--reward-config', type=str, default=None, help='reward配置YAML文件路径')
    parser.add_argument('--tool-config', type=str, default=None, help='工具配置YAML文件路径')
    parser.add_argument('--interaction-config', type=str, default=None, help='交互配置YAML文件路径')
    parser.add_argument('--max-tool-turns-per-interaction', type=int, default=None, help='每次交互的最大工具调用轮次 (已弃用)')
    parser.add_argument('--max-interaction-turns', type=int, default=None, help='最大交互轮次 (已弃用)')
    parser.add_argument('--max-assistant-turns', type=int, default=None, help='assistant响应的最大轮次 (默认: None，无限制)')
    parser.add_argument('--max-user-turns', type=int, default=None, help='user输入的最大轮次(包括tool response, interaction response) (默认: None，无限制)')
    parser.add_argument('--max-concurrent', type=int, default=1, help='最大并发数 (默认: 1)')
    parser.add_argument('--verbose', action='store_true', help='输出详细信息')
    parser.add_argument('--dry-run', action='store_true', help='只验证配置，不实际运行评测')
    parser.add_argument('--tokenizer-path', type=str, default=None, nargs='?', const=None, help='tokenizer路径(可选, apply template时使用)')
    parser.add_argument('--bootcamp-registry', type=str, default=None, help='bootcamp注册表路径(可选, 用于批量评测)')
    parser.add_argument('--resume-from-result-path', type=str, default=None, help='断点重试模式：指定要恢复的结果文件路径(.jsonl)')
    parser.add_argument('--max-iterations', type=int, default=None, help='单轮数据最大迭代次数（用于单轮评测）')
    parser.add_argument('--use-retrieval', action='store_true', help='是否启用参数检索')
    parser.add_argument('--retrieval-db-path', type=str, default=None, help='参数检索数据库路径（文件或目录）')
    parser.add_argument('--retrieval-top-n', type=int, default=5, help='参数检索返回的近邻数量')
    parser.add_argument('--max-loops', type=int, default=None, help='单轮数据最大迭代次数（用于单轮评测）')
    parser.add_argument('--bayesian-n-workers', type=int, default=None, help='贝叶斯优化工人数量')
    parser.add_argument('--bayesian-init-points', type=int, default=None, help='贝叶斯优化初始点数量')
    parser.add_argument('--bayesian-n-iter', type=int, default=None, help='贝叶斯优化迭代次数')
    parser.add_argument('--cold-start-type', type=str, default=None, help='冷启动类型')
    args = parser.parse_args()
    
    # 验证输入文件
    if not os.path.exists(args.dataset_path):
        print(f"❌ 错误: 数据集文件不存在: {args.dataset_path}")
        sys.exit(1)
    
    # 验证断点重试文件
    if args.resume_from_result_path and not os.path.exists(args.resume_from_result_path):
        print(f"❌ 错误: 断点重试文件不存在: {args.resume_from_result_path}")
        sys.exit(1)
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 处理参数兼容性
    if args.max_tool_turns_per_interaction:
        print("⚠️  警告: --max-tool-turns-per-interaction已弃用，请使用--max-assistant-turns代替")
    if args.max_interaction_turns:
        print("⚠️  警告: --max-interaction-turns已弃用，请使用--max-assistant-turns代替")
    
    if args.verbose:
        print("🔧 配置信息:")
        print(f"  数据集路径: {args.dataset_path}")
        print(f"  输出目录: {args.output_dir}")
        print(f"  API模型: {args.api_model}")
        print(f"  工具配置路径 (tool config): {args.tool_config if args.tool_config else '无'}")
        print(f"  Reward配置路径 (reward config): {args.reward_config if args.reward_config else '无'}")
        print(f"  交互配置路径 (interaction config): {args.interaction_config if args.interaction_config else '无'}")
        print(f"  最大assistant轮次: {args.max_assistant_turns}")
        print(f"  最大user轮次: {args.max_user_turns}")
        print(f"  最大并发: {args.max_concurrent}")
        print(f"  额外API头部: {args.api_extra_headers if args.api_extra_headers else '无'}")
        print(f"  额外模型参数: {args.api_extra_params if args.api_extra_params else '无'}")
        print(f"  验证修正参数: {args.verify_correction_kwargs if args.verify_correction_kwargs else '无'}")
        print(f"  断点重试: {'启用 (' + args.resume_from_result_path + ')' if args.resume_from_result_path else '禁用'}")
        print(f"  最大迭代次数: {args.max_iterations if args.max_iterations else '无'}")
        print(f"  最大loop次数: {args.max_loops if args.max_loops else '无'}")
        print(f"  贝叶斯优化初始点数量: {args.bayesian_init_points if args.bayesian_init_points else '无'}")
        print(f"  贝叶斯优化迭代次数: {args.bayesian_n_iter if args.bayesian_n_iter else '无'}")
        print(f"  冷启动类型: {args.cold_start_type if args.cold_start_type else '无'}")
        print(f"  Start阶段API URL: {args.api_start_url if args.api_start_url else '无'}")
        print(f"  Start阶段API模型: {args.api_start_model if args.api_start_model else '无'}")
        print(f"  Loop阶段API URL: {args.api_loop_url if args.api_loop_url else '无'}")
        print(f"  Loop阶段API模型: {args.api_loop_model if args.api_loop_model else '无'}")
    try:
        # 解析额外头部和参数
        extra_headers = parse_extra_headers(args.api_extra_headers) if args.api_extra_headers else None
        extra_params = parse_extra_params(args.api_extra_params) if args.api_extra_params else None
        verify_correction_kwargs = parse_extra_params(args.verify_correction_kwargs) if args.verify_correction_kwargs else None
        
        # 解析Start和Loop阶段的头部（如果指定，否则使用默认值）
        api_start_headers = parse_extra_headers(args.api_start_headers) if args.api_start_headers else extra_headers
        api_loop_headers = parse_extra_headers(args.api_loop_headers) if args.api_loop_headers else extra_headers
        
        # 设置Start和Loop阶段的API密钥（如果指定，否则使用默认值）
        api_start_key = args.api_start_key if args.api_start_key else args.api_key
        api_loop_key = args.api_loop_key if args.api_loop_key else args.api_key
        
        # 创建奖励管理器
        if args.verbose:
            print("📊 正在创建奖励计算器...")
        if args.reward_config:
            reward_config = load_yaml(args.reward_config)
            reward_calculator = load_class_from_string(reward_config["class_name"])
            # reward_calculator = reward_calculator(reward_config["config"])
        elif args.reward_calculator_class:
            reward_calculator = load_class_from_string(args.reward_calculator_class)
        else:
            reward_calculator = None
        
        # 创建评测器
        if args.verbose:
            print("🤖 正在创建评测器...")
        evaluator = create_evaluator(
            evaluator_class=args.evaluator_class,
            api_url=args.api_url,
            api_key=args.api_key,
            api_model=args.api_model,
            api_proxy=args.api_proxy,
            reward_calculator=reward_calculator,
            max_assistant_turns=args.max_assistant_turns,
            max_user_turns=args.max_user_turns,
            api_extra_headers=extra_headers,
            api_extra_params=extra_params,
            verify_correction_kwargs=verify_correction_kwargs,
            tokenizer_path=args.tokenizer_path,
            max_iterations=args.max_iterations,
            max_loops=args.max_loops,
            bayesian_n_workers=args.bayesian_n_workers,
            bayesian_init_points=args.bayesian_init_points,
            bayesian_n_iter=args.bayesian_n_iter,
            cold_start_type=args.cold_start_type,
            api_start_url=args.api_start_url,
            api_start_key=api_start_key,
            api_start_headers=api_start_headers,
            api_start_model=args.api_start_model if args.api_start_model else args.api_model,
            api_loop_url=args.api_loop_url,
            api_loop_key=api_loop_key,
            api_loop_headers=api_loop_headers,
            api_loop_model=args.api_loop_model if args.api_loop_model else args.api_model,
        )
        
        if args.dry_run:
            print("✅ 配置验证通过！(干运行模式)")
            return
        
        # 运行评测 - 直接使用base_evaluator的run_evaluation方法
        asyncio.run(evaluator.run_evaluation(
            dataset_path=args.dataset_path,
            output_dir=args.output_dir,
            yaml_tool_path=args.tool_config,
            yaml_interaction_path=args.interaction_config,
            max_concurrent=args.max_concurrent,
            bootcamp_registry=args.bootcamp_registry,
            resume_from_result_path=args.resume_from_result_path
        ))
        
    except Exception as e:
        print(f"❌ 评测过程中发生错误: {str(e)}")
        if args.verbose:
            print("详细错误信息:")
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
