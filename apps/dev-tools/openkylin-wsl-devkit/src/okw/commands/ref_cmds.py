"""知识快速参考命令：ref。

函数体自原 okw.cli 逐字迁入。
"""

import sys

from okw import ref


def cmd_ref(args) -> int:
    if args.topic:
        topic = ref.get_topic(args.topic)
        if topic is None:
            print(f"未知主题：{args.topic}。可用：{', '.join(ref.list_topics())}", file=sys.stderr)
            return 2
        print(ref.format_topic(topic))
        return 0
    print("== openKylin 知识库参考主题 ==")
    for name in ref.list_topics():
        topic = ref.get_topic(name)
        assert topic is not None
        print(f"  - {name:<16} {topic.title}")
    print("用法：okw ref <主题>（如 okw ref series）")
    return 0
