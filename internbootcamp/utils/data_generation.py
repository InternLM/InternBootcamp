import ast
import json
from starlette.middleware import P
import yaml
import importlib
import random
import argparse
import os
import time
import signal
from typing import Dict, List, Optional, Any
from tqdm import tqdm
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator
from internbootcamp.utils.jsonl2parquet import jsonl_to_parquet
from internbootcamp.utils.format_time_now import format_time_now

from PIL import Image


class TimeoutException(Exception):
    """超时异常"""
    pass


def timeout_handler(signum, frame):
    """超时信号处理函数"""
    raise TimeoutException("Generator execution timeout")


def call_with_timeout(func, timeout_seconds=60):
    """
    带超时的函数调用
    
    Args:
        func: 要调用的函数
        timeout_seconds: 超时时间（秒）
    
    Returns:
        函数的返回值
    
    Raises:
        TimeoutException: 如果函数执行超时
    """
    # 设置信号处理器
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
        result = func()
        signal.alarm(0)  # 取消alarm
        return result
    except TimeoutException:
        signal.alarm(0)  # 取消alarm
        raise
    except Exception as e:
        signal.alarm(0)  # 取消alarm
        raise e

def load_instruction_generators_from_config(config_path: str) -> List[Dict[str, Any]]:
    """
    从配置文件加载指令管理器实例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        List[Dict]: 包含管理器实例和配置信息的列表
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 获取全局配置
    global_config = config.get('global_config', {})
    class_name = global_config.get('class_name')
    
    if not class_name:
        raise ValueError("配置文件中必须指定 global_config.class_name")
    
    # 动态导入类
    module_path, class_name_only = class_name.rsplit('.', 1)
    module = importlib.import_module(module_path)
    generator_class = getattr(module, class_name_only)
    
    # 验证类是否继承自BaseInstructiongenerator
    if not issubclass(generator_class, BaseInstructionGenerator):
        raise TypeError(f"类 {class_name} 必须继承自 BaseInstructiongenerator")
    
    # 处理多组指令管理器配置
    instruction_generators = []
    generators_config = config.get('instruction_generators', {})
    
    for generator_name, generator_config in generators_config.items():
        config_params = generator_config.get('config', {})
        generation_ratio = generator_config.get('generation_ratio', 1.0)
        tool_config_path = generator_config.get('tool_config_path', None)
        interaction_config_path = generator_config.get('interaction_config_path', None)
        
        # 加载该generator的工具配置
        tools = load_tools_from_config(tool_config_path) if tool_config_path else []
        
        # 加载该generator的交互配置
        interaction_kwargs = load_interaction_config(interaction_config_path) if interaction_config_path else {}
        
        # 创建管理器实例
        generator_instance = generator_class(**config_params)
        instruction_generators.append({
            'generator': generator_instance,
            'ratio': generation_ratio,
            'name': generator_name,
            'tools': tools,
            'interaction_kwargs': interaction_kwargs
        })
    
    return instruction_generators


def load_tools_from_config(tool_config_path: Optional[str]) -> List[Dict]:
    """
    从配置文件加载工具配置
    
    Args:
        tool_config_path: 工具配置文件路径
        
    Returns:
        List[Dict]: 工具配置列表
    """
    if tool_config_path is None:
        return []
    
    with open(tool_config_path, 'r', encoding='utf-8') as f:
        yaml_config = yaml.safe_load(f)
    
    return yaml_config.get('tools', [])


def load_interaction_config(interaction_config_path: Optional[str]) -> Dict:
    """
    从配置文件加载交互配置
    
    Args:
        interaction_config_path: 交互配置文件路径
        
    Returns:
        Dict: 交互配置
    """
    if interaction_config_path is None:
        return {}
    
    with open(interaction_config_path, 'r', encoding='utf-8') as f:
        interaction_config = yaml.safe_load(f)
    
    return interaction_config.get('interaction', {})[0] if isinstance(interaction_config, dict) else interaction_config


def generate_data_with_config(
    instruction_config_path: str,
    output_dir: str,
    override: bool,
    tool_config_path: Optional[str] = None,
    interaction_config_path: Optional[str] = None,
    split_samples: Optional[Dict[str, int]] = None,
    shuffle: Optional[bool] = None,
    gen_parquet: Optional[bool] = True,
    global_config_overrides: Optional[Dict] = None,
    no_tool: Optional[bool] = False,
    no_interaction: Optional[bool] = False
    ) -> None:
    """
    通过配置文件生成数据的主函数
    
    Args:
        instruction_config_path: 指令管理器配置文件路径
        output_dir: 输出文件目录
        tool_config_path: 工具配置文件路径（可选）
        interaction_config_path: 交互配置文件路径（可选）
        split_samples: 数据集划分和样本数配置，格式为字典，如 {'train': 100, 'test': 50, 'val': 20}
                      如果为None，将从配置文件中读取默认值
        shuffle: 是否启用数据打乱，如果为None，将从配置文件中读取
        global_config_overrides: 全局配置覆盖参数（可选）
    """
    # 用于跟踪创建的文件，在失败时清理
    created_files = []
    
    try:
        # 加载配置文件
        with open(instruction_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 获取全局配置
        global_config = config.get('global_config', {})
        
        # 应用配置覆盖
        if global_config_overrides:
            global_config.update(global_config_overrides)
        
        # 设置默认值
        if split_samples is None:
            split_samples = global_config.get('default_split_samples', {'test': 1})
        
        # global_config是高优先级，覆盖函数参数
        shuffle = global_config.get('shuffle', shuffle)
        gen_parquet = global_config.get('gen_parquet', gen_parquet)
        
        # 验证split_samples参数
        if not isinstance(split_samples, dict):
            raise ValueError("split_samples参数必须是字典格式，如 {'train': 100, 'test': 50}")
        
        # 加载指令管理器（现在每个generator都有自己的tools和interaction_kwargs）
        try:
            instruction_generators = load_instruction_generators_from_config(instruction_config_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load instruction generators from config file {instruction_config_path}. Error: {str(e)}")
        
        # 如果传入了全局tool_config_path,则加载全局工具配置
        global_tools = []
        global_interaction_kwargs = {}
        if tool_config_path:
            global_tools = load_tools_from_config(tool_config_path)
        
        # 如果传入了全局interaction_config_path,则加载全局交互配置
        if interaction_config_path:
            global_interaction_kwargs = load_interaction_config(interaction_config_path)
        
        # 获取sample num 大于0的splits
        splits = [split for split, num in split_samples.items() if num > 0]
        
        # 计算总样本数
        total_samples = sum(split_samples[split] for split in splits)
        
        # 为每个split生成数据
        if not override:
            timestamp = format_time_now()
        global_index = 0
        
        # 创建总进度条
        with tqdm(total=total_samples, desc=f"生成 {os.path.basename(instruction_config_path).replace('_instruction_config.yaml', '')} 数据") as pbar:
            for current_split in splits:
                num_samples = split_samples[current_split]
                
                # 计算每组配置应生成的数据量
                total_ratio = sum(generator['ratio'] for generator in instruction_generators)
                generator_samples = []
                for generator in instruction_generators:
                    samples = int(num_samples * generator['ratio'] / total_ratio)
                    generator_samples.append((generator, samples))
                
                # 处理余数，确保总数正确
                remaining_samples = num_samples - sum(samples for _, samples in generator_samples)
                if remaining_samples > 0:
                    generator_samples[0] = (generator_samples[0][0], generator_samples[0][1] + remaining_samples)
                
                if override:
                    current_output_path = os.path.join(output_dir, f"{os.path.basename(instruction_config_path).replace('_instruction_config.yaml', '')}_{current_split}.jsonl")
                else:
                    current_output_path = os.path.join(output_dir, f"{os.path.basename(instruction_config_path).replace('_instruction_config.yaml', '')}_{timestamp}_{current_split}.jsonl")
                
                # 确保输出目录存在
                os.makedirs(os.path.dirname(current_output_path), exist_ok=True)
                
                # 记录将要创建的文件
                created_files.append(current_output_path)
                
                # 标记文件是否成功生成数据
                file_has_data = False

                print("data generation ratio (can be modified in instruction.yaml): \n")
                for i in range(len(generator_samples)):
                    print("generator name: ", generator_samples[i][0]["name"], "data num: ", generator_samples[i][1])
                
                try:
                    # 写入文件
                    with open(current_output_path, 'w', encoding='utf-8') as f:
                        for generator_info, samples in generator_samples:
                            generator = generator_info['generator']
                            generator_name = generator_info['name']
                            # 使用该generator的独立配置，如果没有则回退到全局配置
                            tools = generator_info.get('tools', [])
                            if len(tools) == 0:
                                tools = global_tools
                            interaction_kwargs = generator_info.get('interaction_kwargs', {})
                            if len(interaction_kwargs) == 0:
                                interaction_kwargs = global_interaction_kwargs
                            
                            for idx in range(samples):
                                max_attempts = 100
                                
                                for attempt in range(max_attempts):
                                    try:
                                        # 使用带超时的函数调用
                                        identity = generator.case_generator()
                                        prompt = generator.prompt_func(identity)
                                        break
                                    except Exception as e:
                                        print(e)
                                        if attempt == max_attempts - 1:
                                            raise RuntimeError(f"Failed to generate example after {max_attempts} attempts.")
                                        continue
                                
                                tools_kwargs = {}
                                if not no_tool:
                                    for tool in tools:
                                        func_name = tool.get('tool_schema', {}).get('function', {}).get('name')
                                        if func_name:
                                            tools_kwargs[func_name] = {"create_kwargs": {"identity": identity}}
                                
                                extra_info = {}
                                extra_info['tools_kwargs'] = tools_kwargs
                                extra_info['need_tools_kwargs'] = True if len(tools_kwargs) > 0 else False
                                extra_info['index'] = global_index
                                extra_info['split'] = current_split
                                extra_info['generator_name'] = generator_name
                                if not no_interaction and interaction_kwargs:
                                    extra_info['interaction_kwargs'] = {}
                                    extra_info['interaction_kwargs']['name'] = interaction_kwargs['name']
                                    extra_info['interaction_kwargs']['identity'] = identity
                                if isinstance(prompt, str):
                                    data = {
                                        "data_source": generator.data_source,
                                        "prompt": [
                                            {"content": prompt, "role": "user"}
                                        ],
                                        "reward_model": {
                                            "ground_truth": identity,
                                            "style": "rule"
                                        },
                                        "extra_info": extra_info
                                    }
                                elif isinstance(prompt, dict):
                                    image = prompt['prompt_img']
                                    data = {
                                        "data_source": generator.data_source,
                                        "prompt": [
                                            {"content": '<image>' + prompt['prompt_txt'], "role": "user"}
                                        ],
                                        "image": [image],
                                        "reward_model": {
                                            "ground_truth": identity,
                                            "style": "rule"
                                        },
                                        "extra_info": extra_info
                                    }
                                f.write(json.dumps(data, ensure_ascii=False) + '\n')
                                f.flush()  # 确保数据写入磁盘
                                file_has_data = True  # 标记文件已写入数据
                                global_index += 1
                                
                                # 更新总进度条
                                pbar.update(1)
                                pbar.set_postfix({
                                    'split': current_split,
                                    'generator': generator_name,
                                    'samples': f"{global_index}/{total_samples}"
                                })
                    
                    # 如果文件没有数据，删除空文件
                    if not file_has_data and os.path.exists(current_output_path):
                        os.remove(current_output_path)
                        created_files.remove(current_output_path)
                        continue
                    
                    # 如果启用shuffle，对文件进行shuffle操作
                    if shuffle:
                        # print("正在对文件进行shuffle操作...")
                        # 读取文件内容
                        with open(current_output_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        
                        # 打乱行顺序
                        random.shuffle(lines)
                        
                        # 重新写入文件
                        with open(current_output_path, 'w', encoding='utf-8') as f:
                            f.writelines(lines)
                    
                    # print(f'已生成 {current_split} 数据到 {current_output_path}')
                    if gen_parquet:
                        jsonl_to_parquet(current_output_path, current_output_path.replace(".jsonl", ".parquet"))
                        # 如果生成了parquet文件，也记录到created_files中
                        parquet_path = current_output_path.replace(".jsonl", ".parquet")
                        if os.path.exists(parquet_path):
                            created_files.append(parquet_path)
                
                except Exception as e:
                    # 重新抛出异常
                    raise e
    
    except Exception as e:
        # 记录错误
        with open(os.path.join(output_dir, "datagen_error_log.jsonl"), "a") as f:
            f.write(json.dumps({
                "Instruction Config Path": instruction_config_path,
                "Error": str(e),
                "Error Message": str(e),
                "Timestamp": format_time_now(),
            }, ensure_ascii=False) + "\n")
        # 如果整个数据生成过程失败，清理所有已创建的文件
        for file_path in created_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        # 重新抛出原始异常
        raise e
    
def parse_split_samples(split_samples_str):
    """
    将形如 'train:10000,test:100' 的字符串解析为字典 {'train': 10000, 'test': 100}
    """
    result = {}
    if not split_samples_str:
        return result
    for item in split_samples_str.split(','):
        if ':' in item:
            k, v = item.split(':', 1)
            result[k.strip()] = int(v.strip())
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="通过配置文件生成数据集")
    parser.add_argument('--instruction-config', type=str, required=True, help='指令管理器配置文件路径')
    parser.add_argument('--output-dir', type=str, required=True, help='输出文件目录')
    parser.add_argument('--override', action='store_true', help='数据文件不带时间戳，直接覆盖')
    parser.add_argument('--tool-config', type=str, default=None, help='工具配置文件路径(本质上只用到所调用工具的名称)')
    parser.add_argument('--interaction-config', type=str, default=None, help='交互配置文件路径')
    parser.add_argument('--split-samples', type=str, default=None, help="数据集划分和样本数，如 'train:10000,test:100'")
    parser.add_argument('--shuffle', action='store_true', help='是否对生成的数据进行shuffle')
    parser.add_argument('--global-config-overrides', type=str, default=None, help='全局配置覆盖参数')
    
    args = parser.parse_args()

    split_samples = parse_split_samples(args.split_samples) if args.split_samples else None

    # print(args.global_config_overrides)
    
    # print("开始通过配置文件生成数据...")
    generate_data_with_config(
        instruction_config_path=args.instruction_config,
        output_dir=args.output_dir,
        override=args.override,
        tool_config_path=args.tool_config,
        interaction_config_path=args.interaction_config,
        split_samples=split_samples,
        shuffle=args.shuffle,
        global_config_overrides=json.loads(args.global_config_overrides) if args.global_config_overrides else None
    )
    # print("数据生成完成！") 