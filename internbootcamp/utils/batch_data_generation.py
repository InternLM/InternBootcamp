#!/usr/bin/env python3
"""
批量数据生成脚本
从jsonlines配置文件中读取多个配置，批量调用generate_data_with_config函数生成数据
"""

import json
import argparse
import os
import sys
from typing import Dict, Any, List
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
import traceback
import multiprocessing
import psutil
from tqdm import tqdm
import glob
import random

from internbootcamp.utils.data_generation import generate_data_with_config, parse_split_samples
from internbootcamp.utils.format_time_now import format_time_now

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_generation.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def validate_config(config: Dict[str, Any], line_num: int) -> bool:
    """
    验证单个配置项的有效性
    
    Args:
        config: 配置字典
        line_num: 行号（用于错误报告）
        
    Returns:
        bool: 配置是否有效
    """
    required_fields = ['instruction_config_path']
    
    # 检查必需字段
    for field in required_fields:
        if field not in config:
            logger.error(f"第 {line_num} 行配置缺少必需字段: {field}")
            return False
            
        if not isinstance(config[field], str) or not config[field].strip():
            logger.error(f"第 {line_num} 行配置中 {field} 必须是非空字符串")
            return False
    
    # 检查文件路径是否存在
    if not os.path.exists(config['instruction_config_path']):
        logger.error(f"第 {line_num} 行配置中指令配置文件不存在: {config['instruction_config_path']}")
        return False
    
    # 检查可选的文件路径
    optional_file_fields = ['tool_config_path', 'interaction_config_path', 'yaml_tool_path', 'yaml_interaction_path']
    for field in optional_file_fields:
        if field in config and config[field] is not None:
            if not os.path.exists(config[field]):
                logger.error(f"第 {line_num} 行配置中 {field} 文件不存在: {config[field]}")
                return False
    
    # 验证split_samples格式
    if 'split_samples' in config and config['split_samples'] is not None:
        split_samples = config['split_samples']
        if isinstance(split_samples, str):
            # 如果是字符串，尝试解析
            try:
                config['split_samples'] = parse_split_samples(split_samples)
            except Exception as e:
                logger.error(f"第 {line_num} 行配置中 split_samples 格式错误: {e}")
                return False
        elif not isinstance(split_samples, dict):
            logger.error(f"第 {line_num} 行配置中 split_samples 必须是字典或字符串格式")
            return False
    
    # 验证布尔类型字段
    bool_fields = ['shuffle', 'gen_parquet']
    for field in bool_fields:
        if field in config and config[field] is not None:
            if not isinstance(config[field], bool):
                logger.error(f"第 {line_num} 行配置中 {field} 必须是布尔值")
                return False
    
    return True


def load_batch_configs(config_file: str) -> List[Dict[str, Any]]:
    """
    从jsonlines文件加载批量配置
    
    Args:
        config_file: jsonlines bootcamp注册表路径
        
    Returns:
        List[Dict]: 有效的bootcamp注册表列表
    """
    configs = []
    
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"bootcamp注册表不存在: {config_file}")
    
    logger.info(f"开始加载bootcamp注册表: {config_file}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:  # 跳过空行
                continue
                
            try:
                config = json.loads(line)
                if validate_config(config, line_num):
                    configs.append(config)
                    # logger.info(f"成功加载第 {line_num} 行配置")
                else:
                    logger.warning(f"跳过第 {line_num} 行无效配置")
            except json.JSONDecodeError as e:
                logger.error(f"第 {line_num} 行JSON解析错误: {e}")
                continue
    
    logger.info(f"共加载 {len(configs)} 个有效配置")
    return configs


def generate_single_config(config: Dict[str, Any], config_index: int, output_dir: str = 'data/generated', split_samples: str = 'train:1000,test:100', no_tool: bool = False, no_interaction: bool = False) -> Dict[str, Any]:
    """
    执行单个配置的数据生成（多进程兼容版本）
    
    Args:
        config: 数据生成配置
        config_index: 配置索引（用于日志）
        output_dir: 输出目录
        split_samples: 数据集分割比例
        
    Returns:
        Dict: 执行结果
    """
    # 在多进程环境中，每个进程需要重新配置日志
    import logging
    import sys
    
    # 为子进程配置日志
    process_logger = logging.getLogger(f'worker_{config_index}')
    if not process_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        process_logger.addHandler(handler)
        process_logger.setLevel(logging.INFO)
    
    result = {
        'config_index': config_index,
        'success': False,
        'error_message': None,
        'output_info': None
    }
    
    try:
        # process_logger.info(f"开始执行配置 {config_index + 1}: {config.get('instruction_config_path', 'Unknown')}")
        
        # 准备参数
        kwargs = {
            'instruction_config_path': config['instruction_config_path'],
            'output_dir': config['output_dir'] if 'output_dir' in config else output_dir,
            'tool_config_path': config.get('tool_config_path') or config.get('yaml_tool_path'),
            'interaction_config_path': config.get('interaction_config_path') or config.get('yaml_interaction_path'),
            'split_samples': config.get('split_samples') if 'split_samples' in config else split_samples,
            'shuffle': config.get('shuffle', True),
            'gen_parquet': config.get('gen_parquet', False),
            'global_config_overrides': config.get('global_config_overrides', {}),
            'no_tool': no_tool,
            'no_interaction': no_interaction
        }
        
        # 确保split_samples是字典格式
        if isinstance(kwargs['split_samples'], str):
            kwargs['split_samples'] = parse_split_samples(kwargs['split_samples'])
        
        # 执行数据生成
        generate_data_with_config(**kwargs)
        
        result['success'] = True
        result['output_info'] = f"数据已生成到: {config['output_dir'] if 'output_dir' in config else output_dir}"
        # process_logger.info(f"配置 {config_index + 1} 执行成功")
        
    except Exception as e:
        error_msg = f"配置 {config_index + 1} 执行失败: {str(e)}"
        process_logger.error(error_msg)
        # process_logger.error(traceback.format_exc())
        result['error_message'] = error_msg
    
    return result


def concatenate_generated_files(output_dir: str, configs: List[Dict[str, Any]], target_dir: str, time_stamp: str) -> None:
    """
    将所有生成的数据文件合并到对应的split.jsonl中，并打乱数据顺序
    
    Args:
        output_dir: 基础输出目录
        configs: 配置列表，用于获取每个配置的输出目录
        target_dir: 合并文件的目标目录
        time_stamp: 时间戳，用于生成合并文件名
    """
    import tempfile
    import shutil
    import json
    
    logger.info("开始合并生成的数据文件...")
    
    # 收集所有输出目录
    output_dirs = set()
    for config in configs:
        config_output_dir = config.get('output_dir', output_dir)
        output_dirs.add(config_output_dir)
    
    # 动态发现所有split类型
    discovered_splits = set()
    all_jsonl_files = []
    
    # 扫描所有输出目录，发现文件并提取split类型
    for config_output_dir in output_dirs:
        if not os.path.exists(config_output_dir):
            logger.warning(f"输出目录不存在: {config_output_dir}")
            continue
            
        # 查找所有jsonl文件
        pattern = os.path.join(config_output_dir, "*.jsonl")
        jsonl_files = glob.glob(pattern)
        
        for jsonl_file in jsonl_files:
            # 从文件名中提取split类型
            # 假设文件名格式为: *_split.jsonl 或 split.jsonl
            base_name = os.path.basename(jsonl_file)
            name_without_ext = os.path.splitext(base_name)[0]
            
            # 尝试不同的split提取方式
            split_name = None
            if '_' in name_without_ext:
                # 格式: prefix_split
                split_name = name_without_ext.split('_')[-1]
            else:
                # 格式: split
                split_name = name_without_ext
            
            if split_name:
                discovered_splits.add(split_name)
                all_jsonl_files.append((jsonl_file, split_name))
    
    if not discovered_splits:
        logger.warning("没有发现任何数据文件")
        return
    
    logger.info(f"发现的split类型: {sorted(discovered_splits)}")
    
    # 确保目标目录存在
    os.makedirs(target_dir, exist_ok=True)
    
    # 为每个split处理数据
    total_records = 0
    split_counts = {}
    
    for split in sorted(discovered_splits):
        logger.info(f"处理split: {split}")
        
        # 收集该split的所有文件
        split_files = [file_path for file_path, file_split in all_jsonl_files if file_split == split]
        
        if not split_files:
            continue
        
        # 使用临时文件确保原子性写入
        merged_file_path = os.path.join(target_dir, f"{time_stamp}_{split}.jsonl")
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, 
                                       dir=target_dir, prefix=f'tmp_{time_stamp}_{split}_') as temp_file:
            temp_file_path = temp_file.name
            
            try:
                # 收集所有数据行进行打乱
                all_lines = []
                split_record_count = 0
                
                for jsonl_file in split_files:
                    if not os.path.exists(jsonl_file):
                        logger.warning(f"文件不存在: {jsonl_file}")
                        continue
                    
                    try:
                        with open(jsonl_file, 'r', encoding='utf-8') as f:
                            for line_num, line in enumerate(f, 1):
                                line = line.strip()
                                if not line:  # 跳过空行
                                    continue
                                
                                # 验证JSON格式
                                try:
                                    json.loads(line)
                                    all_lines.append(line)
                                    split_record_count += 1
                                except json.JSONDecodeError as e:
                                    logger.warning(f"文件 {jsonl_file} 第 {line_num} 行JSON格式错误: {e}")
                                    continue
                                    
                    except Exception as e:
                        logger.error(f"读取文件 {jsonl_file} 时出错: {e}")
                        continue
                
                # 如果有数据，则打乱并写入临时文件
                if all_lines:
                    logger.info(f"正在打乱 {len(all_lines)} 条 {split} 数据...")
                    random.shuffle(all_lines)
                    
                    # 分批写入，避免内存问题
                    batch_size = 10000
                    for i in range(0, len(all_lines), batch_size):
                        batch = all_lines[i:i + batch_size]
                        for line in batch:
                            temp_file.write(line + '\n')
                        
                        # 每批次后刷新缓冲区
                        temp_file.flush()
                    
                    split_counts[split] = split_record_count
                    total_records += split_record_count
                    
                    # 原子性移动临时文件到最终位置
                    temp_file.close()
                    shutil.move(temp_file_path, merged_file_path)
                    logger.info(f"{split} 数据合并完成: {split_record_count} 条记录 -> {merged_file_path}")
                    
                else:
                    logger.warning(f"没有找到有效的 {split} 数据")
                    temp_file.close()
                    os.unlink(temp_file_path)  # 删除空的临时文件
                    
            except Exception as e:
                # 清理临时文件
                temp_file.close()
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                logger.error(f"处理 {split} 数据时发生错误: {e}")
                raise
    
    # 输出统计信息
    if split_counts:
        logger.info("=== 文件合并统计 ===")
        for split, count in sorted(split_counts.items()):
            logger.info(f"{split}: {count} 条记录")
        logger.info(f"总计: {total_records} 条记录")
        logger.info("文件合并和打乱完成！")
    else:
        logger.warning("没有成功合并任何数据文件")

def batch_generate_data(
    config_file: str,
    max_workers: int = 1,
    continue_on_error: bool = True,
    output_dir: str = 'data/generated',
    split_samples: str = 'train:1000,test:100',
    concat_files: bool = False,
    no_tool: bool = False,
    no_interaction: bool = False
) -> List[Dict[str, Any]]:
    """
    批量生成数据
    
    Args:
        config_file: jsonlines配置文件路径
        max_workers: 最大并行工作线程数
        continue_on_error: 遇到错误时是否继续执行其他配置
        output_dir: 输出目录
        split_samples: 数据集分割比例
        concat_files: 是否将所有生成的文件合并到train.jsonl和test.jsonl

    Returns:
        List[Dict]: 所有配置的执行结果
    """
    time_stamp = format_time_now()
    
    # 加载配置
    configs = load_batch_configs(config_file)
    
    if not configs:
        logger.warning("没有找到有效的配置，退出执行")
        return []
    
    if max_workers == 1:
        logger.info(f"开始批量生成数据，共 {len(configs)} 个配置，采用单进程顺序执行")
    else:
        logger.info(f"开始批量生成数据，共 {len(configs)} 个配置，最大并行进程数: {max_workers}")
    
    if concat_files:
        output_detail_dir = os.path.join(output_dir, f"detail_{time_stamp}")
        os.makedirs(output_detail_dir, exist_ok=True)
        target_dir = output_dir
        output_dir = output_detail_dir
    
    results = []
    
    if max_workers == 1:
        # 单进程顺序执行
        progress_bar = tqdm(total=len(configs), desc="数据生成进度", unit="配置")
        for i, config in enumerate(configs):
            # 更新进度条描述
            progress_bar.set_description(f"执行配置 {i+1}/{len(configs)}")
            
            result = generate_single_config(config, i, output_dir, split_samples, no_tool, no_interaction)
            results.append(result)
            
            # 更新进度条
            if result['success']:
                progress_bar.set_postfix(状态="成功", 当前="配置"+str(i+1))
            else:
                progress_bar.set_postfix(状态="失败", 当前="配置"+str(i+1))
            progress_bar.update(1)
            
            if not result['success'] and not continue_on_error:
                logger.error("遇到错误，停止执行后续配置")
                break
        progress_bar.close()
    else:
        # 多进程并行执行
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_config = {
                executor.submit(generate_single_config, config, i, output_dir, split_samples, no_tool, no_interaction): (config, i)
                for i, config in enumerate(configs)
            }
            
            # 初始化进度条
            progress_bar = tqdm(total=len(configs), desc="数据生成进度", unit="配置")
            completed_count = 0
            success_count = 0
            
            # 收集结果
            for future in as_completed(future_to_config):
                try:
                    result = future.result()
                    results.append(result)
                    completed_count += 1
                    
                    if result['success']:
                        success_count += 1
                        progress_bar.set_postfix(
                            已完成=f"{completed_count}/{len(configs)}", 
                            成功=success_count, 
                            失败=completed_count-success_count
                        )
                    else:
                        progress_bar.set_postfix(
                            已完成=f"{completed_count}/{len(configs)}", 
                            成功=success_count, 
                            失败=completed_count-success_count
                        )
                    
                    progress_bar.update(1)
                    
                    if not result['success'] and not continue_on_error:
                        logger.error("遇到错误，终止剩余任务")
                        # 在多进程中，取消任务的行为有所不同
                        for f in future_to_config:
                            if not f.done():
                                f.cancel()
                        break
                except Exception as e:
                    # 处理进程执行过程中的异常
                    config, i = future_to_config[future]
                    error_result = {
                        'config_index': i,
                        'success': False,
                        'error_message': f"进程执行异常: {str(e)}",
                        'output_info': None
                    }
                    results.append(error_result)
                    completed_count += 1
                    
                    progress_bar.set_postfix(
                        已完成=f"{completed_count}/{len(configs)}", 
                        成功=success_count, 
                        失败=completed_count-success_count
                    )
                    progress_bar.update(1)
                    
                    logger.error(f"配置 {i + 1} 进程执行异常: {str(e)}")
                    
                    if not continue_on_error:
                        logger.error("遇到进程异常，终止剩余任务")
                        break
            
            progress_bar.close()
    
    # 按配置索引排序结果
    results.sort(key=lambda x: x['config_index'])
    
    # 统计结果
    success_count = sum(1 for r in results if r['success'])
    failure_count = len(results) - success_count
    
    logger.info(f"批量生成完成！成功: {success_count}, 失败: {failure_count}")
    
    # 输出失败的配置信息
    if failure_count > 0:
        logger.error("失败的配置:")
        for result in results:
            if not result['success']:
                logger.error(f"  配置 {result['config_index'] + 1}: {result['error_message']}")
    
    # 如果启用了文件合并功能且有成功的配置，则进行文件合并
    if concat_files and success_count > 0:
        try:
            concatenate_generated_files(output_dir, configs, target_dir, time_stamp)
        except Exception as e:
            logger.error(f"文件合并过程中发生错误: {e}")
            logger.error(traceback.format_exc())
    
    return results


def main():
    """主函数"""
    # 设置多进程启动方法（对某些平台很重要）
    if hasattr(multiprocessing, 'set_start_method'):
        try:
            multiprocessing.set_start_method('spawn', force=True)
        except RuntimeError:
            # 如果已经设置过，忽略错误
            pass
    
    parser = argparse.ArgumentParser(description="批量数据生成脚本")
    parser.add_argument(
        '--bootcamp-registry', 
        type=str, 
        required=True, 
        help='bootcamp注册表文件路径'
    )
    parser.add_argument(
        '--max-workers', 
        type=int, 
        default=min(16, multiprocessing.cpu_count()), 
        help=f'最大并行工作进程数 (默认: {min(16, multiprocessing.cpu_count())}，CPU核心数: {multiprocessing.cpu_count()})'
    )
    parser.add_argument(
        '--continue-on-error', 
        action='store_true', 
        help='遇到错误时继续执行其他配置'
    )
    parser.add_argument(
        '--log-level', 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
        default='INFO',
        help='日志级别'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/generated',
        help='输出目录'
    )
    parser.add_argument(
        '--split-samples',
        type=str,
        default='train:100,test:0',
        help='数据集分割比例'
    )
    parser.add_argument(
        '--concat-files',
        action='store_true',
        help='是否将所有生成的文件合并到train.jsonl和test.jsonl两个文件中'
    )
    parser.add_argument(
        '--no-tool',
        action='store_true',
        help='是否不使用工具'
    )
    parser.add_argument(
        '--no-interaction',
        action='store_true',
        help='是否不使用交互'
    )
    args = parser.parse_args()
    
    # 设置日志级别
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    def get_usable_cpu_count():
        try:
            # 获取当前进程实际可用的 CPU 核心数
            return len(psutil.Process().cpu_affinity())
        except Exception:
            # 降级方案：尝试 cpu_count
            return psutil.cpu_count(logical=True) or 1
    cpu_count = get_usable_cpu_count()
    max_workers = min(args.max_workers, cpu_count)
    if max_workers < args.max_workers:
        print(f'Note: System has only {cpu_count} CPU. '
            f'Max workers adjusted from {args.max_workers} to {max_workers}.')
    
    try:
        results = batch_generate_data(
            config_file=args.bootcamp_registry,
            max_workers=max_workers,
            continue_on_error=args.continue_on_error,
            output_dir=args.output_dir,
            split_samples=args.split_samples,
            concat_files=args.concat_files,
            no_tool=args.no_tool,
            no_interaction=args.no_interaction
        )
        
        # 输出结果摘要
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)
        
        print(f"\n=== 批量生成结果摘要 ===")
        print(f"总配置数: {total_count}")
        print(f"成功数: {success_count}")
        print(f"失败数: {total_count - success_count}")
        print(f"成功率: {success_count/total_count*100:.1f}%" if total_count > 0 else "0%")
        
        # 返回适当的退出码
        sys.exit(0 if success_count == total_count else 1)
        
    except Exception as e:
        logger.error(f"批量生成过程中发生严重错误: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    # 多进程保护 - 确保子进程不会重复执行主程序
    multiprocessing.freeze_support()
    main() 