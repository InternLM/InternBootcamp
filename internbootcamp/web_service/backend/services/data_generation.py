"""
数据生成服务
"""
import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Optional


class DataGenerationService:
    """数据生成服务"""
    
    @staticmethod
    async def generate_data(
        instruction_config: str,
        output_dir: str,
        split_samples: Optional[str] = None,
        shuffle: bool = True,
        gen_parquet: bool = False,
        no_tool: bool = False,
        no_interaction: bool = False,
        log_path: Optional[str] = None,
    ) -> None:
        """
        执行数据生成任务
        
        Args:
            instruction_config: 指令配置文件路径
            output_dir: 输出目录
            split_samples: 数据集划分
            shuffle: 是否打乱
            gen_parquet: 是否生成parquet
            no_tool: 不使用工具
            no_interaction: 不使用交互
            log_path: 日志文件路径
        """
        # 构建命令
        cmd = [
            sys.executable, "-m", "internbootcamp.utils.data_generation",
            "--instruction-config", instruction_config,
            "--output-dir", output_dir,
        ]
        
        if split_samples:
            cmd.extend(["--split-samples", split_samples])
        
        if shuffle:
            cmd.append("--shuffle")
        
        if gen_parquet:
            cmd.append("--gen-parquet")
        
        if no_tool:
            cmd.append("--no-tool")
        
        if no_interaction:
            cmd.append("--no-interaction")
        
        # 执行命令
        if log_path:
            with open(log_path, 'w', encoding='utf-8') as log_file:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                )
                await process.wait()
        else:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            await process.wait()
        
        if process.returncode != 0:
            raise RuntimeError(f"Data generation failed with return code {process.returncode}")

