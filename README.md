# media-naming-guide

**Chinese media library naming conventions for Plex, Emby, Jellyfin, and other media servers.**

中文影视库命名规范 + [Cursor AI Skill](https://docs.cursor.com/features/skills)，适用于任何存储设备和媒体服务器。

[中文](#功能) | [English](#features)

---

## Features

This guide standardizes Chinese media filenames with a format that works across all major media servers:

```
电影: 中文名 English Name (年份) [分辨率 来源]/
剧集: 中文名 English Name SXX/
```

**What's inside:**

- Naming conventions for movies, TV series, extras, and multi-part films
- Positive validation regex — scan your library and find all non-conforming names
- Chinese censorship evasion decoding guide — decode names like `S探`, `让丨Z弹飞`, `人MG仆`
- English name verification best practices — avoid common pitfalls
- A ready-to-use scanner script (`scripts/scan.py`)

### Quick Examples

| Before | After |
|--------|-------|
| `The.Imitation.Game.2014.DVDSCR.x264-GoPanda` | `模仿游戏 The Imitation Game (2014)` |
| `煎饼侠.Jian.Bing.Man.2015.HD1080P.Mp4Ba` | `煎饼侠 Jian Bing Man (2015) [1080p]` |
| `S探 S01` | `神探 Detective S01` |
| `让丨Z弹飞` | `让子弹飞 Let the Bullets Fly (2010)` |

## Use as Cursor Skill

Add this repo as a Cursor Skill to let AI agents organize your media library:

```bash
# Clone to your Cursor skills directory
git clone https://github.com/skyzhao1223/media-naming-guide.git \
  ~/.cursor/skills/media-naming-guide
```

Then mention any of the following in Cursor chat to activate the skill:
`影视整理` `电影命名` `剧集命名` `media library` `Plex naming` `资源整理`

## Scan Your Library

```bash
python scripts/scan.py /path/to/media
```

The scanner recursively validates every file and directory against the naming conventions. It groups issues by type and reports all non-conforming items.

```bash
# Output as JSON for scripting
python scripts/scan.py /path/to/media --json > issues.json
```

Your media directory should contain `电影/` and/or `剧集/` subdirectories.

---

## 功能

标准化中文影视文件命名，兼容所有主流媒体服务器的刮削规则：

```
电影: 中文名 English Name (年份) [分辨率 来源]/
剧集: 中文名 English Name SXX/
```

**包含内容：**

- 电影、剧集、花絮、分段电影的命名规范
- 正向验证正则 — 扫描整个库，找出所有不合规命名
- 审查规避命名解码指南 — 解码 `S探`、`让丨Z弹飞`、`人MG仆` 等变形名
- 补英文名最佳实践 — 避免常见陷阱（同名异作、直译名、旧名）
- 可直接使用的扫描脚本 (`scripts/scan.py`)

详细规范见 [SKILL.md](SKILL.md)。

### 作为 Cursor Skill 使用

```bash
git clone https://github.com/skyzhao1223/media-naming-guide.git \
  ~/.cursor/skills/media-naming-guide
```

在 Cursor 对话中提及 `影视整理`、`电影命名`、`剧集命名` 等关键词即可激活。

### 扫描影视库

```bash
python scripts/scan.py /path/to/media
```

扫描器递归验证每个文件/目录是否符合命名规范，按问题类型分组输出。媒体目录下应包含 `电影/` 和/或 `剧集/` 子目录。

## License

[MIT](LICENSE)
