#!/usr/bin/env python3
"""扫描本地影视目录 — 正向验证版。

核心思路：不是检测"脏模式"，而是验证每个文件/目录是否符合规范。
任何不匹配规范格式的，全部输出。

Usage:
    python scan.py /path/to/media
    python scan.py /path/to/media --json
"""

import re
import sys
import json
from pathlib import Path

VIDEO_EXTS = {'.mp4', '.mkv', '.avi', '.ts', '.rmvb', '.flv', '.wmv', '.mov', '.iso', '.m2ts'}
SUB_EXTS = {'.srt', '.ass', '.ssa', '.sub', '.idx'}
JUNK_EXTS = {'.torrent', '.nfo', '.td', '.htm', '.html', '.url', '.txt', '.jpg', '.png', '.nzb'}

# ── 合规格式定义 ──────────────────────────────────────────

MOVIE_DIR_OK = re.compile(
    r'^[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\d·A-Za-z]+'
    r'\s+'
    r'[\w][\w\s\':,.\-&!()0-9]+'
    r'(\s*\(\d{4}\))?'
    r'(\s*\[.*\])?'
    r'(\s*(1-\d|\d-\d|CD\d|导演剪辑版|\[副本\d?\]))?'
    r'$'
)

SERIES_DIR_OK = re.compile(
    r'^[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\d·A-Za-z]+'
    r'\s+'
    r'[\w][\w\s\':,.\-&!()0-9]+'
    r'(\s*S\d{2}(-S\d{2})?)?'
    r'(\s*\(\d{4}\))?'
    r'(\s*(特别篇|\d))?'
    r'$'
)

SERIES_FILE_OK = re.compile(
    r'^'
    r'([\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\d·A-Za-z]+\s+[\w][\w\s\':,.\-&!()0-9]+\s+)?'
    r'('
    r'E\d{2,3}'
    r'|S\d{2}\s*E\d{2,3}'
    r'|E\d{2,3}-E\d{2,3}'
    r'|S\d{2}\s*E\d{2,3}-E\d{2,3}'
    r')'
    r'(\s*(END|V\d))?'
    r'(\s*\[[\w.\s]+\])?'
    r'\s*\.'
    r'(mp4|mkv|avi|ts|rmvb|flv|wmv|mov)$',
    re.I
)

SERIES_SPECIAL_OK = re.compile(
    r'^'
    r'([\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\d·A-Za-z]+\s+[\w][\w\s\':,.\-&!()0-9]+\s+)?'
    r'(SP\d{2}(\s+[\u4e00-\u9fffA-Za-z]+)?'
    r'|花絮|特辑|彩蛋|预告|番外|幕后|特别篇|精华版|前传'
    r'|[\u4e00-\u9fff][\u4e00-\u9fff\w\s]*)'
    r'\.(mp4|mkv|avi|ts)$'
)

# ── 通用黑名单 ────────────────────────────────────────────

BLACKLIST_CHARS = re.compile(r'[丨｜]')

LETTER_SUB = re.compile(
    r'(?:^[A-Z]{1,2}[\u4e00-\u9fff])'
    r'|(?:[\u4e00-\u9fff][A-Z]{1,3}[\u4e00-\u9fff])'
    r'|(?:[\u4e00-\u9fff][A-Z]{1,3}$)'
)

WATERMARK = re.compile(
    r'【|】|\[微信|\[公众号|￡|@圣城|Mp4Ba|XZYS|XunLeiJia|'
    r'kkkanba|字幕侠|霸王龙|压制组|微信|爱影哥|瞎看菌|雷锋菌|影喵儿|'
    r'情话菌|影视步行街|RARBG|STUTTERSHIT|SmY|CHAOSPACE',
    re.I
)

PLACEHOLDER_ENGLISH = re.compile(
    r'\s+Erta\s*$|\s+TBD\s*$|\s+Unknown\s*$|\s+XXX\s*$',
    re.I
)


def movie_file_ok(filename: str, folder_name: str) -> bool:
    stem = Path(filename).stem
    suffix = Path(filename).suffix.lower()
    if stem == folder_name:
        return True
    if stem.startswith(folder_name):
        rest = stem[len(folder_name):]
        if re.match(r'^(\s*(CD\d|_\d|\[\w+\]|E\d{2,3}|\[粤语\]|\[国语\]|\[v\d\]|前传\d?))*$', rest):
            return True
    if re.search(r'\d+-\d+$', folder_name):
        return True
    if suffix in SUB_EXTS and stem.startswith(folder_name):
        return True
    return False


# ── 递归遍历 ──────────────────────────────────────────────

def scan_all(root: Path, depth: int = 0, max_depth: int = 8):
    if depth > max_depth or not root.is_dir():
        return
    try:
        entries = sorted(root.iterdir(), key=lambda p: p.name)
    except PermissionError:
        return
    for entry in entries:
        yield {
            'path': str(entry),
            'name': entry.name,
            'is_dir': entry.is_dir(),
            'depth': depth,
        }
        if entry.is_dir():
            yield from scan_all(entry, depth + 1, max_depth)


# ── 验证逻辑 ─────────────────────────────────────────────

def validate(item: dict, root: str) -> list[str]:
    path = item['path']
    name = item['name']
    is_dir = item['is_dir']
    problems = []

    rel = path.replace(root + '/', '') if path.startswith(root) else path
    parts = rel.split('/')
    ext = Path(name).suffix.lower() if not is_dir else ''
    stem = Path(name).stem if ext else name

    in_movie = '电影' in parts
    in_series = '剧集' in parts

    if not in_movie and not in_series:
        return []

    # ── 通用黑名单 ──
    if BLACKLIST_CHARS.search(name):
        problems.append('审查规避字符(丨｜)')

    if WATERMARK.search(name):
        problems.append('水印/站点标签')

    clean_stem = re.sub(r'\[.*?\]|\(.*?\)', '', stem)
    if LETTER_SUB.search(clean_stem):
        if not re.match(r'^[ES]\d', name):
            if not re.match(r'^(CD|4K|3D|2D|TV|HD|MP|ID)\d*', clean_stem):
                if not re.search(r'[a-z][A-Z]', clean_stem):
                    problems.append('疑似字母替代汉字')

    if is_dir and PLACEHOLDER_ENGLISH.search(name):
        problems.append('占位符英文名(需查找正确英文名)')

    # ── 垃圾文件 ──
    if not is_dir and ext in JUNK_EXTS:
        problems.append('垃圾文件')
        return problems

    if not is_dir and name.endswith('.bt.td'):
        problems.append('下载残留')
        return problems

    # ── 电影区域 ──
    if in_movie:
        movie_idx = parts.index('电影')
        depth_in_movie = len(parts) - movie_idx - 1

        if is_dir and depth_in_movie == 1:
            if not MOVIE_DIR_OK.match(name):
                problems.append('电影文件夹名不合规')
            if re.search(r'\d+-\d+$', name):
                problems.append('合集文件夹(应拆分为独立文件夹)')

        if is_dir and re.match(r'^花絮(\s*-\s*.+)?$', name):
            return []

        if not is_dir and ext in VIDEO_EXTS:
            if any(re.match(r'^花絮', p) for p in parts[movie_idx + 1:]):
                return []
            if depth_in_movie >= 2:
                folder = parts[movie_idx + 1]
                if not movie_file_ok(name, folder):
                    problems.append('电影视频文件名不匹配文件夹')

        if not is_dir and ext in SUB_EXTS:
            if any(re.match(r'^花絮', p) for p in parts[movie_idx + 1:]):
                return []

        if not is_dir and depth_in_movie == 1 and ext in VIDEO_EXTS:
            problems.append('电影散文件(应放入独立文件夹)')

    # ── 剧集区域 ──
    if in_series:
        series_idx = parts.index('剧集')
        depth_in_series = len(parts) - series_idx - 1

        if is_dir and depth_in_series == 1:
            if not SERIES_DIR_OK.match(name):
                problems.append('剧集文件夹名不合规')

        if not is_dir and ext in VIDEO_EXTS:
            if depth_in_series >= 2:
                if not SERIES_FILE_OK.match(name) and not SERIES_SPECIAL_OK.match(name):
                    problems.append('剧集视频文件名不合规')

    # ── PT/Scene 原始命名 ──
    if not is_dir and ext in (VIDEO_EXTS | SUB_EXTS):
        if re.match(r'^[A-Za-z][\w.]+\.\d{4}\.', name):
            problems.append('PT/Scene原始命名')

    # ── 格式转换残留 ──
    if re.search(r'\.qsv\.|\.flv\.mp4$', name):
        problems.append('格式转换残留')

    return problems


# ── 主程序 ────────────────────────────────────────────────

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = [a for a in sys.argv[1:] if a.startswith('--')]

    if not args:
        print('Usage: python scan.py /path/to/media [--json]', file=sys.stderr)
        print('  目录下应包含 电影/ 和/或 剧集/ 子目录', file=sys.stderr)
        sys.exit(1)

    root = Path(args[0]).resolve()
    output_json = '--json' in flags

    if not root.is_dir():
        print(f'Error: {root} is not a directory', file=sys.stderr)
        sys.exit(1)

    root_str = str(root)
    print(f'正在扫描 {root_str} ...\n', file=sys.stderr)

    stats = {'dirs': 0, 'files': 0}
    issues = []

    for item in scan_all(root):
        if item['is_dir']:
            stats['dirs'] += 1
        else:
            stats['files'] += 1

        problems = validate(item, root_str)
        if problems:
            rel = item['path'].replace(root_str + '/', '')
            issues.append({
                'path': rel,
                'name': item['name'],
                'is_dir': item['is_dir'],
                'problems': problems,
            })

    print(f'扫描完成: {stats["dirs"]} 目录, {stats["files"]} 文件\n', file=sys.stderr)

    if output_json:
        json.dump(issues, sys.stdout, ensure_ascii=False, indent=2)
        return

    if not issues:
        print('全部合规，零问题！')
        return

    by_type: dict[str, list] = {}
    for issue in issues:
        for p in issue['problems']:
            by_type.setdefault(p, []).append(issue)

    print(f'发现 {len(issues)} 个问题项:\n')

    for ptype, items in sorted(by_type.items(), key=lambda x: -len(x[1])):
        print(f'[{ptype}] {len(items)} 项')
        for item in items[:8]:
            tag = 'DIR' if item['is_dir'] else '   '
            print(f'  {tag} {item["path"]}')
        if len(items) > 8:
            print(f'  ... 还有 {len(items) - 8} 项')
        print()


if __name__ == '__main__':
    main()
