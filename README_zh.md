# InternBootcamp

<p align="center">
  <a href="https://arxiv.org/pdf/2508.08636">📄 论文</a> •
  <a href="https://github.com/InternLM/InternBootcamp">⭐ Github</a> •
  <a href="examples/data/Intenbootcamp_eval">📊 评测数据</a> • 
  <a href="https://intern.openxlab.org.cn/internthinker/go-game">⚪ Internthinker-Go</a> 
</p>

<p align="center">
🌍 <a href="./README.md">English</a> | <a href="./README_zh.md">简体中文</a>
</p>

<p align="center">
<img src="./figs/logo.png " width=400/> 
</p>

InternBootcamp 是一个开源框架，包含 **1000+ 个领域多样的任务环境**，专为大型语言模型（LLM）推理研究而设计。通过集成可配置难度级别的无限训练/测试数据自动生成以及内置验证模块，InternBootcamp 可作为**基于强化学习的模型优化**、**合成数据生成**和**模型评估**的基础设施。

我们的核心创新在于证明了在训练过程中扩展可验证推理任务的数量能显著提升推理性能和训练效率——这一现象我们称之为 **“任务缩放”（Task Scaling）** 📈。目前，InternBootcamp 涵盖了 8 个不同领域的可验证推理任务，包括算法、密码学、自然科学、语言分析、数学建模、图形谜题、逻辑推理和字符谜题等相关问题。我们正持续努力并与社区共同扩展其范围。

## 🚀 快速开始

快速开始数据生成、强化学习训练、模型评估以及自定义 Bootcamp 的创建！

- [安装](#安装)
- [快速开始](examples/get_started.md)
- [接口与用法](#接口与用法)
- [Bootcamp-Eval 数据集](#examples/data/Intenbootcamp_eval)

## 📢 更新日志

- 📦 **[2025/08] v1.0 版本发布！**
- 📄 **[2025/08] [InternBootcamp 技术报告：通过可验证的任务缩放提升LLM推理能力](https://arxiv.org/pdf/2508.08636) 发布。**
- 🌱 **[2025/04] v0.1 版本发布。**

## 🧩 关于

大规模强化学习已被证明是通向专家级推理模型的有效途径。当前推进这一技术路线的大多数努力都集中在有限的任务上（例如数学），并专注于设计改进的训练算法。互补地，我们认为对**任务缩放**（让模型接触广泛且不断增长的推理任务谱系）的研究对于构建通用且鲁棒的推理模型至关重要：

- 包含更多类型的任务可以覆盖多样的推理模式，从而带来更通用的智能；
- 研究具有可控难度及其组合的任务有助于理解训练动态，并实现更高效的训练策略。

尽管存在大量潜在有价值的任务，但它们分散在不同的来源中，这使得实践者极难利用它们。为此，我们引入了 InternBootcamp 以促进相关研究并提供工程便利。特别地，我们想强调 InternBootcamp 的以下特点：

- **🔧 标准化：** InternBootcamp 为各种任务提供了统一的接口，易于与不同的代码库集成以进行强化学习或合成数据生成。每个 bootcamp 类都实现了标准化的方法来生成问题和验证解决方案，可以与强化学习或合成数据管道无缝集成。

- **📊 自动化：** 得益于用于 bootcamp 合成的自动智能体工作流，InternBootcamp 已经发展到包含大量多样化的 bootcamp 任务。在第一个版本中，它涵盖了 8 个领域的 1000 多个复杂推理任务，包括游戏、逻辑问题、谜题、算法、科学推理等。超过 90% 的这些 bootcamp 是通过自动合成和质量过滤流水线开发的，能够以最少的人工干预持续扩展 bootcamp 环境。此外，InternBootcamp能够自动生成覆盖各类任务的难度可控的指令数据。

- **🧱 可扩展：** InternBootcamp 可以扩展以支持更多样化和复杂的任务（例如，具有多轮交互的任务，如围棋和基于智能体的环境），并为它们提供问题生成和结果验证。代表性的，我们包含了 `InternGObootcamp` 作为演示。

我们还使用 InternBootcamp 进行了一系列强化学习研究。我们的初步发现如下：

- **可扩展的任务合成实现了广泛的经验学习**：我们的自动智能体工作流表明，通过迭代、进化的方法可以有效地合成大规模、多样化的推理环境，为在持续的新任务流上训练智能体打开了大门。
- **泛化能力源于跨任务接触**：LLMs 通过在各种推理任务谱系中学习，而非在狭窄领域深度专精，从而发展出更强的推理泛化和涌现能力。
- **任务缩放同时提高性能和效率**：增加训练任务的数量显著提高了最终性能和学习效率，任务数量与推理能力之间存在近乎线性的关系。
- **InternThinker-GO**：作为单任务训练的代表，我们使用 InternGObootcamp 训练了 `InternThinker-GO`。`InternThinker-GO` 使用远少于 AlphaGO 的对局数接近了职业棋手水平，超越了当前的推理模型。除了优异的性能，`InternThinker-GO` 提供了合理且富有启发性的思考，展示了由强化学习赋能的人类式推理在应对专家级任务方面的巨大潜力。

## 🎯 支持的 Bootcamps

<p align="center">
  <img src="./figs/bootcamps.png" width="1000"/> 
</p>

在第一个版本中，InternBootcamp 已覆盖 **1000+ 个任务** 的 bootcamps，来源包括：

- **🧠 推理基准测试：** 目前，我们已从 [ARC-AGI](https://github.com/fchollet/ARC-AGI), [re-arc](https://github.com/michaelhodel/re-arc), [KOR-Bench](https://kor-bench.github.io/), 和 [BBEH](https://github.com/google-deepmind/bbeh) 这三个代表性推理基准中包含了任务来构建 bootcamps。其中，KOR-Bench 包含五种推理任务类型，即逻辑、操作、密码、谜题和反事实推理，我们忽略了反事实推理（因其依赖于特定的世界观知识），并为其余四种类型的任务构建了 bootcamps。BBEH 是通过复杂化 BBH 中的任务得到的 23 个推理任务，我们为那些不依赖外部知识的任务构建了 bootcamps。

- **🧩 谜题网站：** [puzzle-xxx](https://www.puzzle-aquarium.com/) 是一个系列的谜题网页；我们抓取了其中的 39 个谜题来准备相应的 bootcamps。

- **⚙️ 算法问题：** 算法问题涵盖了各种算法中的推理模式，并且包含接近实际应用的问题。同时，现成的算法问题通常包含参考解决方案，便于将其转换为 bootcamps。目前，我们使用 [CodeContests](https://huggingface.co/datasets/deepmind/code_contests) 并选择了 1265 个中等难度（codeforces 分数在 1000 到 2000 之间）的任务，应用我们的自动工作流来构建相应的 bootcamps。此外，我们还改编了来自 [CodeIO](https://codei-o.github.io/) 的任务，它将基于代码的推理转化为自然语言，以评估大语言模型的推理能力。

- **💻 编程能力基准测试：** 目前，我们已经从 [BigCodeBench](https://bigcode-bench.github.io/) 和 [KodCode](https://kodcode-ai.github.io/) 这两个代表性的编程基准测试中包含了任务来构建 bootcamps。这些基准测试具有多样化和具有挑战性的问题，要求语言模型生成正确的代码。对于每个任务，我们收集或改编了一个 `unittest` 脚本来验证解决方案的正确性。

- **📋 指令遵循：** 这些任务测试模型理解和严格遵守任务描述中嵌入指令的能力。在许多情况下，可以通过代码执行反馈来评估正确性。我们包含了来自 [AutoIF](https://github.com/QwenLM/AutoIF) 的任务，它包含超过 60,000 个指令-评估函数对，每个都被视为一个独立的任务。

- **🎮 游戏：** 游戏是一种复杂的推理任务，涉及多轮交互，具有可控和可验证的目标。作为代表，我们构建了 `InternGObootcamp` 来训练一个用于围棋的推理模型。

- **🔬 科学任务：** 科学任务代表了一系列与科学研究活动深度交织的推理密集型工作，这被视为人工智能将革命性改变的最有价值领域之一。我们认为改进模型在这些任务上的推理能力有助于实现这一愿景。部分科学任务集的构建得到了 [Intern-S1](https://arxiv.org/pdf/2508.15763) 团队的支持，作为回报，InternBootcamp 也为 Intern-S1 提供训练支持。

我们正在持续努力，并呼吁社区验证自动生成的 bootcamps。我们在下方展示了 bootcamps 的完整列表（[完整 bootcamp 列表](./Fulllist_InternBootcamp.md)）并说明了我们的自动工作流。

## 🤖 大规模 Bootcamp 合成的自动智能体工作流

<p align="center">
  <img src="./figs/workflow.png" width="1000"/> 
</p>

为每个任务手动编写 bootcamp 代码效率低下且不可扩展。我们引入了一个**自动智能体工作流**，利用大语言模型根据任务描述生成 bootcamp 代码。该流水线包括：

1.  **📥 任务描述收集：** 识别可验证的任务（谜题、推理基准、算法问题等）并收集它们的描述和支持信息。
2.  **🔄 进化式代码生成：** 使用强大的代码模型（例如 Deepseek-R1）迭代生成 bootcamp 代码，结合执行反馈以避免过度简化和错误信息。
3.  **✅ 自洽单元测试过滤：** 利用Bootcamp自身的验证器评估语言模型的回复，通过检测是否能正确执行以及模型回复的通过率作为单元测试。准确率超出 [0.03, 0.85] 范围的 bootcamps 将被过滤掉。

该工作流已实现快速扩展到 1000+ 个高质量、多样化的 bootcamps。

## 🛠 接口与用法

每个 bootcamp 继承自 `BaseBootcamp`，并包含三个主要接口：`case_generator`、`prompt_func` 和 `verify_func`，用于服务问题生成和结果验证。

<p align="center">
  <img src="./figs/bootcamp-framework.png" width="1000"/> 
</p>

### 安装 <a id="安装"></a>

```bash
git clone https://github.com/InternLM/InternBootcamp.git 
cd InternBootcamp
pip install -e .
```

### 示例：Game24Bootcamp <a id="接口与用法"></a>

24点是一类算术谜题，需使用 `num_numbers` 个数字（每个 ≤ `range_max`）和基本运算来获得 `target` 值（≤ `target_max`）。

#### 生成问题

```python
from internbootcamp import Game24Bootcamp

# 指定难度参数
bootcamp = Game24Bootcamp(num_numbers=4, range_max=100, target_max=100, seed=42)

# 或者使用默认配置
# bootcamp_default = Game24Bootcamp()

identity = bootcamp.case_generator()
prompt = bootcamp.prompt_func(identity)

# 示例输出:
# - identity: {'puzzle': '8 43 65 77', 'target': 28} 
# - prompt: "请解决这个谜题：使用 8, 43, 65, 77 通过基本算术运算得到 28..."
```

#### 验证结果

```python
response = "...一些推理过程...\\boxed{77 / (65 - 43) * 8}"
score = Game24Bootcamp.verify_score(response, identity, format_score=0.1)
```

### 扩展到更多任务

您可以通过继承 `BaseBootcamp` 类来轻松添加新任务。详见 [examples/README.md](examples/README.md)。

### 强化学习

InternBootcamp 可以轻松与 RL 框架集成。详见 [examples/README.md](examples/README.md)。

## 🧪 实验：通过可验证的任务缩放提升 LLM 推理

我们进行了大量实验，以研究**任务缩放**（使用越来越多和多样化的推理任务进行训练）如何增强大语言模型的推理能力。我们的研究结果表明，任务缩放不仅提高了最终性能，而且显著提升了训练效率。

<p align="center">
  <img src="./figs/overall.png" width="800"/> 
</p>

通过系统地缩放训练任务，我们观察到模型在不同推理领域的性能持续提升。使用更多任务训练的模型在我们的 Bootcamp-Eval 基准测试上实现了更好的泛化能力和更高的准确率，展示了任务缩放在开发多功能推理模型方面的有效性。同时，我们发现扩增训练任务的数量能够在强化学习过程中有效提升训练的效率。

此外，我们发现多任务训练能够实现一个**涌现时刻**（Emergent Moment）——当与其他任务一起训练时，那些孤立情况下无法解决的任务突然变得可学习。这种现象表明，跨任务知识转移培养了潜在的泛化能力，使模型能够应对原本无法解决的复杂挑战。

<p align="center">
  <img src="./figs/emergent.png" width="800"/> 
</p>

📌 详细的实验结果和全面分析，欢迎参阅我们的[技术报告](https://arxiv.org/pdf/2508.08636) 📝。

## ⚫ 演示：[InternThinker-围棋](https://intern.openxlab.org.cn/internthinker/go-game)

LLMs 在广泛的常见推理任务上已经展现出卓越的性能。然而，作为最早引发 AI 热潮的研究问题之一，通用 LLMs 在**围棋**这一特定领域的推理能力却很少受到研究关注。虽然 AlphaZero 从“无需人类知识掌握围棋游戏”的角度挑战了人类智能，但我们探索如何将人类智能带回这个古老的游戏，让人类独有的自然语言思维模式在 LLMs 的新背景下再次闪耀。基于 InternBootcamp，我们实现了一个用于推理模型强化学习的围棋 bootcamp，使用专业围棋领域数据冷启动，并通过强化学习强化了模型的推理范式。我们的模型达到了与职业围棋选手相当的性能 - InternThinker-GO 可以稳定击败业余 6 段水平的 Golaxy AI 并接近职业 1 星水平，使其成为首个达到此性能水平的通用大语言模型。

<p align="center">
  <img src="figs/demo_internthinkerGO.png" width="1000"/> 
</p>

对于给定的局面，InternThinker-GO 首先分析棋盘形势：*“右上角存在复杂的战斗区域，黑白双方都有多颗棋子。左下角有一些交错的的黑白棋子，形成了一定的结构。黑棋沿着左边有阵型。黑棋刚刚在第 65 手下了 B14，这明显是为了侵入白棋左边的地盘。作为白棋，我需要小心应对这个威胁。”* 接下来，InternThinker-GO 具体预测并分析了 B13、C13 等潜在落点，并最终选择 B13 作为落子位置。


## 🙏 致谢

我们向以下工作表示感谢，它们为本项目提供了重要的启发和工具支持：

- [Intern-S1](https://github.com/InternLM/Intern-S1)
- [VeRL](https://github.com/volcengine/verl)
- [Xtuner](https://github.com/InternLM/xtuner)
- [OpenCompass](https://github.com/open-compass/opencompass)

## 📜 引用

如果您觉得我们的工作有帮助，请引用：

```bibtex
@misc{li2025internbootcamptechnicalreportboosting,
      title={InternBootcamp Technical Report: Boosting LLM Reasoning with Verifiable Task Scaling}, 
      author={Peiji Li and Jiasheng Ye and Yongkang Chen and Yichuan Ma and Zijie Yu and Kedi Chen and Ganqu Cui and Haozhan Li and Jiacheng Chen and Chengqi Lyu and Wenwei Zhang and Linyang Li and Qipeng Guo and Dahua Lin and Bowen Zhou and Kai Chen},
      year={2025},
      eprint={2508.08636},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2508.08636}, 
}
```