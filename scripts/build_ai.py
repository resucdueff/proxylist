#!/usr/bin/env python3
"""生成 ai/ai.yaml 与 ai/ai.list（Clash Meta / mihomo classical 规则集）。

流程：抓取上游社区规则 -> 合并 ai/extra.txt -> 按 ai/exclude.txt 过滤
     -> 去重、去冗余（被 DOMAIN-SUFFIX 覆盖的子域名）-> 按服务分组排序写出。

用法：python3 scripts/build_ai.py            # 在仓库根目录运行
     python3 scripts/build_ai.py --offline  # 只用 extra.txt（调试用）
"""
import argparse
import datetime as dt
import re
import sys
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
AI_DIR = ROOT / "ai"

GH = "https://raw.githubusercontent.com"
SOURCES = [
    # (名称, URL, 格式)
    ("MetaCubeX/meta-rules-dat geosite category-ai-!cn（基于 v2fly/domain-list-community）",
     f"{GH}/MetaCubeX/meta-rules-dat/meta/geo/geosite/category-ai-!cn.list", "mihomo-domain"),
    ("blackmatrix7/ios_rule_script OpenAI",
     f"{GH}/blackmatrix7/ios_rule_script/master/rule/Clash/OpenAI/OpenAI.yaml", "clash-yaml"),
    ("blackmatrix7/ios_rule_script Claude",
     f"{GH}/blackmatrix7/ios_rule_script/master/rule/Clash/Claude/Claude.yaml", "clash-yaml"),
    ("blackmatrix7/ios_rule_script Gemini",
     f"{GH}/blackmatrix7/ios_rule_script/master/rule/Clash/Gemini/Gemini.yaml", "clash-yaml"),
    ("blackmatrix7/ios_rule_script Copilot",
     f"{GH}/blackmatrix7/ios_rule_script/master/rule/Clash/Copilot/Copilot.yaml", "clash-yaml"),
    ("ACL4SSR Clash/Ruleset/AI.list",
     f"{GH}/ACL4SSR/ACL4SSR/master/Clash/Ruleset/AI.list", "clash-text"),
]

TYPES = ("DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD")
TYPE_ORDER = {"DOMAIN-SUFFIX": 0, "DOMAIN": 1, "DOMAIN-KEYWORD": 2}
DOMAIN_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$")
KEYWORD_RE = re.compile(r"^[a-z0-9-]{4,}$")

# 分组：按顺序匹配。片段含 "." 时按域名后缀匹配（x.ai 不会误匹配 pplx.ai），否则按子串匹配
GROUPS = [
    ("OpenAI / ChatGPT / Sora", ["openai", "chatgpt", "oaistatic", "oaiusercontent", "oaistatsig",
                                 "sora.com", "chat.com", "crixet", "livekit.cloud", "o33249"]),
    ("Anthropic / Claude", ["anthropic", "claude", "clau.de", "ant.dev", "antspace"]),
    ("Google Gemini / AI Studio / NotebookLM / Labs / DeepMind",
     ["google", "googleapis", "gstatic", "deepmind", "ai.studio", "goog", "makersuite"]),
    ("xAI / Grok", ["x.ai", "grok"]),
    ("GitHub Copilot", ["githubcopilot", "copilot-proxy", "copilot-telemetry", "githubnext",
                        "copilotprodattachments"]),
    ("Microsoft Copilot / Bing / Azure AI", ["copilot", "bing", "azure"]),
    ("Meta AI", ["meta.ai", "metaai"]),
    ("Perplexity", ["perplexity", "pplx"]),
    ("Mistral / Cohere / AI21 / Inflection", ["mistral", "cohere", "ai21", "pi.ai"]),
    ("Hugging Face", ["huggingface", "hf.co", "hf.space"]),
    ("Poe / Character.AI / You.com / Phind", ["poe", "character.ai", "c.ai", "you.com", "phind"]),
    ("图像 / 视频生成", ["midjourney", "stability", "dreamstudio", "runway", "pika", "lumalabs",
                    "ideogram", "leonardo", "krea", "civitai", "heygen", "synthesia", "clipdrop",
                    "openart", "lovart", "magnific", "tripo3d", "novelai", "comfy", "oystermercury"]),
    ("语音 / 音乐", ["elevenlabs", "suno", "udio.com"]),
    ("编程助手", ["cursor", "windsurf", "codeium", "jetbrains", "grazie", "devin", "coderabbit",
               "kiro", "opencode", "qoder", "trae", "marscode", "deepwiki", "typesafe"]),
    ("推理 / API 平台", ["replicate", "together", "groq", "fireworks", "openrouter", "deepinfra",
                     "cerebras", "chutes", "gateway.ai.cloudflare.com", "ollama", "lmstudio"]),
    ("写作 / 翻译 / 办公", ["deepl", "jasper", "gamma.app", "notegpt", "sider"]),
    ("ByteDance 海外 AI（Coze / Cici / Dola）", ["coze", "cici", "dola"]),
]
OTHER = "其他境外 AI 服务"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "proxylist-build/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def parse_rule_line(line):
    line = line.split("#", 1)[0].strip().strip("'\"")
    if line.startswith("- "):
        line = line[2:].strip().strip("'\"")
    if not line or line.startswith("payload"):
        return None
    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 2 or parts[0].upper() not in TYPES:
        return None  # 忽略 IP-CIDR / IP-ASN / PROCESS 等非域名规则
    return parts[0].upper(), parts[1].lower().rstrip(".")


def parse(text, fmt):
    out = []
    for raw in text.splitlines():
        if fmt == "mihomo-domain":
            s = raw.split("#", 1)[0].strip().lower()
            if not s:
                continue
            if s.startswith("+."):
                out.append(("DOMAIN-SUFFIX", s[2:]))
            elif s.startswith("."):
                out.append(("DOMAIN-SUFFIX", s[1:]))
            else:
                out.append(("DOMAIN", s))
        else:
            r = parse_rule_line(raw)
            if r:
                out.append(r)
    return out


def load_exclude(path):
    exact, suffix, keywords = set(), set(), set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        s = raw.split("#", 1)[0].strip().lower()
        if not s:
            continue
        if s.startswith("keyword:"):
            keywords.add(s.split(":", 1)[1])
        elif s.startswith("+."):
            suffix.add(s[2:])
        else:
            exact.add(s)
    return exact, suffix, keywords


def excluded(rule, ex):
    exact, suffix, keywords = ex
    t, v = rule
    if t == "DOMAIN-KEYWORD":
        return v in keywords
    if v in exact:
        return True
    return any(v == s or v.endswith("." + s) for s in suffix)


def valid(rule):
    t, v = rule
    return bool(KEYWORD_RE.match(v)) if t == "DOMAIN-KEYWORD" else bool(DOMAIN_RE.match(v))


def prune(rules):
    """去掉被某条 DOMAIN-SUFFIX 覆盖的 DOMAIN / 子域 DOMAIN-SUFFIX。"""
    suffixes = {v for t, v in rules if t == "DOMAIN-SUFFIX"}

    def covered(v, self_suffix):
        labels = v.split(".")
        for i in range(1 if self_suffix else 0, len(labels) - 1):
            parent = ".".join(labels[i:])
            if parent in suffixes and not (self_suffix and parent == v):
                return True
        return False

    out = set()
    for t, v in rules:
        if t == "DOMAIN-SUFFIX" and covered(v, True):
            continue
        if t == "DOMAIN" and covered(v, False):
            continue
        out.add((t, v))
    return out


def group_of(v):
    for name, pats in GROUPS:
        if any((v == p or v.endswith("." + p)) if "." in p else (p in v) for p in pats):
            return name
    return OTHER


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="不抓上游，只用 extra.txt")
    args = ap.parse_args()

    rules, used = set(), []
    if not args.offline:
        for name, url, fmt in SOURCES:
            try:
                got = parse(fetch(url), fmt)
            except Exception as e:  # 任一上游失败就退出，避免规则悄悄变少
                sys.exit(f"[错误] 抓取失败 {name}: {e}")
            print(f"[上游] {name}: {len(got)} 条", file=sys.stderr)
            rules.update(got)
            used.append((name, url))
    extra = parse((AI_DIR / "extra.txt").read_text(encoding="utf-8"), "clash-text")
    print(f"[补充] ai/extra.txt: {len(extra)} 条", file=sys.stderr)
    rules.update(extra)

    ex = load_exclude(AI_DIR / "exclude.txt")
    bad = sorted(r for r in rules if not valid(r))
    for r in bad:
        print(f"[跳过非法] {r}", file=sys.stderr)
    rules = {r for r in rules if valid(r) and not excluded(r, ex)}
    rules = prune(rules)

    grouped = {}
    for t, v in rules:
        grouped.setdefault(group_of(v), []).append((t, v))
    order = [g for g, _ in GROUPS] + [OTHER]
    for g in grouped:
        grouped[g].sort(key=lambda r: (TYPE_ORDER[r[0]], r[1]))

    now = dt.datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    total = len(rules)
    header = [
        "# 名称: ai（中国大陆境外 AI 服务域名）",
        f"# 更新时间: {now} (Asia/Shanghai, UTC+8)",
        f"# 规则数: {total}",
        "# 仓库: https://github.com/resucdueff/proxylist",
        "# 生成脚本: scripts/build_ai.py",
        "# 来源:",
    ] + [f"#   - {n}: {u}" for n, u in used] + ["#   - 手工补充: ai/extra.txt（官方文档 / 实测）",
                                         "# 排除: ai/exclude.txt（大陆 AI 服务、通用 CDN / 统计 / 支付域名）"]

    yaml_lines = header + ["payload:"]
    list_lines = list(header)
    for g in order:
        if g not in grouped:
            continue
        yaml_lines.append(f"  # {g}")
        list_lines.append(f"# {g}")
        for t, v in grouped[g]:
            yaml_lines.append(f"  - {t},{v}")
            list_lines.append(f"{t},{v}")
    (AI_DIR / "ai.yaml").write_text("\n".join(yaml_lines) + "\n", encoding="utf-8")
    (AI_DIR / "ai.list").write_text("\n".join(list_lines) + "\n", encoding="utf-8")
    print(f"[完成] 写出 {total} 条规则 -> ai/ai.yaml, ai/ai.list", file=sys.stderr)


if __name__ == "__main__":
    main()
