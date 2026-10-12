"""开发容器镜像子组命令：build / verify。

两个 CLI 包装函数自原 okw.image 逐字迁入；构建/验收流水线仍留在领域模块
okw.image，本模块只做参数解包与调用编排。
"""

from okw import image


def cmd_build(args) -> int:
    """CLI 入口：okw image build <发行版> [--tag] [--base-image] [--pull-base] [--no-cache] [--context]。"""
    report = image.build_run(
        args.name,
        tag=getattr(args, "tag", image.DEFAULT_TAG),
        base_image=getattr(args, "base_image", image.DEFAULT_BASE_IMAGE),
        pull_base=bool(getattr(args, "pull_base", False)),
        no_cache=bool(getattr(args, "no_cache", False)),
        context=getattr(args, "context", None),
    )
    print(image.format_build(report))
    return report.exit_code()


def cmd_verify(args) -> int:
    """CLI 入口：okw image verify <发行版> [--image] [--no-boot]。"""
    report = image.verify_run(
        args.name,
        image=getattr(args, "image", image.DEFAULT_IMAGE),
        no_boot=bool(getattr(args, "no_boot", False)),
    )
    print(image.format_verify(report))
    return report.exit_code()
