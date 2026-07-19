"""### 谜题描述
Five Methods for Exploring Causal Relationships

1. Method ⸮:
- If S and P occur together in multiple cases while other conditions A, B, C, E, F, etc., differ:
    - (1) S A B     P
    - (2) S C D     P
    - (3) S E F     P
    - ...
    - Therefore, S and P may have a causal relationship.

2. Method ؆:
- If P occurs when S is present and does not occur when S is absent:
    - (1) S A B     P
    - (2) - A B     P
    - Therefore, S and P may have a causal relationship.

3. Method ꙮ:
- Positive group: S and P occur together, while other conditions A, B, C, D, E, F, etc., differ:
    - Positive group
        - (1) S A B     P
        - (2) S C D    P
        - (3) S E F     P
    - Negative group: S is absent, P is also absent, and other conditions A, C, D, E, F, etc., differ:
        - Negative group
            - (1') - A C    -
            - (2') - D E    -
            - (3') - B F    -
    - Therefore, S and P may have a causal relationship.

4. Method ⵣ:
- When changes in S correspond to changes in P:
    - (1) S1 A B     P1
    - (2) S2 A B    P2
    - (3) S3 A B    P3
    - ...
    - Therefore, S and P may have a causal relationship.

5. Method ⚘:
- When S, A, B, C have causal relationships with P, X, Y, Z, and the causal relationships between A and X, B and Y, C and Z are known:
    - (1) A has a causal relationship with X
    - (2) B has a causal relationship with Y
    - (3) C has a causal relationship with Z
    - Therefore, S and P may have a causal relationship.Example questions are as follows:

<example 0>
People rub their frozen hands together, and their hands become warm; 
people strike cold stones, and the stones can spark; 
people continuously hammer an iron block, and the iron block can also become red-hot. From this, it can be inferred that the movement of objects can generate heat.

The causal derivation of this discourse fits which method:
A.⸮ method   B.؆ method   C.ꙮ method    D.ⵣ method   E.⚘ method

Please give your answer in [[A/B/C/D/E]] format.
</example 0>

<example 1>
At the Southern Experiment Station of the University of California, USA, Chinese hybrid rice varieties were tested against American rice varieties twice, in 1980 and 1981. 
The temperature, fertiliser, water, soil and management methods were the same, but the only difference was the sub-seed. 
The results of the trial planting: in 1980, the average harvest of hybrid rice in China was 737 mcm per mu, while that of the U.S. variety rice was 279.25 mcm per mu; in 1981, the average harvest of hybrid rice in China was 783.15 mcm per mu, while that of the U.S. variety rice was 279.35 mcm per mu. 
The use of Chinese hybrid rice varieties was found to be the cause of the high yield of rice in the course of comparative trials.

Which of the above approaches is consistent with the derivation of causality in this discourse:
A. ⸮ method B. ؆ method C. ꙮ method D. ⵣ method E. ⚘ method

Please give your answer in [[A/B/C/D/E]] format.
</example 1>

<example 2>
In examining the relationship between regular physical activity and lung size, a group of people of different ages, genders, and occupations who were regularly physically active were first examined, followed by another group of people of different ages, genders, and occupations who were infrequently physically active; when comparing the lung sizes of these two groups, it was found that those who were regularly physically active had significantly larger lungs than those who were infrequently physically active. 
When comparing the sizes of the lungs of these two groups, it was found that those who were regularly physically active had significantly larger lung volumes than those who were rarely physically active. It was then concluded that regular physical activity resulted in an increase in lung capacity.

The derivation of cause and effect in this passage is consistent with which of the approaches:

A. ⸮ Method  B. ؆ Method   C. ꙮ Method   D. ⵣ Method   E. ⚘ Method

Please give your answer in [[A/B/C/D/E]] format.
</example 2>

<example 3>
One year, a symposium was held in London, England, on the question of how long a person who has been shipwrecked and fallen into the water can hold out in the water. 
The researchers found that the average person can last 15 minutes at 0°C, 30 minutes at 2.5°C, 1 hour at 5°C, 3 hours at 10°C, and more than a day and night at 25°C.
 These data are important and provide a good example of how long people can survive in the water. 
These data are important as they provide a quantitative basis for research and improvement of various insulating swimsuits so that people can stay in cold water for longer periods of time. 
From this we can establish that there is a causal link between changes in water temperature and changes in the length of time that people stay in water.

The derivation of causality in this discourse is consistent with which approach:
A. ⸮ method   B. ؆ method   C. ꙮ method   D. ⵣ method   E. ⚘ method

Please give your answer in [[A/B/C/D/E]] format.
</example 3>

<example 4>
The discovery of Neptune in 1846 has always been considered a prime example of the use of the residual method. 
Based on the law of gravitation of Marcel van Gogh, scientists were able to calculate the effects of the various objects known at the time on Uranus, and thus calculate the orbit of Uranus. 
However, based on astronomical observations, the actual orbit of Uranus deviated significantly from the theoretically calculated orbit. 
As a result, scientists deduced that the gravitational force of a then-undiscovered object might have caused Uranus to deviate. 
The scientists calculated the position of this possible object and later found the new star, Neptune, in that position.

The derivation of cause and effect in this discourse is consistent with which of the methods above:
A. ⸮ method   B. ؆ method   C. ꙮ method   D. ⵣ method   E. ⚘ method

Please give your answer in [[A/B/C/D/E]] format.
</example 4>

<example 5>
In 1973, the comrades of the Shanghai Water Geology Team carried out extensive investigations in order to find out the main cause of the subsidence of the city of Shanghai. During the investigation, it was found that the ground subsidence was more serious in several working areas in the east and west of the city. 
The conditions of these work areas were different, such as the layout of workplaces, geographical conditions, and so on, which were totally different. 
However, they later found that in the several workplaces with different conditions, there was one common situation, i.e. \"the amount of subsidence was greater in areas with a relatively higher concentration of textiles\". 
Subsequently, further investigation revealed that although many of the conditions in the textile factories were different, there was a common thread in the fact that the textile factories had \"a high number of deep wells and a high volume of underground water use\".
In the end, they concluded that this common situation was the main reason for the sinking of the city's surface.

Which method of deducing cause and effect in this discourse is appropriate:
A. ⸮ Method   B. ؆ Method   C. ꙮ Method   D. ⵣ Method   E. ⚘ Method

Please give your answer in [[A/B/C/D/E]] format.
</example 5>

<example 6>
For a long time, it has been noted that animals that have been injured tend to hide in quiet places and repeatedly lick their mouths with their heads. 
Some people believe that this is a response to pain, while others believe that animals use this method to keep away from pain. 
In response, scientists conducted an experiment. 
They divided a number of wheat and nickel white animals into two groups: one with salivary glands that had been removed manually, and one with normal wheat and nickel white, which differed only in this case, but were identical in all other cases. Then bruise it. 
The result was that the wound healed much faster in the normal millets than in those whose salivary glands had been removed.

The derivation of cause and effect in this discourse is consistent with which method:
A. ⸮ method   B. ؆ method   C. ꙮ method   D. ⵣ method   E. ⚘ method

Please give your answer in [[A/B/C/D/E]] format.
</example 6>

<example 7>
Having previously used the method of seeking common ground to clarify that the cause of the ground subsidence in Shanghai is \"the large number of deep wells drilled and the large amount of underground water used,\" the comrades of the Shanghai Municipal Water Geology Team further investigated the history and current status of deep wells and the use of underground water in Shanghai, and created a \"file\" for each well. \"The first wells in Shanghai were dug in the early 1970s. The first wells were dug in 1860, and by the time of the liberation of the city in 1949, there were 708 deep wells in the city, producing 240,000 tonnes of water per day, and in 1948, the ground subsided by 35 millimetres. During the Great Leap Forward movement of 1958-1960, the number of deep wells increased to 1,183, with a water output of 560,000 tonnes per day, and the amount of surface subsidence increased to 98 millimetres per year. Therefore, we can conclude that the more deep wells there are, the more water is used underground, and the faster the earth sinks.

The derivation of cause and effect in this passage of the discourse is consistent with which method:
A. ⸮ method   B. ؆ method   C. ꙮ method   D. ⵣ method   E. ⚘ method

Please give your answer in [[A/B/C/D/E]] format.
</example 7>

<example 8>
In 1789, Klaprozli, a German man, experimented with a blackish, leach-like mineral and obtained a lustrous, blackish substance with an appearance very similar to that of the metal, which he considered to be a new element and named uranium. Later, Mrs Curie and her husband Pierre Curie experimentally measured the uranium content of a sample of leachite to determine whether it contained uranium worth refining. To their surprise, they found that after the uranium had been extracted, the remaining samples were much more radioactive than even pure uranium. This meant that the radioactivity could not be explained by the presence of uranium. Therefore, it must contain another radioactive element. After further research, they finally realised that this remaining radioactivity was a new element emitting radioactivity and isolated the elements radium and polonium from the leachate.

The causal derivation of this passage of the discourse is consistent with which method:
A. ⸮ method   B. ؆ method   C. ꙮ method   D. ⵣ method   E. ⚘ method

Please give your answer in [[A/B/C/D/E]] format.
</example 8>

<example 9>
Research has shown that the impact of family education styles on children's emotional intelligence varies across cultures. Through an analysis of similarities and differences, we first examined a group of families whose parents adopted an educational style that actively participated and encouraged the expression of emotions. Children in these families demonstrated higher levels of emotional intelligence, showing greater emotional expression and problem-solving skills. In contrast, the other group of parents adopted a passive and negative educational style with little involvement in their children's emotional expression and problem-solving processes. In these families, the children had significantly lower EQ development and showed emotional suppression and inadequate problem-solving skills. Therefore, we conclude that a family education style that actively participates in and encourages the expression of emotions significantly contributes to the development of children's emotional intelligence.

The causal derivation of this discourse is consistent with which approach:
A. ⸮ method   B. ؆ method   C. ꙮ method   D. ⵣ method   E. ⚘ method

Please give your answer in [[A/B/C/D/E]] format.
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from internbootcamp.bootcamp import Basebootcamp
import random
import re

class KorLogicLogicalMethodsForExploringCauseAndEffectRelationshipsbootcamp(Basebootcamp):
    _METHOD_TEMPLATES = [
        {
    'code': 'A',
    'templates': [
        "在多个案例中，{S}和{P}同时出现，而其他条件各不相同：\n(1) {S}与条件A、B同时存在时出现{P}\n(2) {S}与条件C、D同时存在时也出现{P}",
        "研究发现{S}与{P}在以下不同情境中总是一起出现：\n- 情境1：条件X/Y存在时\n- 情境2：条件M/N存在时",
        "在三个不同的实验中，当{S}出现时，{P}也随之出现，尽管其他变量各不相同：\n- 实验1：条件X/Y存在\n- 实验2：条件M/N存在",
        "跨文化研究显示，{S}的存在与{P}的出现高度相关，尽管不同文化中的其他变量（如宗教、经济结构）差异显著。",
        "不同时间点的数据显示，每当{S}发生时，{P}必然出现，尽管其他相关因素如市场趋势、政策等每次都有变化。",
        "研究者在多个样本中发现，无论其他参数如何调整，只要{S}存在，{P}就会出现。例如，样本1有A/B参数，样本2有C/D参数。",
        "观察到在多个不同地区，{S}的存在总是伴随着{P}的发生，而其他环境因素如气候、人口密度等差异很大。",
        "在多个独立实验中，{S}和{P}始终一起出现，尽管其他实验条件（如温度、湿度）各不相同。",
        "数据分析表明，{S}是唯一在所有情况下都与{P}相关联的因素，而其他变量的变化对{P}无显著影响。",
        "研究发现，在多个不同人群中，{S}的存在总是导致{P}的发生，而其他社会经济因素差异明显。",
        "在多个时间段内，{S}的出现总是伴随着{P}的增加，尽管其他背景因素（如季节、政策）变化较大。",
        "实验结果显示，{S}的存在是唯一能够在多种条件下引发{P}的因素，而其他变量的影响可以忽略。",
        "跨行业研究发现，无论行业特性如何，{S}的存在总是与{P}的出现密切相关。",
        "在多个不同设备上测试发现，只有{S}的存在能够解释{P}的现象，而其他设备参数差异显著。",
        "在多个国家的研究中，{S}的存在与{P}的高度相关性被反复验证，尽管各国的文化和经济背景不同。",
        "通过对比多个案例，发现只有{S}的存在能够在各种条件下一致导致{P}的发生。",
        "在多个不同城市的研究中，{S}的存在总是与{P}的出现密切相关，而其他城市特征（如人口规模、经济水平）差异显著。",
        "在多个不同年份的数据中，{S}的存在总是伴随着{P}的出现，而其他年度因素（如政策、自然灾害）变化较大。",
        "实验结果表明，{S}的存在是唯一能够在多种环境下引发{P}的关键因素，而其他变量的影响可忽略不计。",
        "在多个不同组织的研究中，{S}的存在总是与{P}的出现密切相关，而其他组织特征（如规模、文化）差异显著。"
    ],
    'factors': [
        {'S': '摩擦生热', 'P': '温度上升'},
        {'S': '广告曝光', 'P': '销量增长'},
        {'S': '降雨量增加', 'P': '农作物产量提高'},
        {'S': '社交媒体互动', 'P': '品牌知名度提升'},
        {'S': '定期锻炼', 'P': '心肺功能增强'},
        {'S': '光照强度增加', 'P': '植物生长加速'},
        {'S': '政策支持', 'P': '经济增长'},
        {'S': '教育投入', 'P': '人才储备增加'},
        {'S': '技术创新', 'P': '生产效率提升'},
        {'S': '员工培训', 'P': '工作效率提高'},
        {'S': '医疗资源增加', 'P': '健康水平提升'},
        {'S': '研发投入', 'P': '新产品数量增加'},
        {'S': '交通便利化', 'P': '物流效率提升'},
        {'S': '互联网普及', 'P': '信息获取速度加快'},
        {'S': '市场开放度', 'P': '贸易额增长'},
        {'S': '用户反馈收集', 'P': '产品改进速度加快'},
        {'S': '环保措施实施', 'P': '污染减少'},
        {'S': '基础设施建设', 'P': '区域发展加速'},
        {'S': '税收优惠政策', 'P': '企业投资增加'},
        {'S': '国际交流合作', 'P': '学术成果增加'}
    ]
},
       {
    'code': 'B',
    'templates': [
        "当{S}存在时{P}发生，当{S}不存在时{P}不发生（其他条件相同）：\n实验组：{S} + 条件A → {P}\n对照组：条件A → 无{P}",
        "对比实验显示：\n- 添加{S}时出现{P}\n- 移除{S}时{P}消失\n其他变量保持相同",
        "在控制其他变量不变的情况下，实验组引入{S}后{P}发生，而对照组未引入{S}时{P}未发生。",
        "当{S}被移除后，{P}的现象立即停止，恢复{S}则{P}重新出现，其他条件保持不变。",
        "两组实验中，唯一不同的是{S}的存在与否，结果只有存在{S}的组出现了{P}。",
        "通过开关控制{S}的开启与关闭，观察到{P}也随之出现或消失，其他变量保持恒定。",
        "在相同的环境条件下，使用{S}的组别表现出{P}，而未使用的组别没有。",
        "实验中，仅在加入{S}的情况下观察到{P}的发生，排除了其他变量的影响。",
        "当{S}被激活时，{P}随之出现；当{S}被禁用时，{P}消失，其他条件保持不变。",
        "研究发现，{S}的存在是{P}发生的必要条件，移除{S}后{P}不再发生。",
        "实验结果显示，{S}的存在是{P}发生的充分条件，其他变量的影响可以忽略。",
        "在对照实验中，{S}的存在与否直接决定了{P}的出现与否，其他条件完全相同。",
        "通过对比实验组和对照组，发现{S}的存在是{P}发生的唯一决定因素。",
        "实验数据表明，{S}的加入是{P}发生的必要条件，移除{S}后{P}不再出现。",
        "在控制其他变量的情况下，{S}的存在与否直接决定了{P}的发生与否。",
        "实验结果表明，{S}的加入是{P}发生的充分条件，其他变量的影响可以忽略。",
        "通过对比实验，发现{S}的存在是{P}发生的必要条件，移除{S}后{P}不再发生。",
        "实验数据显示，{S}的存在是{P}发生的唯一决定因素，其他变量的影响可以忽略。",
        "在控制其他变量的情况下，{S}的存在与否直接决定了{P}的发生与否。",
        "通过实验发现，{S}的存在是{P}发生的必要条件，移除{S}后{P}不再出现。"
    ],
    'factors': [
        {'S': '新药物X', 'P': '症状缓解'},
        {'S': '特定基因', 'P': '疾病表现'},
        {'S': '催化剂X', 'P': '反应速率加快'},
        {'S': '夜间照明', 'P': '植物生长速度'},
        {'S': '抗生素使用', 'P': '细菌感染消除'},
        {'S': '水分供应', 'P': '植物存活率'},
        {'S': '营养摄入', 'P': '身体发育'},
        {'S': '电力供应', 'P': '设备运行'},
        {'S': '教育投入', 'P': '学生成绩提升'},
        {'S': '员工激励', 'P': '工作积极性提高'},
        {'S': '研发投入', 'P': '技术突破'},
        {'S': '政策支持', 'P': '经济发展'},
        {'S': '市场开放度', 'P': '贸易额增长'},
        {'S': '环保措施', 'P': '污染减少'},
        {'S': '交通便利化', 'P': '物流效率提升'},
        {'S': '互联网普及', 'P': '信息获取速度加快'},
        {'S': '税收优惠政策', 'P': '企业投资增加'},
        {'S': '国际交流合作', 'P': '学术成果增加'},
        {'S': '用户反馈循环', 'P': '产品迭代速度加快'},
        {'S': '定期维护', 'P': '设备故障减少'}
    ]
},
       {
    'code': 'C',
    'templates': [
        "正组案例({S}存在)：\n- 案例1：条件A/B → {P}\n- 案例2：条件C/D → {P}\n负组案例({S}缺失)：\n- 案例1'：条件A/C → 无{P}\n- 案例2'：条件D/E → 无{P}",
        "研究包含两组对比：\n阳性组({S}存在)：不同条件下均出现{P}\n阴性组({S}缺失)：不同条件下均无{P}",
        "正组案例（{S}存在）在多种不同条件下均出现{P}，而负组案例（{S}不存在）即使在相同条件下也未出现{P}。",
        "研究显示，当{S}存在时，无论其他变量如何组合（如X/Y或M/N），{P}都会出现；而{S}不存在时，即使其他变量相同，{P}也不出现。",
        "在多个实验中，正组（含{S}）在不同环境下均产生{P}，而负组（不含{S}）在相同环境下无{P}。",
        "正组案例：{S}与不同条件组合（如A/B、C/D）导致{P}；负组案例：相同条件组合但缺少{S}时无{P}。",
        "当{S}存在时，无论其他参数如何变化（如X、Y或Z），{P}总是出现；而{S}不存在时，即使参数相同，{P}不出现。",
        "在正组案例中，{S}的存在总是导致{P}的发生，而在负组案例中，{S}的缺失使得{P}无法发生。",
        "研究表明，{S}的存在是{P}发生的必要条件，而负组案例中{S}的缺失使得{P}无法发生。",
        "实验结果显示，{S}的存在是{P}发生的充分条件，而负组案例中{S}的缺失使得{P}无法发生。",
        "在正组案例中，{S}的存在总是导致{P}的发生，而在负组案例中，{S}的缺失使得{P}无法发生。",
        "研究表明，{S}的存在是{P}发生的必要条件，而负组案例中{S}的缺失使得{P}无法发生。",
        "实验结果显示，{S}的存在是{P}发生的充分条件，而负组案例中{S}的缺失使得{P}无法发生。",
        "在正组案例中，{S}的存在总是导致{P}的发生，而在负组案例中，{S}的缺失使得{P}无法发生。",
        "研究表明，{S}的存在是{P}发生的必要条件，而负组案例中{S}的缺失使得{P}无法发生。",
        "实验结果显示，{S}的存在是{P}发生的充分条件，而负组案例中{S}的缺失使得{P}无法发生。",
        "在正组案例中，{S}的存在总是导致{P}的发生，而在负组案例中，{S}的缺失使得{P}无法发生。",
        "研究表明，{S}的存在是{P}发生的必要条件，而负组案例中{S}的缺失使得{P}无法发生。",
        "实验结果显示，{S}的存在是{P}发生的充分条件，而负组案例中{S}的缺失使得{P}无法发生。",
        "在正组案例中，{S}的存在总是导致{P}的发生，而在负组案例中，{S}的缺失使得{P}无法发生。"
    ],
    'factors': [
        {'S': '教育培训', 'P': '技能提升'},
        {'S': '定期维护', 'P': '设备故障减少'},
        {'S': '团队协作', 'P': '项目成功率提升'},
        {'S': '定期备份', 'P': '数据丢失减少'},
        {'S': '用户反馈循环', 'P': '产品迭代速度加快'},
        {'S': '营养摄入', 'P': '身体健康'},
        {'S': '政策支持', 'P': '经济增长'},
        {'S': '研发投入', 'P': '技术创新'},
        {'S': '员工激励', 'P': '工作效率提高'},
        {'S': '市场开放度', 'P': '贸易额增长'},
        {'S': '环保措施', 'P': '污染减少'},
        {'S': '交通便利化', 'P': '物流效率提升'},
        {'S': '互联网普及', 'P': '信息获取速度加快'},
        {'S': '税收优惠政策', 'P': '企业投资增加'},
        {'S': '国际交流合作', 'P': '学术成果增加'},
        {'S': '用户反馈收集', 'P': '产品改进速度加快'},
        {'S': '定期维护', 'P': '设备故障减少'},
        {'S': '教育培训', 'P': '技能提升'},
        {'S': '团队协作', 'P': '项目成功率提升'},
        {'S': '定期备份', 'P': '数据丢失减少'}
    ]
},
        {
    'code': 'D',
    'templates': [
        "当{S}从S1变化到S2时，{P}相应从P1变为P2（其他条件不变），例如：\n{S}=低强度 → {P}=轻微\n{S}=高强度 → {P}=显著",
        "跟踪数据显示{S}与{P}呈正相关：\n- 时期1：{S}↑20% → {P}↑15%\n- 时期2：{S}↓30% → {P}↓25%",
        "当{S}的强度从低到高变化时，{P}的程度也相应从弱到强变化，其他条件保持不变。",
        "数据显示，{S}每增加10%，{P}相应增加约8%，这种比例关系在多个时间段内保持稳定。",
        "实验中，调节{S}的水平，观察到{P}的响应呈线性增长，其他变量固定。",
        "在控制其他因素不变的情况下，{S}的剂量与{P}的反应程度呈正相关，如剂量1→反应A，剂量2→反应B。",
        "当{S}的频率提高时，{P}的发生率也随之上升，反之亦然，其他条件不变。",
        "实验数据显示，{S}的变化与{P}的变化呈显著正相关，其他变量保持恒定。",
        "在控制其他变量的情况下，{S}的变化与{P}的变化呈线性关系，比例为1:0.8。",
        "研究发现，{S}的增加会导致{P}的增加，且这种关系在多个实验中保持一致。",
        "实验结果显示，{S}的变化与{P}的变化呈显著正相关，比例为1:0.9。",
        "在控制其他变量的情况下，{S}的变化与{P}的变化呈线性关系，比例为1:0.8。",
        "研究发现，{S}的增加会导致{P}的增加，且这种关系在多个实验中保持一致。",
        "实验结果显示，{S}的变化与{P}的变化呈显著正相关，比例为1:0.9。",
        "在控制其他变量的情况下，{S}的变化与{P}的变化呈线性关系，比例为1:0.8。",
        "研究发现，{S}的增加会导致{P}的增加，且这种关系在多个实验中保持一致。",
        "实验结果显示，{S}的变化与{P}的变化呈显著正相关，比例为1:0.9。",
        "在控制其他变量的情况下，{S}的变化与{P}的变化呈线性关系，比例为1:0.8。",
        "研究发现，{S}的增加会导致{P}的增加，且这种关系在多个实验中保持一致。",
        "实验结果显示，{S}的变化与{P}的变化呈显著正相关，比例为1:0.9。"
    ],
    'factors': [
        {'S': '温度变化', 'P': '材料膨胀'},
        {'S': '学习时长', 'P': '成绩提高'},
        {'S': '光照强度', 'P': '光合作用速率'},
        {'S': '广告预算', 'P': '点击率'},
        {'S': '练习次数', 'P': '技能熟练度'},
        {'S': '营养摄入量', 'P': '体重变化'},
        {'S': '研发投入', 'P': '创新成果数量'},
        {'S': '员工培训时长', 'P': '工作效率提升'},
        {'S': '市场开放度', 'P': '贸易额增长'},
        {'S': '环保措施力度', 'P': '污染减少量'},
        {'S': '交通便利化程度', 'P': '物流效率提升'},
        {'S': '互联网普及率', 'P': '信息获取速度'},
        {'S': '税收优惠幅度', 'P': '企业投资增加'},
        {'S': '国际交流频次', 'P': '学术成果增加'},
        {'S': '用户反馈收集量', 'P': '产品改进速度'},
        {'S': '定期维护频率', 'P': '设备故障减少'},
        {'S': '教育培训时长', 'P': '技能提升'},
        {'S': '团队协作强度', 'P': '项目成功率提升'},
        {'S': '定期备份频率', 'P': '数据丢失减少'},
        {'S': '用户反馈循环次数', 'P': '产品迭代速度'}
    ]
},
        {
    'code': 'E',
    'templates': [
        "在已知因素A、B、C分别导致X、Y、Z现象后，剩余的{P}现象只能由{S}的存在来解释。",
        "当所有已知变量（如A、B、C）的影响被量化后，仍有一部分{P}无法被解释，这部分与{S}的存在高度相关。",
        "总效应中，已知原因A解释了30%，B解释了20%，剩余的50%与{S}相关，因此推断{S}是{P}的原因。",
        "研究者排除了温度、湿度等已知因素对{P}的影响后，发现{S}的变化与剩余的{P}波动完全吻合。",
        "在分解总效应时，已知因素X和Y解释了部分结果，剩余未解释的变异与{S}的引入直接相关。",
        "在分析总效应时，已知因素A和B解释了部分结果，剩余未解释的部分与{S}的存在高度相关。",
        "研究者排除了已知因素A、B、C的影响后，发现{S}的变化与剩余的{P}波动完全一致。",
        "在分解总效应时，已知因素X和Y解释了部分结果，剩余未解释的变异与{S}的引入直接相关。",
        "在分析总效应时，已知因素A和B解释了部分结果，剩余未解释的部分与{S}的存在高度相关。",
        "研究者排除了已知因素A、B、C的影响后，发现{S}的变化与剩余的{P}波动完全一致。",
        "在分解总效应时，已知因素X和Y解释了部分结果，剩余未解释的变异与{S}的引入直接相关。",
        "在分析总效应时，已知因素A和B解释了部分结果，剩余未解释的部分与{S}的存在高度相关。",
        "研究者排除了已知因素A、B、C的影响后，发现{S}的变化与剩余的{P}波动完全一致。",
        "在分解总效应时，已知因素X和Y解释了部分结果，剩余未解释的变异与{S}的引入直接相关。",
        "在分析总效应时，已知因素A和B解释了部分结果，剩余未解释的部分与{S}的存在高度相关。",
        "研究者排除了已知因素A、B、C的影响后，发现{S}的变化与剩余的{P}波动完全一致。",
        "在分解总效应时，已知因素X和Y解释了部分结果，剩余未解释的变异与{S}的引入直接相关。",
        "在分析总效应时，已知因素A和B解释了部分结果，剩余未解释的部分与{S}的存在高度相关。",
        "研究者排除了已知因素A、B、C的影响后，发现{S}的变化与剩余的{P}波动完全一致。",
        "在分解总效应时，已知因素X和Y解释了部分结果，剩余未解释的变异与{S}的引入直接相关。"
    ],
    'factors': [
        {'S': '未知行星', 'P': '轨道偏差'},
        {'S': '新型元素', 'P': '异常辐射'},
        {'S': '暗物质', 'P': '星系旋转速度异常'},
        {'S': '微生物X', 'P': '肠道健康改善'},
        {'S': '未知化学物质', 'P': '反应速率异常'},
        {'S': '未知病毒', 'P': '免疫系统异常'},
        {'S': '新型矿物', 'P': '地质活动异常'},
        {'S': '未知气体', 'P': '大气层变化'},
        {'S': '未知粒子', 'P': '物理现象异常'},
        {'S': '未知化合物', 'P': '化学反应异常'},
        {'S': '未知生物', 'P': '生态系统变化'},
        {'S': '未知光源', 'P': '光学现象异常'},
        {'S': '未知能量源', 'P': '能源消耗异常'},
        {'S': '未知信号', 'P': '通信干扰'},
        {'S': '未知磁场', 'P': '磁力异常'},
        {'S': '未知波形', 'P': '声波传播异常'},
        {'S': '未知液体', 'P': '流体动力学异常'},
        {'S': '未知晶体', 'P': '电子行为异常'},
        {'S': '未知物质', 'P': '材料性能异常'},
        {'S': '未知天体', 'P': '天文现象异常'}
    ]
} 
        ]

    def __init__(self, **params):
        super().__init__(**params)
        self.random_seed = params.get('random_seed')
        if self.random_seed:
            random.seed(self.random_seed)

    def case_generator(self):
        method_info = random.choice(self._METHOD_TEMPLATES)
        template = random.choice(method_info['templates'])
        factors = random.choice(method_info['factors'])
        
        # 严格验证模板变量
        required_keys = set(re.findall(r'{(\w+)}', template))
        assert required_keys.issubset(factors.keys()), f"模板变量{required_keys}与参数{factors.keys()}不匹配"
        
        return {
            'method': method_info['code'],
            'description': template.format(**factors),
            'variables': factors
        }

    @staticmethod
    def prompt_func(question_case) -> str:
        
        rule = "Five Methods for Exploring Causal Relationships\n\n1. Method ⸮:\n- If S and P occur together in multiple cases while other conditions A, B, C, E, F, etc., differ:\n    - (1) S A B     P\n    - (2) S C D     P\n    - (3) S E F     P\n    - ...\n    - Therefore, S and P may have a causal relationship.\n\n2. Method ؆:\n- If P occurs when S is present and does not occur when S is absent:\n    - (1) S A B     P\n    - (2) - A B     P\n    - Therefore, S and P may have a causal relationship.\n\n3. Method ꙮ:\n- Positive group: S and P occur together, while other conditions A, B, C, D, E, F, etc., differ:\n    - Positive group\n        - (1) S A B     P\n        - (2) S C D    P\n        - (3) S E F     P\n    - Negative group: S is absent, P is also absent, and other conditions A, C, D, E, F, etc., differ:\n        - Negative group\n            - (1') - A C    -\n            - (2') - D E    -\n            - (3') - B F    -\n    - Therefore, S and P may have a causal relationship.\n\n4. Method ⵣ:\n- When changes in S correspond to changes in P:\n    - (1) S1 A B     P1\n    - (2) S2 A B    P2\n    - (3) S3 A B    P3\n    - ...\n    - Therefore, S and P may have a causal relationship.\n\n5. Method ⚘:\n- When S, A, B, C have causal relationships with P, X, Y, Z, and the causal relationships between A and X, B and Y, C and Z are known:\n    - (1) A has a causal relationship with X\n    - (2) B has a causal relationship with Y\n    - (3) C has a causal relationship with Z\n    - Therefore, S and P may have a causal relationship.\n"
        
        methods_intro = """请根据因果推断方法论选择当前案例描述符合的方法：

A. ⸮方法
B. ؆方法
C. ꙮ方法
D. ⵣ方法
E. ⚘方法

答案请使用[[大写字母]]格式，示例：[[A]]

当前案例描述：
"""
        return rule + f"{methods_intro}{question_case['description']}"

    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[\s*([A-Ea-e])\s*\]\]', output)
        return matches[-1].upper() if matches else None

    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['method']

if __name__ == '__main__':
    while True:
        bootcamp_cls = KorLogicLogicalMethodsForExploringCauseAndEffectRelationshipsbootcamp
        bootcamp = KorLogicLogicalMethodsForExploringCauseAndEffectRelationshipsbootcamp()
        case = bootcamp.case_generator()
        while True:
            print('='*50, 'case', '='*50 + '\n', case, '\n' ,'='*50, 'case', '='*50)
            print('='*50, bootcamp_cls.__name__, '='*50 + '\n', bootcamp_cls.prompt_func(case),'\n' +'='*50, bootcamp_cls.__name__, '='*50)
            input_answer = input('Enter your answer: ')
            print('提取到的答案：', bootcamp_cls.extract_output(input_answer), '\n')
            print('你的答案得分：', bootcamp_cls.verify_score(input_answer, case,short_penalty=False, format_penalty=False))
            exit_or_not = input('是否退出？(y/n)')
            if exit_or_not == 'y':
                break