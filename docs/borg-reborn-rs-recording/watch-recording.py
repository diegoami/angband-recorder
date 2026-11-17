#!/usr/bin/env python3
"""Play a recording's screen frames in the terminal.

  watch-recording.py RECORDING/native [--from-turn T] [--to-turn T] [--delay S] [--every N]

Reads native/frames.jsonl once (the same frames `angband-recorder view` rebuilds), redraws the
80x24 screen at each command frame. Ctrl-C stops. --every N shows every Nth command frame.
"""
import argparse, json, sys, time
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('native', type=Path)
p.add_argument('--from-turn', type=int, default=0)
p.add_argument('--to-turn', type=int, default=None)
p.add_argument('--delay', type=float, default=0.05)
p.add_argument('--every', type=int, default=1)
a = p.parse_args()
screen, dims, shown, n = [], (0, 0), 0, 0
out = sys.stdout
out.write('\x1b[?25l\x1b[2J')
try:
    with open(a.native / 'frames.jsonl') as f:
        for line in f:
            fr = json.loads(line)
            w, h = fr['width'], fr['height']
            if (w, h) != dims:
                screen, dims = [' '] * (w * h), (w, h)
            for at, code, *_ in fr['cells']:
                c = chr(code)
                screen[at] = c if c.isprintable() else ' '
            turn = fr.get('turn') or 0
            if fr.get('phase') != 'command' or turn < a.from_turn:
                continue
            if a.to_turn is not None and turn > a.to_turn:
                break
            n += 1
            if n % a.every:
                continue
            rows = [''.join(screen[i:i + w]) for i in range(0, w * h, w)]
            out.write('\x1b[H' + '\n'.join(rows) +
                      f"\n\x1b[7m frame {fr.get('index')}  turn {turn}  depth {fr.get('depth')}  "
                      f"HP {fr.get('hp')}/{fr.get('max_hp')} \x1b[0m\x1b[K")
            out.flush()
            time.sleep(a.delay)
except KeyboardInterrupt:
    pass
finally:
    out.write('\x1b[?25h\n')
