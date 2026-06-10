#!/usr/bin/env python3
"""
YAML文件列表合并脚本

该脚本可以将指定目录下所有以指定后缀结尾的yaml文件中的指定yaml列表合并到一个新的yaml文件中。

使用示例:
    python merge_yaml_lists.py --source-dir /path/to/yaml/files --suffix _tool_config.yaml --list-key tools --output merged_tools.yaml
    python merge_yaml_lists.py -s . -x .yaml -k interaction -o merged_interactions.yaml
"""

import argparse
import os
import glob
import yaml
from pathlib import Path
from typing import List, Dict, Any, Union
import sys


def load_yaml_file(file_path: str) -> Union[Dict, List, None]:
    """
    加载YAML文件
    
    Args:
        file_path: YAML文件路径
        
    Returns:
        解析后的YAML内容，如果文件无法解析则返回None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"警告: 无法解析文件 {file_path}: {e}")
        return None


def save_yaml_file(data: Any, file_path: str) -> bool:
    """
    保存数据到YAML文件
    
    Args:
        data: 要保存的数据
        file_path: 输出文件路径
        
    Returns:
        保存成功返回True，否则返回False
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
        return True
    except Exception as e:
        print(f"错误: 无法保存文件 {file_path}: {e}")
        return False


def find_yaml_files(source_dir: str, suffix: str) -> List[str]:
    """
    查找指定目录下符合后缀条件的YAML文件
    
    Args:
        source_dir: 源目录路径
        suffix: 文件后缀（如：_tool_config.yaml）
        
    Returns:
        符合条件的文件路径列表
    """
    pattern = os.path.join(source_dir, "**", f"*{suffix}")
    files = glob.glob(pattern, recursive=True)
    return sorted(files)


def extract_list_from_yaml(yaml_data: Union[Dict, List], list_key: str) -> List[Any]:
    """
    从YAML数据中提取指定键的列表
    
    Args:
        yaml_data: YAML数据
        list_key: 列表键名
        
    Returns:
        提取的列表，如果键不存在或不是列表则返回空列表
    """
    if isinstance(yaml_data, dict) and list_key in yaml_data:
        value = yaml_data[list_key]
        if isinstance(value, list):
            return value
        else:
            print(f"警告: 键 '{list_key}' 的值不是列表类型")
            return []
    return []


def merge_yaml_lists(source_dir: str, suffix: str, list_key: str, output_file: str, 
                    preserve_structure: bool = True) -> bool:
    """
    合并YAML文件中的指定列表
    
    Args:
        source_dir: 源目录路径
        suffix: 文件后缀
        list_key: 要合并的列表键名
        output_file: 输出文件路径
        preserve_structure: 是否保持原有的YAML结构
        
    Returns:
        合并成功返回True，否则返回False
    """
    # 查找所有符合条件的YAML文件
    yaml_files = find_yaml_files(source_dir, suffix)
    
    if not yaml_files:
        print(f"未找到任何以 '{suffix}' 结尾的YAML文件")
        return False
    
    print(f"找到 {len(yaml_files)} 个符合条件的文件:")
    for file_path in yaml_files:
        print(f"  - {file_path}")
    
    # 合并所有列表
    merged_list = []
    processed_files = 0
    
    for file_path in yaml_files:
        yaml_data = load_yaml_file(file_path)
        if yaml_data is None:
            continue
            
        extracted_list = extract_list_from_yaml(yaml_data, list_key)
        if extracted_list:
            merged_list.extend(extracted_list)
            processed_files += 1
            print(f"从 {file_path} 提取了 {len(extracted_list)} 个项目")
    
    print(f"\n总共处理了 {processed_files} 个文件，合并了 {len(merged_list)} 个项目")
    
    # 准备输出数据
    if preserve_structure:
        output_data = {list_key: merged_list}
    else:
        output_data = merged_list
    
    # 保存合并结果
    if save_yaml_file(output_data, output_file):
        print(f"合并结果已保存到: {output_file}")
        return True
    else:
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="合并指定目录下YAML文件中的指定列表",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 合并所有tool_config.yaml文件中的tools列表
  python %(prog)s -s . -x _tool_config.yaml -k tools -o merged_tools.yaml
  
  # 合并所有interaction_config.yaml文件中的interaction列表
  python %(prog)s -s . -x _interaction_config.yaml -k interaction -o merged_interactions.yaml
  
  # 输出为平铺列表（不保持YAML结构）
  python %(prog)s -s . -x .yaml -k items -o output.yaml --no-structure
        """
    )
    
    parser.add_argument(
        '-s', '--source-dir',
        type=str,
        default='.',
        help='源目录路径（默认为当前目录）'
    )
    
    parser.add_argument(
        '-x', '--suffix',
        type=str,
        required=True,
        help='文件后缀（如: _tool_config.yaml, .yaml）'
    )
    
    parser.add_argument(
        '-k', '--list-key',
        type=str,
        required=True,
        help='要合并的列表键名（如: tools, interaction）'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        required=True,
        help='输出文件路径'
    )
    
    parser.add_argument(
        '--no-structure',
        action='store_true',
        help='输出为平铺列表，不保持原有的YAML结构'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='试运行模式，只显示将要处理的文件，不实际合并'
    )
    
    args = parser.parse_args()
    
    # 验证源目录
    if not os.path.isdir(args.source_dir):
        print(f"错误: 源目录不存在: {args.source_dir}")
        sys.exit(1)
    
    # 试运行模式
    if args.dry_run:
        yaml_files = find_yaml_files(args.source_dir, args.suffix)
        print(f"试运行模式: 找到 {len(yaml_files)} 个符合条件的文件:")
        for file_path in yaml_files:
            print(f"  - {file_path}")
        print(f"\n将要合并的列表键: {args.list_key}")
        print(f"输出文件: {args.output}")
        print(f"保持结构: {not args.no_structure}")
        return
    
    # 执行合并
    success = merge_yaml_lists(
        source_dir=args.source_dir,
        suffix=args.suffix,
        list_key=args.list_key,
        output_file=args.output,
        preserve_structure=not args.no_structure
    )
    
    if success:
        print("\n✅ YAML列表合并完成!")
    else:
        print("\n❌ YAML列表合并失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()

# python ${PROJECT_DIR} -s internbootcamp/bootcamps/bootcamps_v1 -x _interaction_config.yaml -k interaction -o merged_interactions.yaml
# python -m  internbootcamp.bootcamps.bootcamps_v1.configs.merge_yaml_lists -s internbootcamp/bootcamps/bootcamps_v1 -x _tool_config.yaml -k tools -o merged_tools.yaml