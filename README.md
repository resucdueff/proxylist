# proxylist

自用代理分流规则集，适用于 Clash Meta（mihomo）。

## ai：境外 AI 服务

收录中国大陆以外、在大陆通常需要代理才能访问的 AI 服务域名：OpenAI / ChatGPT / Sora、Anthropic / Claude、Google Gemini / AI Studio / NotebookLM / Labs / DeepMind、xAI / Grok、Microsoft Copilot、GitHub Copilot、Meta AI、Perplexity、Mistral、Cohere、Hugging Face、Poe、Character.AI、Midjourney、Stability、Runway、Pika、Luma、Ideogram、Leonardo、ElevenLabs、Suno、Udio、Cursor、Windsurf、Replicate、Together、Groq、Fireworks、OpenRouter、DeepL、Jasper 等。

- 包含中国 AI 公司的**海外站**（如 Kimi 国际版 kimi.ai、Kling 国际版、海螺海外版、Qwen 国际版 chat.qwen.ai、Z.ai、Dreamina、BytePlus ModelArk、Manus、Genspark、Vidu、PixVerse 等），单独分在「中国公司海外 AI」区。
- 不含仅大陆站或海内外共用的域名（如 deepseek.com、kimi.com、豆包、通义、智谱 bigmodel.cn、文心等），它们应直连。
- 不含 google.com、googleapis.com、microsoft.com、cloudflare.com 之类被大量普通网站共用的整域名，只收录 AI 专用的子域名（如 `gemini.google.com`、`generativelanguage.googleapis.com`、`copilot.microsoft.com`）。
- 只使用 `DOMAIN-SUFFIX` / `DOMAIN` / `DOMAIN-KEYWORD`（关键字仅 `openai`、`anthropic`），不含 IP 规则。
- 当前规则数：264，每周自动更新。
- 文件内按「分区 → 公司 - 服务」两级注释分组（如 `# OpenAI - ChatGPT`、`# Google - Gemini`、`# Moonshot - Kimi intl`）。

### 规则地址

| 格式 | 地址 |
| --- | --- |
| YAML（`format: yaml`） | https://raw.githubusercontent.com/resucdueff/proxylist/main/ai/ai.yaml |
| 纯文本（`format: text`） | https://raw.githubusercontent.com/resucdueff/proxylist/main/ai/ai.list |

### mihomo 配置示例

```yaml
rule-providers:
  ai:
    type: http
    behavior: classical
    format: yaml
    url: https://raw.githubusercontent.com/resucdueff/proxylist/main/ai/ai.yaml
    path: ./ruleset/ai.yaml
    interval: 86400

proxy-groups:
  - name: AI
    type: select
    proxies: [美国节点, 日本节点, 新加坡节点]   # 换成你自己的节点或分组

rules:
  - RULE-SET,ai,AI
  # ... 其他规则
  - MATCH,DIRECT
```

使用纯文本格式时，把 `format` 改成 `text`，`url` 换成 `ai.list` 的地址即可。

> 提示：`RULE-SET,ai,AI` 要放在 GEOIP / GEOSITE 等国内直连规则之前，否则部分域名（如 Google 的 AI 子域名）可能先被其他规则匹配。

### 数据来源

由 `scripts/build_ai.py` 自动合并生成：

- [MetaCubeX/meta-rules-dat](https://github.com/MetaCubeX/meta-rules-dat) geosite `category-ai-!cn`（基于 [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community)）
- [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script) OpenAI / Claude / Gemini / Copilot
- [ACL4SSR](https://github.com/ACL4SSR/ACL4SSR) `Clash/Ruleset/AI.list`
- `ai/extra.txt`：手工补充（参考各服务官方文档）
- `ai/exclude.txt`：排除列表（国内 AI 服务、通用 CDN / 统计 / 支付等非 AI 专用域名）

### 重新生成

```bash
python3 scripts/build_ai.py   # 仅依赖 Python 3.9+ 标准库
git diff ai/                  # 检查变化后提交
```

想加域名改 `ai/extra.txt`，想去掉某条改 `ai/exclude.txt`，然后重新运行脚本。
