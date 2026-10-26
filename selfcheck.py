# -*- coding: utf-8 -*-
"""无头自检（不开窗口、不播放音频）：SRT 解析 + VLC 绑定可用性。

用法：python selfcheck.py    （退出 0 = 通过）
GUI 入口仍是 `python play.py`。
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

import play  # noqa: E402  （模块级只定义函数/类，__main__ 下才开窗）

SAMPLE = """1
00:00:01,500 --> 00:00:04,000
第一句

2
00:01:02,250 --> 00:01:05,000
第二句
"""

BROKEN = """1
not-a-time-range
坏块
"""


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="daily-player-selfcheck-") as tmp:
        good = Path(tmp) / "sample.srt"
        good.write_text(SAMPLE, encoding="utf-8")
        subs = play.parse_srt(str(good))
        if len(subs) != 2:
            print(f"FAIL parse_srt returned {len(subs)} entries, expected 2")
            return 1
        start, end, text = subs[0]
        if abs(start - 1.5) > 1e-6 or abs(end - 4.0) > 1e-6 or text != "第一句":
            print(f"FAIL first subtitle {subs[0]!r}")
            return 1
        if abs(subs[1][0] - 62.25) > 1e-6:
            print(f"FAIL second subtitle start {subs[1][0]!r}")
            return 1

        bad = Path(tmp) / "broken.srt"
        bad.write_text(BROKEN, encoding="utf-8")
        if play.parse_srt(str(bad)):
            print("FAIL broken SRT produced entries")
            return 1

        # VLC 绑定：能建实例与播放器即证明运行库可用（不加载媒体、不出声）
        instance = play.vlc.Instance()
        player = instance.media_player_new()
        if instance is None or player is None:
            print("FAIL vlc instance/player not created")
            return 1
        media = instance.media_new(str(good))
        if media is None or not media.get_mrl():
            print("FAIL vlc media_new did not produce an MRL")
            return 1

    print("selfcheck ok: srt parse x2（时间轴/文本）+ broken guard + vlc binding（instance/player/media MRL）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
