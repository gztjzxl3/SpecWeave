"""环境验收命令：verify（openKylin 五步验收）。

WslError 不在此捕获：统一由 okw.cli.main 单点收口（stderr「错误：…」+ 退出码 1）。
"""

from okw import distro, verify


def cmd_verify(args) -> int:
    default_before = distro.default_distro_name()
    report = verify.verify(args.name, default_before=default_before)
    print(verify.format_report(report))
    return 0 if report.all_passed else 1
