---
name: media-naming-guide
description: >-
  Standardize movie and TV series filenames for Plex, Emby, Jellyfin, and other media servers.
  Chinese name + English name + year + resolution format, with censorship evasion decoding.
  Use when the user mentions 影视整理, 电影命名, 剧集命名, media library organization,
  rename movies, NAS media management, Plex/Emby/Jellyfin naming, or 资源整理.
---

# 影视文件命名规范

适用于任何存储设备（NAS / 本地硬盘 / 网盘）和任何媒体服务器（Plex / Emby / Jellyfin / Kodi）的影视文件命名规范。

## 核心原则

**正向验证，不是反向检测。**

不要试图列举所有"脏模式"（永远会漏）。正确的方法是：
1. 定义"合规格式"
2. 遍历每个文件/目录
3. 不符合合规格式的，全部标记为问题

## 工作流程

### Step 1: 完整扫描

```bash
python scripts/scan.py /path/to/media
```

脚本会递归遍历所有目录，对每个文件/目录进行正向合规验证，按问题类型分组输出。

加 `--json` 输出 JSON 格式：
```bash
python scripts/scan.py --json /path/to/media > /tmp/issues.json
```

### Step 2: 分类修复

按以下**严格顺序**处理：

1. **删除垃圾文件** — torrent / nfo / td / jpg / htm
2. **移错分类** — 多集资源从电影移到剧集
3. **解码审查规避** — 需要人工映射表
4. **修复目录名** — 补英文名/年份、去水印/PT后缀
5. **对齐内部文件名** — 电影文件名=文件夹名；剧集文件名=剧名 SXXEYY.ext
6. **清理字幕文件** — 语言标签标准化

### Step 3: 重新扫描验证

```bash
python scripts/scan.py /path/to/media
```

问题数 = 0 即完成。有新增问题则重复 Step 2-3。

## 命名规范

### 电影文件夹

```
中文名 English Name (年份) [分辨率 来源]/
  中文名 English Name (年份) [分辨率 来源].mkv
  中文名 English Name (年份) [分辨率 来源].chs.srt
```

- 允许中文名中混合数字和英文（`007无暇赴死`、`致命ID`）
- 年份可选（合集无单一年份时省略）
- 分辨率/来源方括号可选
- 多版本/多CD：`… CD1.mp4`、`… [4K].mkv`、`…_2.mp4`
- **禁止合集文件夹**：`钢铁侠 Iron Man 1-3` 这种多部合集必须拆成独立文件夹，每部各自 `中文名 English Name (年份)` 格式
- 花絮/幕后内容放在 `花絮/` 子目录下

### 电影花絮（extras）

```
中文名 English Name (年份) [分辨率 来源]/
  中文名 English Name (年份) [分辨率 来源].mkv       ← 正片
  花絮/                                               ← 花絮子目录
    花絮 - 视觉之旅/
      花絮 - 视觉之旅.mkv
    花絮 - 删减片段/
      花絮 - 删减片段.mkv
```

- PT 场景名的 extras 目录（如 `A.Visual.Journey-Grym@BTNET`）必须清理为中文规范名
- 花絮子目录内文件不参与主文件名校验

### 剧集文件夹

```
中文名 English Name [SXX]/
  中文名 English Name SXX E01.mp4
  中文名 English Name SXX E02 [4K].mkv
```

- 季数格式统一 SXX（`S01`、`S01-S06`）
- 内部文件用 `剧名 E{XX}` 或 `剧名 S{XX} E{XX}` 格式（带剧名前缀）
- 小写 `s01e01` 必须改为大写格式
- 允许标签：`[4K]`、`[国语]`、`[粤语]`、`END`

### 剧集特殊内容（彩蛋/花絮/MV）

```
中文名 English Name SXX/
  中文名 English Name SXX SP01 彩蛋.mp4
  中文名 English Name SXX SP02 花絮.mp4
  中文名 English Name SXX SP01 MV.mp4
```

- 彩蛋、花絮、MV 等用 `SP{XX}` 编号
- 格式：`剧名 SP{XX} 类型.ext`
- 不允许纯 `彩蛋1.mp4`、`花絮2.mp4` 这种不带剧名的简称

### 分辨率标签

`4K` `1080p` `720p` `480p` | `BluRay` `WEB-DL` `WEBRip` `HDRip` `BDRip` `Remux` `DVDRip` `HDTV`

## 正向合规验证逻辑

```python
import re

MOVIE_DIR_OK = re.compile(
    r'^[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\d·A-Za-z]+'  # 中文名（含标点、数字）
    r'\s+'
    r'[\w][\w\s\':,.\-&!()0-9]+'                              # 英文名
    r'(\s*\(\d{4}\))?'                                         # (年份) 可选
    r'(\s*\[.*\])?'                                            # [分辨率 来源] 可选
    r'$'
)

SERIES_DIR_OK = re.compile(
    r'^[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\d·A-Za-z]+'
    r'\s+'
    r'[\w][\w\s\':,.\-&!()0-9]+'
    r'(\s*S\d{2}(-S\d{2})?)?'                                 # 季号
    r'(\s*\(\d{4}\))?'
    r'$'
)

SERIES_FILE_OK = re.compile(
    r'^'
    r'([\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\d·A-Za-z]+\s+[\w][\w\s\':,.\-&!()0-9]+\s+)?'
    r'(E\d{2,3}|S\d{2}\s*E\d{2,3}|E\d{2,3}-E\d{2,3}|S\d{2}\s*E\d{2,3}-E\d{2,3})'
    r'(\s*(END|V\d))?'
    r'(\s*\[[\w.\s]+\])?'
    r'\s*\.(mp4|mkv|avi|ts|rmvb|flv|wmv|mov)$',
    re.I
)
```

## 审查规避解码

中文互联网资源为规避审查，会对文件名做各种变形。**无法用正则自动还原，必须人工维护映射表。**

| 变形模式 | 示例 | 还原 | 解码要点 |
|----------|------|------|----------|
| 单字母前缀 | `S探` `W杀` `F联4` | 神探、误杀、复仇者联盟4 | 首字母通常是缺失汉字的拼音声母 |
| `丨`/`｜` 断词 | `让丨Z弹飞` `蜘丨ZX` | 让子弹飞、蜘蛛侠 | `丨` (U+4E28) 是汉字部件，不是竖线 |
| 方括号包裹 | `[源DM][2011]` `[冰Hx落]` | 源代码、冰海陷落 | 方括号内字母替代对应位置的汉字 |
| 首字母缩写 | `FS.风骚LS` `PF.平凡Z路` | 风骚律师、平凡之路 | 前缀是剧名拼音缩写 |
| 多字母替代 | `人MG仆` `变X金G` | 人民公仆、变形金刚 | 连续大写字母替代连续汉字 |
| 故意丢字 | `云之上` `F界线` | 乌云之上、分界线 | 删掉敏感字后剩余部分仍可读 |
| 拼音混写 | `F-罚zui` `X失de她` | 罚罪、消失的她 | 部分汉字用拼音替代 |

### 解码铁则

1. **解码后必须搜索验证**。`F界线` 可能是「界线」（丢弃前缀）也可能是「**分**界线」（F=分 fen）。只有搜索确认才能判断。
2. **不能凭直觉脑补**。`人MG仆` 不是「人形仆人」——MG=民公，实为「人民公仆」。必须用集数、演员等线索交叉验证。
3. **数字也可能是替代**。`J号秘事` 中 J=9（jiu），实为「9号秘事」。
4. **同一部剧可能有多种变体**。同一资源可能同时出现 `F-罚zui`（拼音混写）和 `FZ.罚罪2`（首字母缩写）两种命名。

### 首字母陷阱

单字母前缀（如 `F`、`S`、`K`）可能是：
1. **无意义前缀**（直接丢弃）：`S-三体` → 三体、`H-黑鸟` → 黑鸟
2. **缺失汉字的首字母**（必须还原）：`F界线` → **分**界线（F=分）、`S尘暴` → **沙**尘暴（S=沙）

**判断方法**：解码后的中文名是否是一个"说得通"的词——
- 「界线」不是常见剧名 → 搜索确认 → 应为「分界线」
- 「尘暴」不是标准用词 → 搜索确认 → 应为「沙尘暴」
- 「三体」已是完整剧名 → 正确

**铁则：解码后必须用搜索引擎验证，确认中文名是真实存在的影视作品。不确定时宁可标记待人工确认，不要擅自决定。**

## 判断电影 vs 剧集

如果一个目录内有 **5 个以上的视频文件**，大概率是电视剧，应移到剧集目录。

```python
from pathlib import Path

VIDEO_EXTS = {'.mp4', '.mkv', '.avi', '.ts', '.rmvb', '.flv', '.wmv', '.mov', '.iso', '.m2ts'}

def count_videos(folder: Path) -> int:
    return sum(1 for f in folder.iterdir() if f.is_file() and f.suffix.lower() in VIDEO_EXTS)

folder = Path('/path/to/movie/folder')
if count_videos(folder) >= 5:
    print(f'WARNING: {folder.name} 可能是剧集 ({count_videos(folder)} 个视频)')
```

### 分段电影误判为剧集

有些电影被拆成多段（CD1/CD2、Part1/Part2、上下集），因为有多个视频文件而被误判为剧集。

**识别分段电影的特征**：
1. 文件名含 `CD1`/`CD2`、`Part1`/`Part2`、`Disc1`/`Disc2`、`上`/`下` 等分段标记
2. 文件名**不含** `E01`/`S01E01` 等剧集编号
3. 文件夹名像电影（有年份，无季号）
4. 搜索确认是电影而非迷你剧

```python
import re

SEGMENT_PATTERN = re.compile(
    r'(CD\d|Part\s*\d|Disc\s*\d|[上下]集|[上下]部|_[12]\.)',
    re.I
)

def is_segmented_movie(folder_name: str, filenames: list[str]) -> bool:
    has_segments = any(SEGMENT_PATTERN.search(f) for f in filenames)
    has_episodes = any(re.search(r'[ES]\d{2}', f, re.I) for f in filenames)
    has_season = bool(re.search(r'S\d{2}', folder_name, re.I))
    return has_segments and not has_episodes and not has_season
```

**命名规范**（分段电影留在电影目录）：
```
中文名 English Name (年份)/
  中文名 English Name (年份) CD1.mkv
  中文名 English Name (年份) CD2.mkv
```

**注意**：不要把分段电影合并成一个文件，保持原始分段，仅规范文件名。

## 拆分合集文件夹

多部电影合集（如 `钢铁侠 Iron Man 1-3`、`指环王 1-3`）必须拆成独立文件夹。

原因：合集文件夹内部命名无法统一（每部有不同年份、不同分辨率），导致文件名不规范。

```python
import re

def is_collection(folder_name: str) -> bool:
    return bool(re.search(r'\d+-\d+$', folder_name))
```

### 拆分步骤

```python
from pathlib import Path
import shutil

base = Path('/path/to/movies')
old_dir = base / '钢铁侠 Iron Man 1-3'

# 1. 为每部创建独立文件夹
(base / '钢铁侠 Iron Man (2008)').mkdir(exist_ok=True)
(base / '钢铁侠2 Iron Man 2 (2010)').mkdir(exist_ok=True)
(base / '钢铁侠3 Iron Man 3 (2013)').mkdir(exist_ok=True)

# 2. 改名 + 移动各文件到对应文件夹
# 3. 如果某部已有独立高画质版本，删除合集中的低画质副本
# 4. 删除空的合集文件夹
```

### 注意事项
- 拆分前检查是否已有独立文件夹（避免重复）
- 有独立高画质版本时，合集中的低画质副本直接删除
- 拆分后每部必须加上年份

## 补英文名的铁则

补英文名是高频出错环节，必须遵守：

1. **必须搜索官方来源**：维基百科、豆瓣、TMDB、MyDramaList。不能凭记忆猜、不能用直译名
2. **注意同名异作**：`Heroic Legend` 对应多部剧（萍踪侠影/大清风云），必须用中文名交叉确认
3. **注意改名/旧名**：部分剧播出前改过英文名（如「低智商犯罪」从 Low IQ Crime 改为 Born with Luck）
4. **解码后也要验证**：审查规避解码后的中文名也可能不对，中文名不确定时先搜索

### 验证流程

1. 搜索 `{中文名} 电视剧/电影 英文名`
2. 确认搜索结果中的中文名与资源中文名完全匹配
3. 确认英文名来自官方来源（不是直译/机翻）
4. 如果同名有多部作品，用年份/演员/集数交叉确认

| 陷阱 | 示例 | 正确做法 |
|------|------|----------|
| 同名异作 | `AI Amok`（日本 vs 中国《黑金风暴》） | 用中文名交叉搜索，确认对应关系 |
| 直译名 ≠ 官方名 | `Low IQ Crime` vs `Born with Luck` | 以豆瓣/TMDB/维基为准 |
| 旧名 ≠ 现名 | 播出前改名 | 搜索确认当前官方英文名 |
| 关联错误 | `Heroic Legend` 对应多部剧 | 必须用年份+演员确认唯一性 |

## 文件名 ≠ 内容

**文件名可能与实际视频内容完全无关。** 当文件名在任何影视数据库都查不到时：

1. 不要凭文件名推测内容
2. 通过视频元数据（duration、resolution）排除明显不匹配
3. 通过播放器/缩略图确认实际内容
4. 无法确认的标记为「待确认」，不要擅自重命名

## 常见脏数据类型与处理策略

整理影视库时，常见以下几类不规范命名。按出现频率排列：

### 1. 审查规避命名

见上方「审查规避解码」章节。

### 2. PT/场景组命名

PT（Private Tracker）下载的资源保留原始场景命名，纯英文+编码参数：

```
The.Imitation.Game.2014.DVDSCR.x264-GoPanda
Fury.2014.R6.1080p.WEB-DL.x264.AAC-SeeHD
Brokeback.Mountain.2005.720p.BluRay.DTS.x264-HDS
```

处理方式：从场景名中提取英文标题 + 年份 + 分辨率，搜索对应中文名后重命名。

### 3. 资源站水印命名

国内资源站（Mp4Ba、圣城家园等）在文件名中添加水印标记：

```
煎饼侠.Jian.Bing.Man.2015.HD1080P.X264.AAC.Mandarin.CHS-ENG.Mp4Ba
辛德勒的名单[微信公众号 西西追剧]
杀死比尔ⅠⅡ合集.中英字幕￡圣城九洲客
```

处理方式：去除水印后缀 / 微信公众号标记 / 圣城标记，保留有效信息重组为标准格式。

### 4. 格式不统一

同一库中混合存在多种命名风格：

| 问题 | 示例 | 规范化 |
|------|------|--------|
| 英文名用点号分隔 | `功夫熊猫.720P.中英字幕` | `功夫熊猫 Kung Fu Panda (2008) [720p]` |
| 缺英文名 | `好东西 (2024)` | `好东西 Her Story (2024)` |
| 缺年份 | `刺杀金正恩.The.Interview` | `刺杀金正恩 The Interview (2014)` |
| 合集未拆分 | `钢铁侠 Iron Man 1-3/` | 拆为 3 个独立文件夹，各带年份 |

### 5. 分类错误

电影和剧集混放是常见问题：

| 场景 | 判断依据 | 处理 |
|------|----------|------|
| 多集剧集放在电影目录 | 目录内 ≥5 个视频文件 + 含 E01 编号 | 移到剧集目录 |
| 分段电影误判为剧集 | 文件含 CD1/Part1/上下，无 E01 编号 | 保留在电影目录 |
| 单文件剧集在电影目录 | 无分集编号、审查规避名 | 需搜索确认后决定 |

## 整理操作清单

执行整理时按以下顺序逐步推进：

```
1. 完整扫描（正向验证，输出所有不合规项）
2. 删除垃圾文件（torrent / nfo / td / jpg / htm）
3. 修复分类错误（电影↔剧集互移）
4. 解码审查规避名（人工映射 + 搜索验证）
5. 清理 PT/水印目录名（提取有效信息重组）
6. 补全英文名/年份/分辨率
7. 拆分合集文件夹
8. 对齐内部文件名（电影=文件夹名；剧集=剧名 SXXEYY）
9. 重新扫描验证 → 问题数=0 即完成
```

每一步都应该先生成 `old → new` 映射表预览，确认后再批量执行。

## 踩坑记录

| 坑 | 表现 | 解决 |
|----|------|------|
| 反向检测 | 永远有漏网之鱼 | **改用正向验证** |
| 审查规避 | 无通用正则能覆盖 | 人工映射表 + 黑名单字符 |
| 字幕没改 | 视频改了字幕没跟 | 字幕与文件夹同名+语言标签 |
| rename 冲突 | 同名文件已存在 | 加 `_2` 后缀或标 `[副本]` |
| 电影误分类 | 多集资源放在电影目录 | 检查视频文件数，≥5 移到剧集 |
| 合集文件夹 | 内部命名无法统一 | **拆成独立文件夹**，每部各带年份 |
| 小写集号 | `s02e10.mp4` 格式不统一 | 重命名为 `剧名 E10.mp4`（大写集号） |
| 彩蛋/花絮命名 | `彩蛋1.mp4` 不带剧名 | 改为 `剧名 SP01 彩蛋.mp4` |
| PT花絮目录 | `A.Visual.Journey-Grym@BTNET` | 重命名为 `花絮 - 视觉之旅` |
| 两部电影合拍 | 同目录 | 拆为独立电影文件夹 |
| 审查规避丢字 | `F界线`→界线 | 首字母是缺失汉字：**分**界线。解码后必须搜索验证 |
| 审查规避脑补 | `人MG仆`→人形仆人 | 多字母替代多汉字，不能脑补。正确为「人民公仆」 |
| 英文名张冠李戴 | `黑金风暴 AI Amok` | 补英文名必须搜索官方来源 |
| 英文名过期 | `Low IQ Crime` | 旧名/直译名不等于官方名 |
| 分段电影误判 | CD1/CD2 被当成剧集 | 检查文件名是否含 CD/Part/上下 |
| 中文名被篡改 | 文件名与实际内容无关 | 必须确认实际内容后再命名 |
