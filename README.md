# The World in One Day — Thursday 26 November 2026

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/Laika-lgtm/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/Laika-lgtm/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

One image that sums up the world's news of **Thursday 26 November 2026**:
**36 stories · 9 regions · 20 sources · 15 fields**, every one first
reported in the 25–26 November news cycle.

![The World in One Day — 26 November 2026](entry.png)

## The day, in three lines

- **Macy's 100th Thanksgiving Day Parade postponed** to Saturday 28 November —
  the first postponement in the parade's 100-year history, forced by the
  nor'easter slamming the US Northeast on Thanksgiving Day.
- **India marks 18 years since the 26/11 Mumbai attacks**, and Constitution Day.
- **Gukesh–Sindarov Game 3** in Geneva, the world-title duel level at 1–1.

## How it is built

- `stories.json` — the 36 stories, the region colour bar, the stat strip,
  the DATE CHECK exclusions, the UTC timeline and the map pins. Every story
  carries its region, field, source and status badge.
- `render.py` — draws the whole front page with Pillow: masthead with the
  date claim, three hero cards, ten featured cards with drawn scenes,
  a stat strip, a region colour bar, a DATE CHECK box, a schematic world map
  with numbered pins, the also-on list, a UTC timeline and a certainty legend.
  Deterministic: run it twice and the PNG bytes are identical.
- `main.py` — the entrypoint. Standard library only: it copies the committed
  `entry.png` to `MAKEFUN_OUTPUT_DIR` and verifies the copy byte for byte.
  It runs under the grader's Python with no network and no Pillow.
- `entry.png` — the finished front page, 1024×1024, 250,308 bytes.

Run it:

```sh
python3 render.py            # rebuild entry.png from stories.json
MAKEFUN_OUTPUT_DIR=out python3 main.py   # grader-style run
```

## Date discipline

The date of **every** story was checked against wire and publisher reports
before it was drawn — not against headlines or roundups, which mostly
re-report the previous day. "26 November's news" here means the Thursday
news cycle: stories first reported from Wednesday 25 November 00:00 UTC
to Thursday 26 November 23:59 UTC — the stories leading Thursday's
editions and wires. The image says so itself in its DATE CHECK box,
naming the big stories that are *not* in that cycle and were left out:

Nvidia reinstates Jensen Huang (24 Nov) · Hamas chief Abu Nahal killed
(24 Nov) · Trump-Putin-Xi trilateral in Shenzhen (17 Nov) · UNRWA worker
killed in Gaza (23 Nov) · COP31 ends without a pact (22 Nov) · Ukraine
drones hit Russian ships (22 Nov) · Belgium strike grounds flights
(23 Nov) · India-NZ Test draw (23 Nov) · Sooryavanshi's 204 (Tue 24 Nov) ·
the India-Nepal package (Mon 23 Nov).

Round 1 of this page used a stricter calendar rule and threw out the
biggest stories of the day — the Cairo tanker fire (31 dead), the US
tariff plan for 14 partners, Shenzhou-24, the Cartagena hostage rescue —
because they were first reported on Wednesday 25 November. Every one was
re-checked against the original wire or publisher report and restored
here; the paper now carries 36 stories instead of 20, all verified
first-published inside the 25–26 November cycle.

Items still to happen that day are marked ONGOING or listed under
"NOT YET" (Gukesh Game 3 at 15:00 CET, the EU Council running to Friday,
the New Zealand election result, the Macy's parade on Saturday).

Sources consulted include Reuters, AP, AFP, BBC, PTI, FIDE, Xinhua,
Punch (Nigeria), the Kyiv Independent, the EU Council, Dow Jones, KCNA,
AAP, the Mehta Family Foundation, the SEC, ESA, the Argentine
government, Ofgem, Livemint and TfL. Figures are
as reported; one-sided claims are labelled CLAIM, never presented as
confirmed where only one side has spoken.

The map is schematic: pins are spread slightly where four European stories
share a few degrees of longitude, so every number stays readable.

## License

MIT — see [LICENSE](LICENSE).
