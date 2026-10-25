#!/usr/bin/env python3
"""生成 github / linux / docker 三个规则集（手工维护的数据都在本文件里）。

用法: python3 scripts/build_dev.py
输出: github/github.{yaml,list}  linux/linux.{yaml,list}  docker/docker.{yaml,list}
不参与 scripts/build_ai.py 的每周自动合并；想增删域名直接改下面的 RULESETS。
"""
import datetime
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TZ = datetime.timezone(datetime.timedelta(hours=8))
REPO = "https://github.com/resucdueff/proxylist"

S = "DOMAIN-SUFFIX"
D = "DOMAIN"

RULESETS = {
    "github": {
        "title": "github（GitHub 全家：网页、Git、Raw、Release、Pages、Actions、GHCR）",
        "sources": [
            "v2fly/domain-list-community data/github: https://github.com/v2fly/domain-list-community/blob/master/data/github",
            "GitHub 文档 About GitHub's IP addresses / 网络白名单: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-githubs-ip-addresses",
        ],
        "notes": [
            "Copilot 相关（githubcopilot.com、copilot-*.githubusercontent.com、copilot-workspace.githubnext.com）已在 ai 规则集，未重复收录；",
            "  需要 Copilot 走 AI 分组时，把 RULE-SET,ai 放在 RULE-SET,github 前面",
            "ghcr.io 同时收录在 docker 规则集（单独使用 docker 时也能拉 GHCR 镜像）",
        ],
        "sections": [
            ("GitHub 主站", [
                ("GitHub - 网页 / API / Git (HTTPS) / codeload 源码包", [
                    (S, "github.com"),
                ]),
                ("GitHub - Raw / Release 下载 / 头像 / 附件（raw、objects、release-assets、avatars、camo、user-images、media）", [
                    (S, "githubusercontent.com"),
                ]),
                ("GitHub - 静态资源（github.githubassets.com）", [
                    (S, "githubassets.com"),
                ]),
                ("GitHub - 桌面端 / 内部服务", [
                    (S, "githubapp.com"),
                ]),
                ("GitHub - Pages", [
                    (S, "github.io"),
                ]),
                ("GitHub - Codespaces / github.dev 网页编辑器", [
                    (S, "github.dev"),
                    (S, "githubpreview.dev"),
                ]),
                ("GitHub - 企业版云（数据驻留，*.ghe.com）", [
                    (S, "ghe.com"),
                ]),
                ("GitHub - 短链接", [
                    (S, "gh.io"),
                    (S, "git.io"),
                    (S, "repo.new"),
                ]),
                ("GitHub - 注册 / 登录人机验证", [
                    (S, "octocaptcha.com"),
                    (D, "github-api.arkoselabs.com"),
                ]),
            ]),
            ("GitHub 存储与 CDN", [
                ("GitHub - Release / LFS / 附件存储（AWS S3）", [
                    (D, "github-cloud.s3.amazonaws.com"),
                    (D, "github-production-release-asset-2e65be.s3.amazonaws.com"),
                    (D, "github-production-repository-file-5c1aeb.s3.amazonaws.com"),
                    (D, "github-production-repository-image-32fea6.s3.amazonaws.com"),
                    (D, "github-production-upload-manifest-file-7fdce7.s3.amazonaws.com"),
                    (D, "github-production-user-asset-6210df.s3.amazonaws.com"),
                ]),
                ("GitHub - Actions 日志 / 产物（Azure Blob）", [
                    (D, f"productionresultssa{i}.blob.core.windows.net") for i in range(20)
                ]),
                ("GitHub - Fastly CDN 入口", [
                    (D, "github.global.ssl.fastly.net"),
                    (D, "github.map.fastly.net"),
                ]),
            ]),
            ("GitHub 容器 / 包", [
                ("GitHub - Container Registry（GHCR）", [
                    (S, "ghcr.io"),
                ]),
            ]),
            ("GitHub 周边站点", [
                ("GitHub - 状态页 / 博客 / 社区 / 支持", [
                    (S, "githubstatus.com"),
                    (S, "github.blog"),
                    (S, "github.community"),
                    (S, "githubsupport.com"),
                ]),
                ("GitHub - Next 实验项目 / Universe 大会 / 开源指南", [
                    (S, "githubnext.com"),
                    (S, "githubuniverse.com"),
                    (S, "opensource.guide"),
                ]),
                ("GitHub - Dependabot", [
                    (S, "dependabot.com"),
                ]),
            ]),
        ],
    },
    "linux": {
        "title": "linux（Linux 发行版官方源 / 镜像站 / 内核与通用包仓库）",
        "sources": [
            "v2fly/domain-list-community data/debian、ubuntu、canonical、launchpad、snapcraft、archlinux、fedora、nixos、kernel",
            "各发行版官方文档中的默认软件源地址（sources.list / repositories / yum.repos.d / mirrorlist）",
        ],
        "notes": [
            "只收录境外官方源；清华 TUNA、中科大 USTC、阿里云、华为云、腾讯云等国内镜像站应继续直连（本文件不含）",
            "Fedora / CentOS / Rocky / Alma / openSUSE / Arch 的 mirrorlist / metalink 按出口 IP 分配镜像，",
            "  走代理后可能分配到节点所在地区的第三方镜像（这些镜像不在本规则内、会直连），速度反而可能变差；",
            "  这类发行版更推荐直接把源换成国内镜像，本规则主要保证官方主站、Alpine / Debian / Ubuntu 等固定域名源可用",
        ],
        "sections": [
            ("Alpine", [
                ("Alpine Linux - 官方源 dl-cdn / 官网 / pkgs / GitLab", [
                    (S, "alpinelinux.org"),
                ]),
            ]),
            ("Debian 系", [
                ("Debian - deb.debian.org / security.debian.org / snapshot / salsa", [
                    (S, "debian.org"),
                    (S, "debian.net"),
                ]),
                ("Canonical - Ubuntu 官方源 archive / security / ports / cloud-images", [
                    (S, "ubuntu.com"),
                    (S, "canonical.com"),
                ]),
                ("Canonical - Launchpad / PPA", [
                    (S, "launchpad.net"),
                    (S, "launchpadcontent.net"),
                    (S, "launchpadlibrarian.net"),
                ]),
                ("Canonical - Snap 商店", [
                    (S, "snapcraft.io"),
                    (S, "snapcraftcontent.com"),
                    (S, "snapstore.io"),
                ]),
                ("Kali Linux - 官方源 http.kali.org / kali.download", [
                    (S, "kali.org"),
                    (S, "kali.download"),
                ]),
                ("Linux Mint - 官方源", [
                    (S, "linuxmint.com"),
                ]),
                ("Raspberry Pi - archive.raspberrypi.com / .org", [
                    (S, "raspberrypi.com"),
                    (S, "raspberrypi.org"),
                ]),
                ("Armbian - 官方源", [
                    (S, "armbian.com"),
                ]),
                ("Proxmox - download.proxmox.com", [
                    (S, "proxmox.com"),
                ]),
            ]),
            ("Red Hat 系", [
                ("Fedora - 官方源 / EPEL / Copr", [
                    (S, "fedoraproject.org"),
                    (S, "getfedora.org"),
                    (S, "fedorapeople.org"),
                    (S, "fedorainfracloud.org"),
                ]),
                ("Red Hat - RHEL 订阅源 CDN", [
                    (D, "cdn.redhat.com"),
                ]),
                ("CentOS - mirror.stream / vault", [
                    (S, "centos.org"),
                ]),
                ("Rocky Linux - 官方源", [
                    (S, "rockylinux.org"),
                ]),
                ("AlmaLinux - 官方源", [
                    (S, "almalinux.org"),
                ]),
                ("Oracle Linux - yum.oracle.com", [
                    (D, "yum.oracle.com"),
                ]),
            ]),
            ("Arch 系", [
                ("Arch Linux - 官方源 / AUR / Wiki", [
                    (S, "archlinux.org"),
                    (S, "pkgbuild.com"),
                ]),
                ("Arch Linux ARM - 官方源", [
                    (S, "archlinuxarm.org"),
                ]),
                ("Manjaro - 官方源", [
                    (S, "manjaro.org"),
                ]),
            ]),
            ("其他发行版", [
                ("openSUSE - download.opensuse.org / OBS", [
                    (S, "opensuse.org"),
                ]),
                ("Gentoo - distfiles / rsync / 官网", [
                    (S, "gentoo.org"),
                ]),
                ("NixOS - cache.nixos.org / channels / nix.dev", [
                    (S, "nixos.org"),
                    (S, "nix.dev"),
                ]),
                ("Cachix - Nix 二进制缓存", [
                    (S, "cachix.org"),
                ]),
                ("Void Linux - 官方源", [
                    (S, "voidlinux.org"),
                ]),
            ]),
            ("通用", [
                ("Linux 内核 - kernel.org / git.kernel.org / cdn.kernel.org", [
                    (S, "kernel.org"),
                ]),
                ("Flatpak - Flathub", [
                    (S, "flathub.org"),
                    (S, "flatpak.org"),
                ]),
            ]),
        ],
    },
    "docker": {
        "title": "docker（Docker Hub 及常用境外容器镜像仓库、Kubernetes 官方源）",
        "sources": [
            "v2fly/domain-list-community data/docker、kubernetes: https://github.com/v2fly/domain-list-community/blob/master/data/docker",
            "Docker 文档 Allowlist for Docker Desktop / Docker Hub: https://docs.docker.com/desktop/setup/allow-list/",
            "Kubernetes registry.k8s.io 说明: https://github.com/kubernetes/registry.k8s.io",
        ],
        "notes": [
            "ghcr.io 与 github 规则集重复收录，方便单独使用",
            "registry.k8s.io 会把镜像层重定向到 AWS S3 / Google Artifact Registry 等地址，S3 部分未收录（域名按区域变化），如拉取仍慢可开 sniffer 观察后自行补充",
            "未收录 mcr.microsoft.com（微软镜像仓库国内直连通常可用），需要时自行加 DOMAIN-SUFFIX,mcr.microsoft.com",
        ],
        "sections": [
            ("Docker", [
                ("Docker - Docker Hub 镜像仓库（registry-1 / auth / index.docker.io）", [
                    (S, "docker.io"),
                ]),
                ("Docker - 官网 / Hub 网页 / 镜像层 CDN production.cloudflare / download.docker.com 安装源 / Desktop / 登录", [
                    (S, "docker.com"),
                    (S, "dockerstatic.com"),
                ]),
                ("Docker - 镜像层存储（Cloudflare R2）", [
                    (D, "docker-images-prod.6aa30f8b08e16409b46e0173d6de2f56.r2.cloudflarestorage.com"),
                ]),
                ("Docker - Compose 规范", [
                    (S, "compose-spec.io"),
                ]),
            ]),
            ("Kubernetes", [
                ("Kubernetes - registry.k8s.io / dl.k8s.io / pkgs.k8s.io / 官网", [
                    (S, "k8s.io"),
                    (S, "kubernetes.io"),
                ]),
                ("Google - Container Registry（gcr.io、k8s.gcr.io）/ Artifact Registry（*-docker.pkg.dev）", [
                    (S, "gcr.io"),
                    (S, "pkg.dev"),
                ]),
                ("Helm - get.helm.sh / Artifact Hub", [
                    (S, "helm.sh"),
                    (S, "artifacthub.io"),
                ]),
            ]),
            ("其他镜像仓库", [
                ("GitHub - Container Registry（GHCR）", [
                    (S, "ghcr.io"),
                ]),
                ("Red Hat - Quay.io", [
                    (S, "quay.io"),
                    (D, "quay-registry.s3.amazonaws.com"),
                ]),
                ("Red Hat - registry.redhat.io / registry.access.redhat.com", [
                    (S, "redhat.io"),
                    (D, "registry.access.redhat.com"),
                ]),
                ("AWS - ECR Public", [
                    (S, "public.ecr.aws"),
                ]),
                ("NVIDIA - NGC（nvcr.io）", [
                    (S, "nvcr.io"),
                ]),
                ("Elastic - docker.elastic.co", [
                    (D, "docker.elastic.co"),
                ]),
                ("GitLab - Container Registry", [
                    (D, "registry.gitlab.com"),
                ]),
            ]),
        ],
    },
}


def build(name, cfg, now):
    rules = [r for _, groups in cfg["sections"] for _, items in groups for r in items]
    keys = [f"{t},{v}" for t, v in rules]
    dup = {k for k in keys if keys.count(k) > 1}
    assert not dup, f"{name}: 重复规则 {dup}"
    head = [
        f"# 名称: {cfg['title']}",
        f"# 更新时间: {now} (Asia/Shanghai, UTC+8)",
        f"# 规则数: {len(rules)}",
        f"# 仓库: {REPO}",
        "# 维护方式: 手工整理，由 scripts/build_dev.py 生成，不参与 scripts/build_ai.py 自动合并",
        "# 来源:",
        *[f"#   - {s}" for s in cfg["sources"]],
        *[("# 说明: " if i == 0 else "#       ") + n for i, n in enumerate(cfg["notes"])],
    ]
    yml, lst = head + ["payload:"], list(head)
    for sec, groups in cfg["sections"]:
        yml.append(f"  # ===== {sec} =====")
        lst.append(f"# ===== {sec} =====")
        for g, items in groups:
            yml.append(f"  # {g}")
            lst.append(f"# {g}")
            for t, v in items:
                yml.append(f"  - {t},{v}")
                lst.append(f"{t},{v}")
    d = ROOT / name
    d.mkdir(exist_ok=True)
    (d / f"{name}.yaml").write_text("\n".join(yml) + "\n", encoding="utf-8")
    (d / f"{name}.list").write_text("\n".join(lst) + "\n", encoding="utf-8")
    print(f"{name}: {len(rules)} 条")


if __name__ == "__main__":
    now = datetime.datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
    for n, c in RULESETS.items():
        build(n, c, now)
