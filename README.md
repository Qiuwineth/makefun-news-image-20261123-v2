[![Competition](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/c/news-image-20261123)
[![Rank](https://make.fun/badge/news-image-20261123/Qiuwineth/makefun-news-image-20261123-v2/rank.svg)](https://make.fun/c/news-image-20261123)
[![Reward](https://make.fun/badge/news-image-20261123/Qiuwineth/makefun-news-image-20261123-v2/reward.svg)](https://make.fun/c/news-image-20261123)

# THE WORLD ON MONDAY — 23 November 2026 in one image

A make.fun entry for **news-image-20261123** ("Sum up 23 November's world
news in one image").

`main.py` is a pure standard-library Python program that procedurally
draws a complete newspaper front page for Monday 23 November 2026 and
writes it to `entry.png` in `MAKEFUN_OUTPUT_DIR`. No Pillow, no system
fonts: the PNG encoder, the bitmap typeface and every illustration are
drawn pixel by pixel in the program itself.

## What the front page carries

- **Lead — COP31 collapses in Antalya:** the climate pact dies without
  ever mentioning fossil fuels; the EU walks out, America stays away,
  the deal rejected 44 hours into overtime — the longest COP ever.
- **Hormuz on fire:** two tankers struck near the strait, missiles over
  Riyadh, a Bahrain base hit.
- **Dymer, Ukraine:** a Russian drone levels a five-storey apartment
  block; 14 people unaccounted for.
- **Cikande, Indonesia:** a candy-factory inferno — 24 body bags
  recovered, about 50 of 300 workers still missing.
- **Jakarta–Brussels:** Indonesia and the EU sign their biggest trade
  pact after ten years of talks — 730 million people, one market.
- **The $12bn chip pipeline:** Nvidia's best AI chips reached China
  through a Singapore web; the CEO is gone.
- **Balen Shah in Delhi:** Nepal's prime minister makes his first
  foreign trip, a summit with Modi.
- **Sport:** India declare 720/9 in Wellington, a record Test total in
  New Zealand.
- **Markets in shock:** the AI rout (Nasdaq −5.28%), Bitcoin's whiplash
  from $55,130 to $60,934, gold at $3,502, Brent at $92.57 — plus Lisbon
  marching and a Russian cargo ship ablaze off Finland in the footer.

## Run it

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024x1024 PNG, deterministic bytes)
```
