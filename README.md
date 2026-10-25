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

## apple-ai：Apple 智能（Apple Intelligence）

让 Apple 智能（含 ChatGPT 扩展、私有云计算）在大陆网络下可用所需的最少域名，共 6 条，手工维护（不参与每周自动生成）。

### 规则地址

| 格式 | 地址 |
| --- | --- |
| YAML（`format: yaml`） | https://raw.githubusercontent.com/resucdueff/proxylist/main/apple-ai/apple-ai.yaml |
| 纯文本（`format: text`） | https://raw.githubusercontent.com/resucdueff/proxylist/main/apple-ai/apple-ai.list |

| 规则 | 作用 |
| --- | --- |
| `DOMAIN,gspe1-ssl.ls.apple.com` | 按出口 IP 判断地区，ChatGPT 扩展依赖；走代理后地图等也会变成海外版 |
| `DOMAIN,apple-relay.apple.com` | ChatGPT 扩展中继 |
| `DOMAIN,apple-relay.cloudflare.com` | 私有云计算中继 |
| `DOMAIN,apple-relay.fastly-edge.com` | 私有云计算中继 |
| `DOMAIN,cp4.cloudflare.com` | 私有云计算 |
| `DOMAIN,apple-relay.mask.apple-dns.net` | 中继入口 |

### 使用前提

- **国行设备（型号含 CH/A）无论怎么配置都用不了**，与代理无关。
- 使用非中国大陆地区的 Apple ID，设备语言与 Siri 语言一致且为 Apple 智能支持的语言。
- 代理节点必须在 ChatGPT 支持的地区（**不能用香港**，推荐美国 / 日本 / 新加坡），并且支持 **UDP**（私有云计算中继走 QUIC）。
- mihomo 需开启 **TUN** 和 **sniffer（域名嗅探）**，否则设备直接按 IP 连接时匹配不到域名规则。
- 可选：Siri 走代理可手动加 `DOMAIN,guzzoni.apple.com`（未放进规则文件，按需自行添加）。

### mihomo 配置示例

注意规则顺序：`apple-ai` 必须在 Apple 直连规则和 `GEOIP,CN` **之前**。

```yaml
tun:
  enable: true
  stack: mixed
  auto-route: true
  auto-detect-interface: true

sniffer:
  enable: true
  sniff:
    HTTP: {ports: [80, 8080-8880], override-destination: true}
    TLS: {ports: [443, 8443]}
    QUIC: {ports: [443, 8443]}

rule-providers:
  apple-ai:
    type: http
    behavior: classical
    format: yaml
    url: https://raw.githubusercontent.com/resucdueff/proxylist/main/apple-ai/apple-ai.yaml
    path: ./ruleset/apple-ai.yaml
    interval: 86400
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
    proxies: [美国节点, 日本节点, 新加坡节点]   # 换成你自己的节点，不要选香港

rules:
  - RULE-SET,apple-ai,AI
  - RULE-SET,ai,AI
  # 其余 Apple 服务直连
  - DOMAIN-SUFFIX,push.apple.com,DIRECT
  - DOMAIN-SUFFIX,icloud.com,DIRECT
  - DOMAIN-SUFFIX,icloud-content.com,DIRECT
  - DOMAIN-SUFFIX,apple-cloudkit.com,DIRECT
  - DOMAIN-SUFFIX,mzstatic.com,DIRECT
  - DOMAIN-SUFFIX,cdn-apple.com,DIRECT
  - DOMAIN-SUFFIX,ls.apple.com,DIRECT
  - DOMAIN-SUFFIX,apple.com,DIRECT
  - DOMAIN-SUFFIX,apple.com.cn,DIRECT
  - IP-CIDR,17.0.0.0/8,DIRECT,no-resolve
  - GEOIP,CN,DIRECT
  # ... 其他规则
  - MATCH,DIRECT
```

### 来源

- Apple 支持文档 [101555](https://support.apple.com/zh-cn/101555)（在企业网络中使用 Apple 产品）
- [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community) `apple-intelligence`（MetaCubeX geosite `apple-intelligence`）
- [SukkaW/Surge](https://github.com/SukkaW/Surge) `apple_intelligence`

## github / linux / docker：开发常用境外源

三个规则集收录在国内直连打不开或速度很差的开发相关域名，手工维护，由 `scripts/build_dev.py` 生成（不参与每周自动更新）。文件内同样按「分区 → 公司 - 服务」两级注释分组。

| 规则集 | 条数 | 内容 |
| --- | --- | --- |
| `github` | 50 | github.com、githubusercontent.com（raw / Release / 头像）、githubassets.com、github.io、github.dev、ghcr.io、ghe.com、Release / LFS 的 S3 存储、Actions 日志 Blob、状态页 / 博客等 |
| `linux` | 40 | **Alpine 官方源**（alpinelinux.org，含 dl-cdn）、Debian、Ubuntu / Launchpad PPA / Snap、Kali、Mint、树莓派、Armbian、Proxmox、Fedora / EPEL / Copr、RHEL CDN、CentOS、Rocky、Alma、Oracle Linux、Arch / AUR / ArchARM、Manjaro、openSUSE、Gentoo、NixOS / Cachix、Void、kernel.org、Flathub |
| `docker` | 20 | Docker Hub（docker.io、docker.com、镜像层 CDN / R2）、registry.k8s.io / k8s.io、gcr.io、pkg.dev、Helm、ghcr.io、Quay、Red Hat Registry、ECR Public、NVIDIA NGC、Elastic、GitLab Registry |

说明：

- 只收录境外官方源，清华 TUNA、中科大 USTC、阿里云等国内镜像站继续直连。
- Copilot 相关域名在 `ai` 规则集里，`github` 不重复收录；想让 Copilot 走 AI 分组，把 `RULE-SET,ai` 放在 `RULE-SET,github` 前面。
- `ghcr.io` 在 `github` 和 `docker` 里都有，方便单独使用。
- Fedora / CentOS / Rocky / Alma / openSUSE / Arch 的 mirrorlist 会按出口 IP 分配镜像，走代理后可能分到海外第三方镜像，这类发行版更推荐直接换国内镜像源。

### 规则地址

| 规则集 | YAML（`format: yaml`） | 纯文本（`format: text`） |
| --- | --- | --- |
| github | https://raw.githubusercontent.com/resucdueff/proxylist/main/github/github.yaml | https://raw.githubusercontent.com/resucdueff/proxylist/main/github/github.list |
| linux | https://raw.githubusercontent.com/resucdueff/proxylist/main/linux/linux.yaml | https://raw.githubusercontent.com/resucdueff/proxylist/main/linux/linux.list |
| docker | https://raw.githubusercontent.com/resucdueff/proxylist/main/docker/docker.yaml | https://raw.githubusercontent.com/resucdueff/proxylist/main/docker/docker.list |

### mihomo 配置示例

```yaml
rule-providers:
  github:
    type: http
    behavior: classical
    format: yaml
    url: https://raw.githubusercontent.com/resucdueff/proxylist/main/github/github.yaml
    path: ./ruleset/github.yaml
    interval: 86400
  linux:
    type: http
    behavior: classical
    format: yaml
    url: https://raw.githubusercontent.com/resucdueff/proxylist/main/linux/linux.yaml
    path: ./ruleset/linux.yaml
    interval: 86400
  docker:
    type: http
    behavior: classical
    format: yaml
    url: https://raw.githubusercontent.com/resucdueff/proxylist/main/docker/docker.yaml
    path: ./ruleset/docker.yaml
    interval: 86400

rules:
  - RULE-SET,ai,AI           # 如果也用了 ai 规则集，放在最前
  - RULE-SET,github,代理
  - RULE-SET,linux,代理
  - RULE-SET,docker,代理
  # ... GEOSITE / GEOIP,CN,DIRECT 等
  - MATCH,DIRECT
```

> 提示：规则集本身托管在 raw.githubusercontent.com，首次下载如果失败，可以给 rule-provider 加 `proxy: 代理`。

### 重新生成

```bash
python3 scripts/build_dev.py   # 改 RULESETS 里的域名后运行
git diff github/ linux/ docker/
```
