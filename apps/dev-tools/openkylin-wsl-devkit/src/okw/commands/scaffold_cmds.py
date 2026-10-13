"""脚手架命令：scaffold deb / dput。

ScaffoldError 不在此捕获：统一由 okw.cli.main 单点收口（stderr「错误：…」+ 退出码 1）。
"""

import argparse
import sys

from okw import scaffold


def cmd_scaffold(args: argparse.Namespace) -> int:
    if args.kind == "deb":
        files = scaffold.scaffold_deb(args.project, args.series, args.version, args.output_dir)
        print(f"已生成 debian/ 打包骨架（{len(files)} 个文件）：")
        for f in files:
            print(f"  - {f}")
        print("下一步：编辑 control/changelog → 源码放入项目根 → dpkg-buildpackage -us -uc")
        return 0
    if args.kind == "dput":
        text, written = scaffold.scaffold_dput(args.openkylin_id, output=args.output)
        if written:
            print(f"已写入：{written}")
        else:
            print("配置片段（可重定向到 ~/.dput.cf 或追加）：")
            print(text, end="")
        print("用法：dput okbs:~<你的ID>/ppa <source.changes>（需安装 paramiko / dput-ng）")
        return 0
    print(f"未知 scaffold 类型：{args.kind}", file=sys.stderr)
    return 2
