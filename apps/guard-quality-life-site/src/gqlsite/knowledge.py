"""品质生活知识树 · 数据层（Domain → Entry，与知识包 concepts 同源）。

纯结构化内存数据，dataclasses 建模，不依赖任何外部服务。
条目统一建模为「五要素」：purpose / steps / cost_benefit / evidence_level / caveat，
与模板 entry.html 渲染结构一一对应。
"""

from dataclasses import dataclass, field

__all__ = ["Entry", "Domain", "all_domains", "get_domain", "get_entry", "search", "domain_count"]


@dataclass(frozen=True)
class Entry:
    """知识树叶节点：一条可执行的生活行动建议。"""

    id: str
    title: str
    purpose: str
    steps: list[str] = field(default_factory=list)
    cost_benefit: str = ""
    evidence_level: str = "C"  # A/B/C
    evidence_source: str = ""
    caveat: str = ""


@dataclass(frozen=True)
class Domain:
    """知识树分支：一个生活域，含若干条目。"""

    id: str
    name: str
    summary: str
    entries: list[Entry] = field(default_factory=list)


# ---------------------------------------------------------------- 内置数据

_DOMAINS: dict[str, Domain] = {
    "home": Domain(
        id="home",
        name="家居",
        summary="用低维护的整理与收纳节奏，把家变成不耗精力的回血场。",
        entries=[
            Entry(
                id="home-surface-reset",
                title="每日 5 分钟台面复位",
                purpose="以一成不变的低摩擦动作，防止杂物在桌面、台面堆积成心理负担。",
                steps=[
                    "固定一个动作终点（如进卧室前 / 睡前），顺手将桌面物放回原位",
                    "只处理「本次摸过」的物品，不做大扫除",
                    "结束后给自己一句确认：台面是空的，家是可控的",
                ],
                cost_benefit="每日约 5 分钟，收益是持续的秩序感与更低的环境压力，边际成本近乎为零。",
                evidence_level="A",
                evidence_source="环境心理学：秩序环境降低注意力分散与焦虑（环境秩序与认知负荷综述）",
                caveat="适用于轻度杂物；深度囤积 / 无法自主决策时宜寻求专业协助而非硬性自我要求。",
            ),
            Entry(
                id="home-weekly-zone",
                title="每周单区域深度整理",
                purpose="把一次性大扫除拆成每周一片，降低执行阻力并保持可见进度。",
                steps=[
                    "按空间划分 4~6 个区域（如玄关/厨房/书桌/衣柜）",
                    "每周只处理一个区域，其余一律不动",
                    "每个区域定义「保留/归位/丢弃」三通道并当场完成",
                    "记录完成区，下周转下一区",
                ],
                cost_benefit="每周约 30~45 分钟，半年覆盖全屋；避免周末依赖加班式大清扫的情绪消耗。",
                evidence_level="B",
                evidence_source="习惯养成 / 小步拆解原则（行为拆分与持续执行研究）",
                caveat="不要追求一次到位的「极简」；丢弃动作应留有缓冲（如暂存箱）再最终处理。",
            ),
        ],
    ),
    "health": Domain(
        id="health",
        name="健康",
        summary="以规律、可量化的基础动作守护身体，不迷信任一生理指标。",
        entries=[
            Entry(
                id="health-hydration",
                title="工作时段补水节奏",
                purpose="用环境锚点而非意志力，改善常被忽略的饮水缺口。",
                steps=[
                    "工位放一只固定容量水杯，作为可视化锚点",
                    "与既有习惯挂钩：每次上厕所 / 上下午各设定一次接水",
                    "用尿色或整日杯数为粗指标，而非计数强迫",
                ],
                cost_benefit="几乎零成本；明显降低久坐脱水带来的疲劳与头痛概率。",
                evidence_level="C",
                evidence_source="一般健康建议汇总（非单一随机对照，个体差异大）",
                caveat="存在肾病、心衰等需限水情形者不适用；以医嘱为准。",
            ),
            Entry(
                id="health-move-hourly",
                title="每小时起身活动 2 分钟",
                purpose="打断久坐，用微小活动延缓久坐对代谢与颈椎的累积影响。",
                steps=[
                    "可选：用浏览器插件/番茄钟设整点提醒",
                    "起身：走几步、伸懒腰、做 3 次深呼吸的肩颈放松",
                    "把一件事留到起身时顺带完成（如接水/看远处）",
                ],
                cost_benefit="每日累计约 20~30 分钟低强度活动；相比健身房，几乎不占整块时间。",
                evidence_level="B",
                evidence_source="久坐人群间断性活动研究（打断久坐对血糖/血压的即时效应）",
                caveat="若以减脂或增肌为目标，本动作只是基础，不能替代专门训练。",
            ),
        ],
    ),
    "diet": Domain(
        id="diet",
        name="饮食",
        summary="用结构化的餐盘比例而非热量计算，建立易坚持、少痛苦的健康饮食。",
        entries=[
            Entry(
                id="diet-plate-method",
                title="餐盘法：半蔬一蛋白一主食",
                purpose="无需称重计算，用视觉比例建立长期可重复的均衡膳食结构。",
                steps=[
                    "盘子先填一半蔬菜（颜色越杂越好）",
                    "四分之一放优质蛋白（蛋/豆/鱼/瘦肉）",
                    "四分之一放主食（优先粗粮）",
                    "吃前先完成装盘，再开动",
                ],
                cost_benefit="零额外工具成本；长期执行可稳定宏量营养均衡，避免极端节食反噬。",
                evidence_level="A",
                evidence_source="膳食指南餐盘模型（中国居民膳食指南 / 各国饮食指南一致推荐）",
                caveat="肾功能异常者蛋白质摄入需个体化；本方法关注比例而非能量绝对值，减重仍须配合总热量管理。",
            ),
            Entry(
                id="diet-weekly-mealplan",
                title="每周一次菜单预排",
                purpose="用一次决策替代每天纠结，降低饮食决策疲劳与外卖冲动。",
                steps=[
                    "周末用 15 分钟排出未来一周 5 个晚餐主题",
                    "围绕主题列出采购清单，一次买齐",
                    "餐桌上固定两三个「万用组合」覆盖突发事件",
                ],
                cost_benefit="每周决策时间从分散的每天十几分钟压缩到一次；直接减少冲动点外卖。",
                evidence_level="C",
                evidence_source="决策疲劳与行为经济学（选择架构减少选择的实证）",
                caveat="计划不宜过细过死；预留弹性以防突发事件带来的挫败感。",
            ),
        ],
    ),
    "sleep": Domain(
        id="sleep",
        name="睡眠",
        summary="以节律与光环境为核心的睡眠卫生，先稳作息再谈质量。",
        entries=[
            Entry(
                id="sleep-fixed-wakeup",
                title="固定起床时间（而非入睡时间）",
                purpose="以稳定起床为锚稳定昼夜节律，比强迫早睡更可行。",
                steps=[
                    "选定并固定起床时间（含周末误差不超过半小时）",
                    "起床后立即拉开窗帘接触清晨光照",
                    "午睡控制在 20 分钟内，避免影响夜晚睡眠压力",
                ],
                cost_benefit="几乎零成本；固定起床是时相稳定的最强杠杆之一。",
                evidence_level="A",
                evidence_source="昼夜节律与睡眠医学（固定起床对昼夜节律稳定性的证据）",
                caveat="长期缺觉者不建议突然大幅提前起床；渐进调整并配合早睡。",
            ),
            Entry(
                id="sleep-winddown",
                title="睡前 30 分钟降档缓冲",
                purpose="用可预期的低刺激程序，向身体发送「即将入睡」的信号。",
                steps=[
                    "睡前一小时开始降低光照，减少蓝光屏幕",
                    "把手机放在床外充电，设定固定待机位",
                    "进行 30 分钟缓冲：洗漱、阅读纸质书或轻微伸展，不做高强度脑力活",
                ],
                cost_benefit="成本为零；显著缩短入睡潜伏期，减少「躺下清醒刷屏」的时耗。",
                evidence_level="B",
                evidence_source="睡眠卫生研究与睡前光照对褪黑素影响研究",
                caveat="若长期（>3 月）入睡或维持障碍，需排除睡眠呼吸暂停等器质问题，勿仅归因于卫生欠佳。",
            ),
        ],
    ),
    "efficiency": Domain(
        id="efficiency",
        name="效率",
        summary="用外部化、批量化的方法减少决策与切换成本，把精神资源留给正事。",
        entries=[
            Entry(
                id="efficiency-inbox-zero",
                title="收件箱落地（Inbox Zero）",
                purpose="把大脑里的待办外部化，消除「记不住」带来的隐形焦虑。",
                steps=[
                    "选择唯一收纳点（任务清单/本子/便签不求精致）",
                    "新想法一律先落入收件箱，再每周统一分类",
                    "清理标准：已做/规划到某日/删除/归档，四选一",
                ],
                cost_benefit="每周约 20 分钟；大幅降低任务遗忘与「假性多任务」的心理负担。",
                evidence_level="B",
                evidence_source="GTD 外部化与认知卸载研究（外部记忆减轻认知负荷的实证）",
                caveat="工具极简即可，避免在方法论与工具之间来回切换造成二次负担。",
            ),
            Entry(
                id="efficiency-deep-block",
                title="每日一块深度工作时段",
                purpose="用预先划定的不间断时段，确保最重要的事不再被碎片吞噬。",
                steps=[
                    "选定一天中最清醒的时段作为深度块",
                    "提前告知他人该时段勿打扰，关闭非必要通知",
                    "时段内只做一件最重要的事，到点坚决收尾",
                ],
                cost_benefit="每日约 60~90 分钟；深度时段产出常超其余时段总和。",
                evidence_level="A",
                evidence_source="深度工作与专注研究（无干扰专注对产出质量的证据）",
                caveat="深度块需在外界可配合环境下进行；有照料责任者须先安置好他人安排。",
            ),
        ],
    ),
    "finance": Domain(
        id="finance",
        name="财务",
        summary="以自动化与优先级排序管理钱流，不追求刺激更看重确定性。",
        entries=[
            Entry(
                id="finance-three-account",
                title="三账户分流",
                purpose="用账户物理隔离替代意志力，让储蓄先于消费发生。",
                steps=[
                    "开设「日常支出 / 应急备用金 / 长期储蓄」三类账户",
                    "工资到账当日先把储蓄与应急部分转出",
                    "剩余额度作为可自由支配的日常预算",
                ],
                cost_benefit="零额外成本；先储蓄后消费是提升储蓄率最可复制的做法。",
                evidence_level="B",
                evidence_source="行为金融与自动储蓄研究（栅栏效应减弱消费冲动）",
                caveat="应急备用金一般建议 3~6 个月支出；高风险投资不在本条目范围内。",
            ),
            Entry(
                id="finance-subscription-audit",
                title="季度订阅体检",
                purpose="定期清理无感扣费的订阅，停止为不使用的服务持续付费。",
                steps=[
                    "每季度导出一次支付账单，圈出所有定期扣款",
                    "逐项问：过去 3 个月我真用过吗？",
                    "对不用的立即取消，并把仍要保留的列入清单",
                ],
                cost_benefit="每季度约 30 分钟；常能发现被遗忘的订阅，形成持续节流。",
                evidence_level="B",
                evidence_source="订阅经济研究与金融健康实践（自动续费默认效应）",
                caveat="取消前确认是否含年费合约与解约条款，避免违约损失。",
            ),
        ],
    ),
    "relation": Domain(
        id="relation",
        name="关系",
        summary="用少量却稳定的用心动作，维护低频高价值的人际联结。",
        entries=[
            Entry(
                id="relation-touch-base",
                title="定期给重要的人报平安",
                purpose="用低成本的定期问候维持关系温度，避免「久不联系便不好意思联系」。",
                steps=[
                    "维护一张不超过 10 人的重要联系人清单",
                    "为每人设定周期性节奏（如每月一次）",
                    "问候不追求妙语，真诚的一句近况足矣",
                ],
                cost_benefit="每月约 30 分钟；对支持网络与归属感的维护极为高效。",
                evidence_level="C",
                evidence_source="社会联结与心理健康研究（弱联结维护与归属感）",
                caveat="关系维护以双方舒适为度，避免单方面高频打扰造成压力。",
            ),
            Entry(
                id="relation-first-rule",
                title="大事当面/深度沟通",
                purpose="把重要分歧与决定摆到当面，减少文字沟通的误解与延迟伤害。",
                steps=[
                    "判定：涉及情绪、坚持、重大决定时升级为熟人当面沟通",
                    "约定不受打扰的时间与安静环境",
                    "先听完整，再表达；不急于争对错",
                ],
                cost_benefit="一次深入沟通常可换来数周少疑猜；显著降低关系内耗。",
                evidence_level="B",
                evidence_source="沟通研究与关系韧性（非语言线索与冲突解决）",
                caveat="急性冲突中宜先冷却再谈；存在暴力或控制风险时以安全优先。",
            ),
        ],
    ),
    "mind": Domain(
        id="mind",
        name="心理",
        summary="以正念与情绪命名增强情绪调节，降低被情绪绑架的频率。",
        entries=[
            Entry(
                id="mind-naming-emotion",
                title="情绪命名（Labeling）",
                purpose="把模糊的情绪冲动转译为具体命名，夺回一部分自主调节空间。",
                steps=[
                    "察觉身体与心绪的波动信号（心跳/紧绷/烦躁）",
                    "用尽量精确的词命名它：「这是烦躁」「这是对失控的担忧」",
                    "不评判、不镇压，只是观察它如何来去",
                ],
                cost_benefit="零成本、随时可用；长期练习提升情绪粒度与调节能力。",
                evidence_level="A",
                evidence_source="情绪粒度与命名研究（Emotion Granularity 对情绪调节的实证）",
                caveat="本方法为自我调节辅助，不能替代严重的抑郁/焦虑等精神科诊疗。",
            ),
            Entry(
                id="mind-device-pause",
                title="信息摄入前的 10 秒暂停",
                purpose="在刷信息流前建立微小闸门，减少无意识消耗与被动情绪牵动。",
                steps=[
                    "拿起手机前停 10 秒，问：「我现在需要信息，还是在逃避什么？」",
                    "为逃避找到的正事/休息给一个替代动作",
                    "主动检索替代被动投喂",
                ],
                cost_benefit="几乎零成本；长期减少信息焦虑与时段黑洞。",
                evidence_level="C",
                evidence_source="数字成瘾与心智参与研究（主动 vs 被动媒介使用）",
                caveat="若已出现显著功能障碍（工作/学业受损），宜就医评估而非仅自律。",
            ),
        ],
    ),
    "travel": Domain(
        id="travel",
        name="出行",
        summary="用打包模板与行程留白，把出行变得更省心、更从容。",
        entries=[
            Entry(
                id="travel-packing-template",
                title="常年维护的行李清单模板",
                purpose="用一张复用清单消灭每次收拾的遗漏与重来。",
                steps=[
                    "建立一个分类清单（随身/衣物/洗漱/电子/证件）",
                    "每类固定条目，出远门前对照勾选",
                    "新增用品随手补进模板，不用即删",
                ],
                cost_benefit="一次性 20 分钟投入，此后每次出行都省去回忆成本与遗漏补购。",
                evidence_level="C",
                evidence_source="认知卸载与检查清单实践（航空业核对单经验迁移）",
                caveat="廉价航空公司或目的地特殊要求（电源/气候）仍需按次微调。",
            ),
            Entry(
                id="travel-schedule-buffer",
                title="行程每日留白一小时",
                purpose="用缓冲吸收突发，避免「赶行程」把旅行变成另一种上班。",
                steps=[
                    "每天只安排 60% 必做项，其余留白",
                    "重要衔接（机/车/入住）额外预留冗余",
                    "突发时优先放弃弹性项，不让赶路毁掉体验",
                ],
                cost_benefit="无显性成本；显著提升旅途愉悦与抗意外韧性。",
                evidence_level="C",
                evidence_source="旅行体验与时间缓冲实践（非正式幸福感经验总结）",
                caveat="黄金周等热门安排仍须提前预订，留白不等于不规划。",
            ),
        ],
    ),
    "digital": Domain(
        id="digital",
        name="数字生活",
        summary="把数字世界的入口管起来，减少通知与多账号造成的注意力漏损。",
        entries=[
            Entry(
                id="digital-notification-batch",
                title="通知改批处理（批量看）",
                purpose="打破即时通知的被动唤醒，把注意力从被打断中交还给自己。",
                steps=[
                    "关闭非即时必要 App 的推送",
                    "把邮箱、社交设为固定时段集中查看（如上下各一次）",
                    "工作沟通渠道保留即时，娱乐类全部静默",
                ],
                cost_benefit="零成本；大幅减少日均被打断次数，专注与情绪同时受益。",
                evidence_level="B",
                evidence_source="注意力中断与通知研究（即时通知对注意力恢复的负面影响）",
                caveat="需与所在团队约定可接收的响应时效，避免误伤协作。",
            ),
            Entry(
                id="digital-account-vault",
                title="密码与备份托管",
                purpose="用密码管理器与自动备份，把数字资产的流失风险降到最低。",
                steps=[
                    "选用一款密码管理器，把常用账号迁移进去",
                    "开启两步验证；重要云盘开启自动同步/备份",
                    "每季度验证一次恢复路径可走通",
                ],
                cost_benefit="一次性约 1~2 小时配置；此后防账号丢失、防勒索式锁定。",
                evidence_level="B",
                evidence_source="信息安全最佳实践（统一凭据管理与备份冗余）",
                caveat="主密码与恢复码务必线下留存；勿使用短信作为唯一 2FA 于高风险账户。",
            ),
        ],
    ),
    "safety": Domain(
        id="safety",
        name="安全",
        summary="以低成本的预设动作覆盖高频风险，把安全从临场反应变成默认配置。",
        entries=[
            Entry(
                id="safety-family-drill",
                title="家庭应急预设演练",
                purpose="提前彩排火/震/断电等流程，让危机时刻不必临时想。",
                steps=[
                    "与家人商定一处「汇合点」与两位紧急联系人",
                    "走一遍灭火器/逃生通道位置并演示使用",
                    "把关键流程贴在醒目处，每年演练一次",
                ],
                cost_benefit="每年约 1 小时；用极小成本换来危机时可复现的正确动作。",
                evidence_level="A",
                evidence_source="应急准备与防灾教育（预设流程显著提升逃生成功率）",
                caveat="演练应以家庭实际结构为准；有行动不便成员须单独设计撤离方案。",
            ),
            Entry(
                id="safety-digital-hygiene",
                title="链接与附件的三问",
                purpose="用固定核对动作压制钓鱼与社工攻击的最常见入口。",
                steps=[
                    "收到含链接/附件的消息先问：是我预期中的事吗？",
                    "核对域名拼写与发件人地址，不点短链直接访问",
                    "来路不明的附件一律在受控隔离环境打开或放弃",
                ],
                cost_benefit="每次 10 秒；几乎是抵御绝大多数社工攻击的最低成本防线。",
                evidence_level="A",
                evidence_source="社会工程学防护最佳实践（链接感知与来源核验）",
                caveat="高价值账户（财务/工作）应配合硬密钥与最低权限，勿只依赖个人警惕。",
            ),
        ],
    ),
}


def all_domains() -> list[Domain]:
    """按固定插入顺序返回全部域。"""
    return list(_DOMAINS.values())


def domain_count() -> int:
    return len(_DOMAINS)


def get_domain(domain_id: str) -> Domain | None:
    """按 id 取域；不存在返回 None。"""
    return _DOMAINS.get(domain_id)


def get_entry(domain_id: str, entry_id: str) -> tuple[Domain, Entry] | None:
    """按 (域, 条目) 定位；不存在返回 None。返回 (domain, entry)。"""
    domain = _DOMAINS.get(domain_id)
    if domain is None:
        return None
    for entry in domain.entries:
        if entry.id == entry_id:
            return domain, entry
    return None


def search(q: str) -> list[tuple[Domain, Entry]]:
    """在域名/摘要/条目标题/目的/步骤中做不区分大小写子串匹配。"""
    term = (q or "").strip().lower()
    if not term:
        return []
    hits: list[tuple[Domain, Entry]] = []
    for domain in _DOMAINS.values():
        for entry in domain.entries:
            blobs = [
                domain.name,
                domain.summary,
                entry.title,
                entry.purpose,
                " ".join(entry.steps),
                entry.caveat,
            ]
            if any(term in (b or "").lower() for b in blobs):
                hits.append((domain, entry))
    return hits