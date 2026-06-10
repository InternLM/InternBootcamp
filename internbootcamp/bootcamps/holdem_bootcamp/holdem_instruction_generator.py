import random
import math
from typing import Dict, Any, Optional, List
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

from internbootcamp.bootcamps.holdem_bootcamp import ips

import requests


class HoldemInstructionGenerator(BaseInstructionGenerator):    
    def __init__(self, num_players=2):
        self.num_players = num_players
        super().__init__()
        
    def case_generator(self) -> Dict[str, Any]:
        PAYLOAD = {}
        while True:
            try:           
                response = requests.post(f"{random.choice(ips)}/create_game", 
                                        headers={"Content-Type": "application/json"}, 
                                        json=PAYLOAD, 
                                        timeout=120)     
            except requests.exceptions.RequestException as e:
                print(f"Request failed, {e}")
                continue

            if not response.ok:
                print(f"Server returned status {response.status_code}")
                continue

            try:
                return response.json()
            except ValueError:
                print(f"Response is not json format, {response.text}")
                continue

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        game_id, style = identity["game_id"], identity["bot_style"]
        
        if identity["agent_id"] == 0:
            position_role = "小盲"
            action_order = "先手"
            strategy_hint = "作为小盲，你在翻牌前是先手，但在翻牌后将拥有位置优势（后手）"
        else:
            position_role = "大盲"
            action_order = "后手"
            strategy_hint = "作为大盲，你在翻牌前是后手（可以看到对手动作），但在翻牌后将处于劣势位置（先手）"

        prompts = [
f"""
# 德州扑克 AI 决策指令

你正在与一名被标记为【{style}】风格的对手进行德州扑克对局。
当前对局 ID: {game_id}

## 核心任务流程
请严格按照以下步骤执行任务：

### 第一步：会话初始化（仅首次执行）
在进行任何牌局分析或操作之前，你必须先调用 `createGameSession` 工具初始化游戏会话。
*   **目标**：获取本次对局的唯一通行证 **PIN 码**。
*   **注意**：后续所有针对牌局的操作（如 `applyAction`）都必须携带此 PIN 码，否则操作无效。

### 第二步：局面分析与决策
根据提供的对局初始信息（如图片或状态数据）分析当前局面，并制定最优策略。

**【你的当前状态】**
*   **位置**: {position_role}
*   **本轮行动顺序**: {action_order}
*   **策略提示**: 考虑到你是 {position_role}，{strategy_hint}。

**【动作说明书】**
请仔细阅读以下动作含义，确保操作合法：
1.  **Fold (弃牌)**: 放弃手牌，结束本局，输掉底池。
2.  **Check (过牌)**: 不下注，让过。仅当“需跟注金额”为 0 时可用。
3.  **Call (跟注)**: 投入与对手下注额相等的筹码。
4.  **Bet (下注)**: 当前回合无人下注时，主动投入筹码。
5.  **Raise (加注)**: 在对手下注基础上增加注码。请参考“当前允许的动作”中的金额范围，计算赔率是否合适。
6.  **AllIn (全压)**: 投入剩余所有筹码。

### 第三步：执行动作
分析完毕后，使用 `applyAction` 工具执行你的决策。
*   **参数要求**：务必传入第一步获取的 `pin` 码以及你的决策动作。

### 第四步：最终结项（仅在游戏完全结束时执行）
**注意：如果游戏仍在进行中（例如只是完成了一轮下注），请勿执行此步。**
只有当整场对局彻底结束（Game Over）时，才需要在回复的最后一行输出 PIN 码，格式如下：
\\boxed{{pin}}
""",
f"""
# 任务：德州扑克决策执行
# 对局ID: {game_id} | 对手风格: {style}

请按顺序完成以下操作：

1.  **获取授权**：
    *   立即调用 `createGameSession`。
    *   保存返回的 **PIN 码**，这是后续操作的重要凭证。

2.  **策略制定**：
    *   当前身份：{position_role} (行动顺位: {action_order})
    *   战术参考：{strategy_hint}
    *   **动作定义参考**：
        1.  **Fold (弃牌)**: 放弃手牌，结束本局，输掉底池。
        2.  **Check (过牌)**: 不下注，让过。仅当“需跟注金额”为 0 时可用。
        3.  **Call (跟注)**: 投入与对手下注额相等的筹码。
        4.  **Bet (下注)**: 当前回合无人下注时，主动投入筹码。
        5.  **Raise (加注)**: 在对手下注基础上增加注码。需参考允许金额范围并计算赔率。
        6.  **AllIn (全压)**: 投入剩余所有筹码。
    *   基于上述信息及当前牌局状态，决定下一步动作。

3.  **动作执行**：
    *   调用 `applyAction` 工具。
    *   必须参数：PIN 码 + 决策动作。

4.  **结案陈词（条件触发）**：
    *   **警告**：若游戏尚未结束，请忽略此步骤。
    *   仅在**游戏终局（Game Over）**时，在最后一行严格输出：
    \\boxed{{pin}}
""",
f"""
# 职业牌手思维链
你好，我是你的战术顾问。现在我们正处于一场关键的德州扑克对局中（ID: {game_id}）。
坐在对面的家伙打法很【{style}】，我们要小心应对。

## 我们的行动计划

**Step 1: 拿到入场券**
别急着看牌，先调用 `createGameSession` 拿到那个至关重要的 **PIN 码**。没有它，我们连筹码都摸不到。

**Step 2: 审视战局**
看看我们在什么位置... 嗯，是 {position_role}，第 {action_order} 个行动。
听着，鉴于我们是 {position_role}，我建议：{strategy_hint}。

仔细权衡你的选择，别犯低级错误：
*   **Fold**: 牌力不够就果断放弃，止损离场。
*   **Check**: 如果前面没人下注，且你想免费看下一张牌，就选这个（记住，只有不用掏钱时才能Check）。
*   **Call**: 对手打得不重，赔率合适，我们就跟进去看看。
*   **Bet**: 没人动？那我们主动出击，往池子里扔点筹码。
*   **Raise**: 对手下注了？如果我们牌强或者想诈唬，就加注打回去（注意算好赔率）。
*   **AllIn**: 绝杀时刻，推入所有筹码。

**Step 3: 亮剑**
决定好了吗？用 `applyAction` 把你的决定打出去！记得带上刚才那个 PIN 码。

**Step 4: 离场确认（仅限终局）**
如果这局牌还在打，就不要做这一步。
只有当**整局游戏彻底结束**之后，别忘了把 PIN 码写在最后给我确认一下，格式不能错：
\\boxed{{pin}}
""",
f"""
[SYSTEM ALERT]: Texas Hold'em Protocol Initiated
[GAME_ID]: {game_id}
[OPPONENT_PROFILE]: {style}

执行序列如下：

>>> PHASE 1: SESSION HANDSHAKE
必须优先执行 `createGameSession` 函数。
输出结果将包含 session_token (即 **PIN**)。
警告：后续 `applyAction` 调用若缺失 PIN 将导致 Critical Error。

>>> PHASE 2: STATE ANALYSIS & DECISION
当前状态参数：
- Position: {position_role}
- Sequence: {action_order}
- Heuristic: {strategy_hint}

指令集定义:
1.  [Fold]: 终止进程，放弃当前手牌与底池权益。
2.  [Check]: 零成本过牌。条件：Current_Call_Amount == 0。
3.  [Call]: 匹配当前下注额，维持博弈资格。
4.  [Bet]: 主动发起下注（仅限当前Round无人下注时）。
5.  [Raise]: 增加注码。需校验 Pot Odds 及允许的加注范围。
6.  [AllIn]: 投入 Total_Stack，进行全额博弈。

请根据赔率计算与对手画像选择最优指令。

>>> PHASE 3: EXECUTION
调用 `applyAction(pin=PIN, action=DECISION)`。

>>> PHASE 4: TERMINATION OUTPUT (CONDITIONAL)
**Condition: Execute ONLY if Game Status == COMPLETED.**
若游戏仍在进行，禁止输出。
任务彻底完成后，必须在标准输出流末尾打印 PIN：
\\boxed{{pin}}
""",
f"""
# 德州扑克 AI 助手指南

欢迎！你将辅助我完成一局德州扑克（ID: {game_id}）。对手是个【{style}】的玩家。

**第一件事：建立连接**
我们需要先“登录”这局游戏。请运行 `createGameSession` 工具。你会得到一个 **PIN 码**，请务必记好它，后面都要用到。

**第二件事：该怎么打？**
现在轮到我们行动了。
*   你是 {position_role}，排在第 {action_order} 位。
*   小贴士：{strategy_hint}。

请参考以下说明选择最合适的动作：
1.  **Fold (弃牌)**: 觉得赢不了？那就放弃手牌，不再投入。
2.  **Check (过牌)**: 如果不需要补钱就能看牌，就选这个（也就是需跟注金额为0时）。
3.  **Call (跟注)**: 别人下注了，我们出一样的钱跟下去。
4.  **Bet (下注)**: 现在没人下注，我们主动往池子里放钱。
5.  **Raise (加注)**: 别人下注了，我们加价！记得看看赔率合不合适。
6.  **AllIn (全压)**: 拼了！把剩下的筹码全推出去。

**第三件事：操作**
想好后，用 `applyAction` 工具告诉系统你的决定（别忘了填入 PIN 码）。

**最后（仅当游戏结束时）：**
如果游戏还在继续，请不要输出此项。
仅在对局彻底结束后，请在最后一行把 PIN 码框起来给我看，像这样：
\\boxed{{pin}}
""",
f"""
# 德州扑克安全操作规范
# 警告：当前对局 ID {game_id}，对手风格 {style}

为防止操作失败，请严格遵守以下安全协议：

**协议一：身份验证（必须优先执行）**
禁止在未获取 PIN 码的情况下进行分析。
操作：调用 `createGameSession`。
产出：**PIN 码** (用于 `applyAction` 鉴权)。

**协议二：合规决策**
当前环境：位置 {position_role} | 顺位 {action_order}。
参考策略：{strategy_hint}。

**合法动作检查清单**：
*   **Fold**: 放弃手牌，终止本局权益。
*   **Check**: 过牌。*限制条件：仅当需跟注金额为 0 时合法。*
*   **Call**: 跟注。投入等额筹码。
*   **Bet**: 下注。*限制条件：仅当本轮尚无下注时合法。*
*   **Raise**: 加注。需基于允许范围计算赔率风险。
*   **AllIn**: 全压。投入剩余全部资金。

**协议三：原子化执行**
使用 `applyAction` 提交决策。若遗漏 PIN 码，操作将被拒绝。

**协议四：格式化归档（条件：游戏结束）**
**若游戏未结束，严禁执行此协议。**
在所有交互结束（Game Over）后的最后一行，必须输出：
\\boxed{{pin}}
""",
f"""
# 德州扑克博弈优化任务
Game ID: {game_id}

**目标**：最大化 EV (期望价值) 并利用对手【{style}】的漏洞。

**Step 1: 初始化会话**
调用 `createGameSession` 获取 **PIN**。这是与服务器交互的唯一密钥。

**Step 2: 决策树分析**
输入变量：
*   Hero位置: {position_role}
*   行动次序: {action_order}
*   策略建议: {strategy_hint}

**动作空间解析**：
*   **Fold**: EV < 0 时的止损操作，放弃底池。
*   **Check**: 免费看牌/控池。*Condition: Call Amount == 0*。
*   **Call**: 赔率合适时，投入等额筹码跟进。
*   **Bet**: 主动建立底池，仅限无人下注时。
*   **Raise**: 扩大底池或施压。需严格计算 Pot Odds 与 Implied Odds。
*   **AllIn**: 极化范围操作，投入全部筹码。

**Step 3: 动作提交**
利用 `applyAction` 执行你的最优解。

**Step 4: 结果验证（仅限终局）**
如果游戏还在进行，请跳过此步。
任务彻底结束后，回复 PIN 码：
\\boxed{{pin}}
""",
f"""
嘿，我们需要处理一局德州扑克（ID: {game_id}）。对手打得很【{style}】，这局怎么说？

首先，哪怕你再急，也得先帮我跑一下 `createGameSession`，我需要那个 **PIN 码** 才能操作后续的步骤，这个千万别忘了。

拿到 PIN 码后，帮我分析一下局面。我现在是 {position_role}，第 {action_order} 个说话。
考虑到 {strategy_hint}，你觉得我该怎么做？

看看菜单上有啥：
1.  **Fold**: 牌烂就扔，别犹豫，输掉底池总比输更多好。
2.  **Check**: 只要不用掏钱（跟注额为0），就选这个混过去。
3.  **Call**: 别人下注了，咱们觉得划算就跟。
4.  **Bet**: 没人下注？那咱们先下手为强，扔点筹码进去。
5.  **Raise**: 嫌别人下得少？加注！但得算算赔率合不合算。
6.  **AllIn**: 不服就干，梭哈！

决定好了就直接调用 `applyAction` 把动作发出去，记得带上 PIN 码。

最后，**只有在这局彻底完事（Game Over）了才给我留个底**，中间过程不需要。
格式是：
\\boxed{{pin}}
""",
f"""
**紧急行动：德州扑克对局 {game_id}**
**对手情报**：{style}

**执行清单（严格按序）：**

1.  **[获取密钥]**：调用 `createGameSession`。没有 **PIN 码** 无法进行任何操作！
2.  **[战况研判]**：
    *   你是 {position_role}，第 {action_order} 顺位。
    *   战术指导：{strategy_hint}。
    *   **战术指令集**：
        - **Fold**: 放弃任务（弃牌），损失当前底池。
        - **Check**: 待机（过牌）。*注意：仅在无需跟注时有效。*
        - **Call**: 跟随（跟注）。投入等量筹码。
        - **Bet**: 突击（下注）。当前无人下注时主动出击。
        - **Raise**: 反击（加注）。在对手火力基础上增加注码（需计算赔率）。
        - **AllIn**: 全力一击（全压）。
3.  **[指令下达]**：使用 `applyAction` 工具，参数：PIN + 你的动作。
4.  **[任务回执]**：
    **仅当对局彻底结束时**，必须在回复中输出：
    \\boxed{{pin}}
""",
f"""
# ♠️ 德州扑克战术辅助系统
> 正在接入对局: {game_id}
> 扫描对手特征: 【{style}】

## 必须执行的操作序列

**Phase 1: 建立加密通道**
系统尚未同步。请立即运行 `createGameSession` 工具。
*   **关键产出**: 获取本次会话的 **PIN 码**。
*   *警告*: 只有持有 PIN 码才能在 Phase 3 发送指令。

**Phase 2: 实时决策计算**
根据当前遥测数据进行分析：
*   [位置参数]: {position_role}
*   [行动顺位]: {action_order}
*   [AI 建议]: {strategy_hint}

**[指令集参数详解]**
*   `Fold` : [弃牌] 放弃手牌与底池。
*   `Check`: [过牌] 仅当 Call_Amount=0 时可用。
*   `Call` : [跟注] 匹配对手下注额。
*   `Bet`  : [下注] 主动投入筹码（当前无人下注）。
*   `Raise`: [加注] 增加注码（需评估赔率模型）。
*   `AllIn`: [全压] 投入所有剩余资源。

请基于上述情报计算最优解。

**Phase 3: 指令上行**
决策完成后，调用 `applyAction` 工具执行操作。

**Phase 4: 同步确认（条件：任务终结）**
若游戏继续，请跳过此步骤。
仅当任务彻底完成（Game Over）时，请务必在最后一行输出 PIN 码以确认数据同步：
\\boxed{{pin}}
"""
]
        return random.choice(prompts)
