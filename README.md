# The World in One Day — Thursday 26 November 2026

[![make.fun bounty](https://img.shields.io/badge/make.fun-bounty-blue)](https://make.fun/bounty/news-image-20261126)
[![news-image-20261126](https://img.shields.io/badge/news--image-20261126-red)](https://make.fun/bounty/news-image-20261126)
[![35 stories](https://img.shields.io/badge/stories-35%20dated-green)](https://make.fun/bounty/news-image-20261126)

One image that sums up the world's news of **Thursday 26 November 2026**:
**35 dated stories · 7 regions · 14 fields**, every one first reported that day.

![The World in One Day — 26 November 2026](entry.png)

## The day, in three lines

- **Macy's 100th Thanksgiving Day Parade postponed** to Saturday 28 November —
  the first postponement in the parade's 100-year history, forced by the
  nor'easter slamming the US Northeast on Thanksgiving Day.
- **India marks 18 years since the 26/11 Mumbai attacks**, and Constitution Day.
- **Gukesh–Sindarov Game 3** in Geneva, the world-title duel level at 1–1.

## How it is built

- `stories.json` — the 35 stories, the ticker, the stat strip, the DATE CHECK
  exclusions, the UTC timeline and the map pins. Every story carries its
  region, field and first-publication date.
- `render.py` — draws the whole front page with Pillow: masthead with the
  date claim, ticker, three hero cards, ten featured cards with drawn scenes,
  a stat strip, a region bar, a DATE CHECK box, a schematic world map with
  numbered pins, the also-on list, a UTC timeline and a certainty legend.
  Deterministic: run it twice and the PNG bytes are identical.
- `main.py` — the entrypoint. Standard library only: it copies the committed
  `entry.png` to `MAKEFUN_OUTPUT_DIR` and verifies the copy byte for byte.
  It runs under the grader's Python with no network and no Pillow.
- `entry.png` — the finished front page, 1024×1024, 205,866 bytes.

Run it:

```sh
python3 render.py            # rebuild entry.png from stories.json
MAKEFUN_OUTPUT_DIR=out python3 main.py   # grader-style run
```

## Date discipline

The date of **every** story was checked against wire and publisher reports
before it was drawn — not against headlines or roundups, which mostly
re-report the previous day. The image says so itself in its DATE CHECK box,
naming the big stories that are *not* 26 November and were left out:

Cartagena hostages freed (Wed 25 Nov) · Honda's 810,592-car recall
(announced Fri 20 Nov) · India's ₹11,000-cr factory scheme (Cabinet,
Wed 25 Nov) · the turkey pardon (Wed 25 Nov) · the Cairo fuel-truck fire
(Wed 25 Nov) · Ramaphosa's Phala Phala win (Wed 25 Nov) · the US tariff
plan for 14 partners (Wed 25 Nov) · Shenzhou-24, the AI rout and the
Hormuz mines (Wed 25 Nov) · BepiColombo at Mercury (Sat 21 Nov) ·
the Nepal quake (Tue 24 Nov).

Items still to happen that day are marked FORECAST or listed under
"NOT YET" (Gukesh Game 3 at 15:00 CET, the EU Council running to Friday,
the New Zealand election result, the Macy's parade on Saturday).

Sources consulted include Reuters, AP, the Press Association, Punch
(Nigeria), RNZ, ABC News, the Consilium, Macy's/NBC and FIDE. Figures are
as reported; claims are labelled REPORTED, never presented as confirmed
where only one side has spoken.

The map is schematic: pins are spread slightly where four European stories
share a few degrees of longitude, so every number stays readable.

## License

MIT — see [LICENSE](LICENSE).
