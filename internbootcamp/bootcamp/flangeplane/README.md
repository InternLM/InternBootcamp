# FlangePlaneBootcamp 使用说明

本 Readme 面向需要在 Internbootcamp V1 框架中新增一个自定义 Bootcamp（以“FlangePlaneBootcamp”为例）的使用者，涵盖环境搭建、FreeCAD 集成、代码修改点、数据预处理流水线与评测方法。请在阅读前确保你已正确安装并可运行 [Internbootcamp 主仓库](https://gitlab.pjlab.org.cn/lilinyang/internbootcamp)。

若你首次接触 Internbootcamp，推荐先阅读仓库根目录下的 README_zh.md，了解 Bootcamp 的统一接口：`case_generator`、`prompt_func`、`verify_score`。

---

## 目录
- 1. 环境准备
- 2. FreeCAD 集成
- 3. 代码结构与修改点
- 4. 数据预处理与生成
- 5. 评测与基线脚本
- 6. 常见问题与建议

---

## 1. 环境准备

建议使用 Conda 独立环境（例如Python 3.10）：

- 创建环境并安装依赖
  - `conda create -n [yourEnv] python==3.10`
  - `conda activate [yourEnv]`
  - `pip install openpyxl==3.1.3 numpy==1.23.5 pandas==1.5.3 matplotlib==3.5.3 trimesh==4.4.1`
  - `conda install -c conda-forge pythonocc-core==7.9.0`

---

## 2. FreeCAD 集成

FlangePlaneBootcamp 依赖 FreeCAD 的本地解压版本（AppImage 提取的 `squashfs-root`）。请按以下步骤安装并集成：

- 下载 AppImage
  - 前往 https://www.freecad.org/downloads.php 下载linux版的 FreeCAD（`FreeCAD_1.0.1-conda-Linux-x86_64-py311.AppImage`）

- 赋予执行权限并解包
  - `chmod +x FreeCAD_1.0.1-conda-Linux-x86_64-py311.AppImage`
  - `./FreeCAD_1.0.1-conda-Linux-x86_64-py311.AppImage --appimage-extract`

- 放置解包目录
  - 将生成的 `squashfs-root` 目录整体移动至：
    - `internbootcamp/bootcamp/flangeplane/DeepCAD/squashfs-root`

---

## 3. 代码结构与修改点

为注册并启用新的 Bootcamp 类，请确认/编辑以下文件：

- `internbootcamp/bootcamp/__init__.py`
  - 在此处导入并注册 `FlangePlaneBootcamp`

- `internbootcamp/bootcamp/flangeplane/flangeplane.py`
  - 核心实现文件。需实现继承 `Basebootcamp` 的类，至少包含：
    - `case_generator(self) -> dict`
    - `prompt_func(self, identity: dict) -> str`
    - `extract_output(output: str) -> str|None`
    - `_verify_correction(self, solution: str|None, identity: dict) -> float`

- `examples/pipelines/puzzle_configs/flange_plane_train.json`
- `examples/pipelines/puzzle_configs/flange_plane_test.json`
- `examples/pipelines/data_configs/data_config_train_flangeplane.jsonl`
- `examples/pipelines/data_configs/data_config_test_flangeplane.jsonl`
  - 定义训练/测试集的数据生成配置

- 其他资源
  - “DeepCAD” 目录（含 FreeCAD 解包目录 `squashfs-root`）用于承载与 CAD 解析相关的依赖与脚本。请确保其放在 `internbootcamp/bootcamp/flangeplane` 下。

---

## 4. 数据预处理与生成

新增 Bootcamp 的数据集生成通过 pipeline 脚本完成：

- 编辑并运行脚本
  - `bash examples/pipelines/run_pipeline_flangeplane.sh`

- 训练集与测试集将生成在`examples/bootcamp_generator_outputs`

---

## 5. 评测与基线脚本

完成数据生成后，可使用仓库内的统一评测脚本进行模型评测。示例命令如下（以 DeepSeek API 为例）：

```bash
python examples/unittests/run_eval.py \
  --url https://api.deepseek.com/v1/ \
  --api_key YOUR_API_KEY \
  --model_name deepseek-reasoner \
  --test_dir /root/cpfs/code/internbootcamp/examples/bootcamp_generator_outputs/test_dir_name/test \
  --max_concurrent_requests 128 \
  --template r1 \
  --max_tokens 32768 \
  --temperature 0.6 \
  --api_mode chat_completion \
  --max_retries 64 \
  --max_retrying_delay 60 \
  --timeout 6000