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

# 分组：按顺序匹配，先命中先归组（越具体的放越前）。
# 片段含 "." 时按域名后缀匹配（x.ai 不会误匹配 pplx.ai），否则按子串匹配。
# 输出按 分区 -> "公司 - 服务" 两级注释；新增规则若没命中任何组，会落到最后的"其他"组，记得来这里补。
S_INTL = "境外 AI 公司"
S_CN = "中国公司海外 AI（仅海外站）"
GROUPS = [
    (S_INTL, 'OpenAI - Sora', ['sora.com']),
    (S_INTL, 'Microsoft - Azure AI / Azure OpenAI', ['ai.azure.com', 'openai.azure.com']),
    (S_INTL, 'OpenAI - ChatGPT', ['chatgpt', 'chat.com', 'oaiusercontent.com', 'oaistatic.com', 'livekit.cloud', 'openai-api.arkoselabs.com', 'o33249']),
    (S_INTL, 'OpenAI - 官网 / API / 静态资源', ['openai', 'oaistatsig.com', 'crixet.com']),
    (S_INTL, 'Anthropic - Claude', ['claude', 'clau.de']),
    (S_INTL, 'Anthropic - 官网 / API', ['anthropic', 'ant.dev', 'antspace.dev']),
    (S_INTL, 'Google - AI Studio / Gemini API', ['aistudio.google.com', 'ai.studio', 'makersuite.google.com', 'alkali', 'generativelanguage.googleapis.com', 'ai.google.dev', 'generativeai.google']),
    (S_INTL, 'Google - NotebookLM', ['notebooklm', 'notebook.google', 'notebook.google.com']),
    (S_INTL, 'Google - Gemini', ['gemini', 'bard.google.com', 'proactivebackend-pa.googleapis.com', 'robinfrontend-pa.googleapis.com', 'geller-pa.googleapis.com']),
    (S_INTL, 'Google - Labs（Flow / Opal / Stitch）', ['labs.google', 'labs.google.com', 'labstailwind', 'flow.google', 'flow.google.com', 'opal.google', 'opal.google.com', 'stitch.withgoogle.com', 'aisandbox-pa.googleapis.com']),
    (S_INTL, 'Google - Jules', ['jules.google', 'jules.google.com']),
    (S_INTL, 'Google - Antigravity', ['antigravity']),
    (S_INTL, 'Google - Gemini Code Assist', ['cloudaicompanion.googleapis.com', 'cloudcode-pa', 'aicode.googleapis.com']),
    (S_INTL, 'Google - Vertex AI', ['aiplatform.googleapis.com']),
    (S_INTL, 'Google - DeepMind', ['deepmind']),
    (S_INTL, 'Google - 其他 AI 接口', ['aida.googleapis.com']),
    (S_INTL, 'xAI - Grok', ['grok.com', 'grok.x.com']),
    (S_INTL, 'xAI - Grokipedia', ['grokipedia.com']),
    (S_INTL, 'xAI - 官网 / API', ['x.ai']),
    (S_INTL, 'GitHub - Copilot', ['githubcopilot', 'copilot-proxy', 'copilot-telemetry', 'githubnext', 'copilotprodattachments']),
    (S_INTL, 'Microsoft - Copilot', ['copilot.microsoft.com', 'copilot.cloud.microsoft', 'copilot.com', 'copilot-stg.com', 'sydney.bing.com', 'edgeservices.bing.com']),
    (S_INTL, 'Meta - Meta AI', ['meta.ai', 'metaaivm.com']),
    (S_INTL, 'Perplexity - Perplexity', ['perplexity', 'pplx', 'ppl-ai-file-upload']),
    (S_INTL, 'Mistral - Le Chat / API', ['mistral.ai']),
    (S_INTL, 'Cohere - Cohere', ['cohere.ai', 'cohere.com']),
    (S_INTL, 'AI21 - AI21', ['ai21.com']),
    (S_INTL, 'Inflection - Pi', ['pi.ai']),
    (S_INTL, 'Hugging Face - Hugging Face', ['huggingface.co', 'hf.co', 'hf.space']),
    (S_INTL, 'Quora - Poe', ['poe.com', 'poecdn.net']),
    (S_INTL, 'Character.AI - Character.AI', ['character.ai', 'c.ai']),
    (S_INTL, 'You.com - You.com', ['you.com']),
    (S_INTL, 'Phind - Phind', ['phind.com']),
    (S_INTL, 'LMArena - Arena', ['arena.ai']),
    (S_INTL, 'DuckDuckGo - Duck.ai', ['duck.ai']),
    (S_INTL, 'The Browser Company - Dia', ['diabrowser.com', 'diabrowser.engineering']),
    (S_INTL, 'Midjourney - Midjourney', ['midjourney.com']),
    (S_INTL, 'Stability AI - Stability / DreamStudio', ['stability.ai', 'dreamstudio.ai']),
    (S_INTL, 'Jasper - Jasper / Clipdrop', ['jasper.ai', 'clipdrop.co']),
    (S_INTL, 'Runway - Runway', ['runwayml.com']),
    (S_INTL, 'Pika - Pika', ['pika.art']),
    (S_INTL, 'Luma AI - Dream Machine', ['lumalabs.ai']),
    (S_INTL, 'Ideogram - Ideogram', ['ideogram.ai']),
    (S_INTL, 'Leonardo.Ai - Leonardo', ['leonardo.ai']),
    (S_INTL, 'Krea - Krea', ['krea.ai']),
    (S_INTL, 'Civitai - Civitai', ['civitai.com']),
    (S_INTL, 'HeyGen - HeyGen', ['heygen.com']),
    (S_INTL, 'Synthesia - Synthesia', ['synthesia.io']),
    (S_INTL, 'OpenArt - OpenArt', ['openart.ai']),
    (S_INTL, 'Freepik - Magnific', ['magnific.com']),
    (S_INTL, 'Anlatan - NovelAI', ['novelai.net']),
    (S_INTL, 'Comfy Org - ComfyUI', ['comfy', 'oystermercury.top']),
    (S_INTL, 'ElevenLabs - ElevenLabs', ['elevenlabs.io', 'elevenlabs.com']),
    (S_INTL, 'Suno - Suno', ['suno.com', 'suno.ai']),
    (S_INTL, 'Udio - Udio', ['udio.com']),
    (S_INTL, 'Anysphere - Cursor', ['cursor']),
    (S_INTL, 'Windsurf - Windsurf / Codeium', ['windsurf', 'codeium']),
    (S_INTL, 'JetBrains - JetBrains AI', ['jetbrains.ai', 'grazie']),
    (S_INTL, 'Cognition - Devin / DeepWiki', ['devin.ai', 'deepwiki']),
    (S_INTL, 'CodeRabbit - CodeRabbit', ['coderabbit']),
    (S_INTL, 'Amazon - Kiro', ['kiro.dev']),
    (S_INTL, 'SST - OpenCode', ['opencode.ai']),
    (S_INTL, 'Zed - Agent Client Protocol', ['agentclientprotocol.com']),
    (S_INTL, 'Replicate - Replicate', ['replicate.com', 'replicate.delivery']),
    (S_INTL, 'Together AI - Together', ['together.ai', 'together.xyz']),
    (S_INTL, 'Groq - Groq', ['groq.com']),
    (S_INTL, 'Fireworks AI - Fireworks', ['fireworks.ai']),
    (S_INTL, 'OpenRouter - OpenRouter', ['openrouter.ai']),
    (S_INTL, 'DeepInfra - DeepInfra', ['deepinfra.com']),
    (S_INTL, 'Cerebras - Cerebras', ['cerebras.ai']),
    (S_INTL, 'Chutes - Chutes', ['chutes.ai']),
    (S_INTL, 'Cloudflare - AI Gateway', ['gateway.ai.cloudflare.com']),
    (S_INTL, 'Ollama - Ollama', ['ollama.com']),
    (S_INTL, 'Element Labs - LM Studio', ['lmstudio.ai']),
    (S_INTL, 'LangChain - LangChain', ['langchain.com']),
    (S_INTL, 'CrewAI - CrewAI', ['crewai.com']),
    (S_INTL, 'OpenClaw - OpenClaw / ClawHub', ['openclaw.ai', 'clawhub.ai']),
    (S_INTL, 'LangGenius - Dify', ['dify.ai']),
    (S_INTL, 'Mintplex Labs - AnythingLLM', ['anythingllm.com']),
    (S_INTL, 'H2O.ai - H2O.ai', ['h2o.ai']),
    (S_INTL, 'Mozilla - Mozilla.ai', ['mozilla.ai']),
    (S_INTL, 'YouMind - YouMind', ['youmind.ai', 'youmind.com', 'youmind.site']),
    (S_INTL, 'NoteGPT - NoteGPT', ['notegpt.io']),
    (S_INTL, 'DeepL - DeepL', ['deepl.com']),
    (S_INTL, 'Gamma - Gamma', ['gamma.app']),
    (S_CN, 'Moonshot - Kimi intl', ['kimi.ai']),
    (S_CN, 'Moonshot - API intl', ['moonshot.ai']),
    (S_CN, 'Kuaishou - Kling intl', ['klingai.com', 'kling.ai']),
    (S_CN, 'MiniMax - 海外站 / Agent / API', ['minimax.io']),
    (S_CN, 'MiniMax - Hailuo intl', ['hailuoai.video']),
    (S_CN, 'MiniMax - Talkie', ['talkie-ai.com']),
    (S_CN, 'Alibaba - Qwen intl', ['qwen.ai', 'qwenlm.ai']),
    (S_CN, 'Alibaba - Wan intl', ['wan.video']),
    (S_CN, 'Alibaba - Tongyi intl', ['tongyi.ai']),
    (S_CN, 'Alibaba Cloud - Model Studio intl', ['dashscope-intl.aliyuncs.com', 'modelstudio.console.alibabacloud.com']),
    (S_CN, 'Alibaba - Qoder', ['qoder.com']),
    (S_CN, 'Zhipu - Z.ai', ['z.ai']),
    (S_CN, 'ByteDance - Dreamina', ['dreamina.capcut.com']),
    (S_CN, 'ByteDance - Seed', ['seed.bytedance.com']),
    (S_CN, 'ByteDance - BytePlus ModelArk', ['bytepluses.com', 'console.byteplus.com']),
    (S_CN, 'ByteDance - Coze', ['coze.com']),
    (S_CN, 'ByteDance - Cici / Dola', ['cici.com', 'ciciai.com', 'ciciaicdn.com', 'dola.com']),
    (S_CN, 'ByteDance - Trae / MarsCode', ['trae.ai', 'marscode.com']),
    (S_CN, 'Tencent - Hunyuan intl', ['hunyuanglobal.com', 'hunyuan.intl.tencentcloudapi.com']),
    (S_CN, 'Butterfly Effect - Manus', ['manus.im', 'manuscdn.com', 'manus.space']),
    (S_CN, 'Butterfly Effect - Monica', ['monica.im']),
    (S_CN, 'MainFunc - Genspark', ['genspark.ai']),
    (S_CN, 'Shengshu - Vidu intl', ['vidu.com', 'vidu.studio']),
    (S_CN, 'AIsphere - PixVerse', ['pixverse.ai']),
    (S_CN, 'Cloud Whale - PolyBuzz', ['polybuzz.ai']),
    (S_CN, 'SeaArt - SeaArt', ['seaart.ai']),
    (S_CN, 'Tensor.Art - Tensor.Art', ['tensor.art']),
    (S_CN, 'HiDream - Vivago', ['vivago.ai']),
    (S_CN, 'StepFun - 海外站 / API', ['stepfun.ai']),
    (S_CN, '01.AI - 海外站 / API', ['01.ai']),
    (S_CN, 'Kunlun Tech - Skywork', ['skywork.ai']),
    (S_CN, 'Kunlun Tech - Mureka', ['mureka.ai']),
    (S_CN, 'VAST - Tripo', ['tripo3d.ai']),
    (S_CN, 'LiblibAI - Lovart', ['lovart.ai']),
    (S_CN, 'Sider - Sider', ['sider.ai']),
]
OTHER = (S_INTL, "其他 - 未分类")


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
    for sec, name, pats in GROUPS:
        if any((v == p or v.endswith("." + p)) if "." in p else (p in v) for p in pats):
            return (sec, name)
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
    # 输出顺序：分区 -> 公司（按首次出现顺序）-> 服务（按 GROUPS 顺序），与匹配顺序无关
    company_rank, keyed = {}, []
    for i, (sec, n, _) in enumerate(GROUPS):
        company_rank.setdefault(n.split(" - ")[0], i)
        keyed.append(((0 if sec == S_INTL else 2, company_rank[n.split(" - ")[0]], i), (sec, n)))
    keyed.append(((1, 0, 0), OTHER))
    order = [g for _, g in sorted(keyed)]
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
                                         "# 排除: ai/exclude.txt（仅大陆站、海内外共用域名，以及通用 CDN / 统计 / 支付域名）"]

    yaml_lines = header + ["payload:"]
    list_lines = list(header)
    cur_sec = None
    for g in order:
        if g not in grouped:
            continue
        sec, name = g
        if sec != cur_sec:
            cur_sec = sec
            yaml_lines.append(f"  # ===== {sec} =====")
            list_lines.append(f"# ===== {sec} =====")
        yaml_lines.append(f"  # {name}")
        list_lines.append(f"# {name}")
        for t, v in grouped[g]:
            yaml_lines.append(f"  - {t},{v}")
            list_lines.append(f"{t},{v}")
    (AI_DIR / "ai.yaml").write_text("\n".join(yaml_lines) + "\n", encoding="utf-8")
    (AI_DIR / "ai.list").write_text("\n".join(list_lines) + "\n", encoding="utf-8")
    print(f"[完成] 写出 {total} 条规则 -> ai/ai.yaml, ai/ai.list", file=sys.stderr)


if __name__ == "__main__":
    main()
