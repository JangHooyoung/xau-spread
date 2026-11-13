#!/usr/bin/env python3
"""Build history.json for the XAU spread page (read-only public APIs, no auth).

RISEx REST blocks CORS from github.io, so the browser cannot fetch its candles.
This script fetches RISEx (market 17) and TXFlow (XAU-USDC, id 51) candle closes
server-side and writes a static history.json next to index.html. Re-run and push
to refresh; otherwise the past-spread chart stays frozen at the build time.
"""
import json, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent / "history.json"
TX_INFO = "https://rpc.txflow.com/info"
TX_VER = "2026-08-16"
RISE_TV = "https://api.rise.trade/v1/markets/id/{mid}/trading-view-data?interval={iv}&from={a}&to={b}"
RISE_ID, TX_ID = 17, 51
WINDOWS = {"h1": (3600, 7 * 86400, "1h"), "m5": (300, 3 * 86400, "5m")}
UA = {"User-Agent": "xau-spread/1.0", "Accept": "application/json"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.loads(r.read())


def tx(body):
    req = urllib.request.Request(TX_INFO, data=json.dumps(body).encode(), method="POST",
                                 headers={**UA, "Content-Type": "application/json", "x-api-version": TX_VER})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def rise_candles(step, start, end):
    b = get(RISE_TV.format(mid=RISE_ID, iv=step * 10**9, a=start * 10**9, b=end * 10**9))
    rows = (b.get("data") or {}).get("data") or []
    return {int(r["time"]) // 10**9: float(r["close"]) for r in rows}


def tx_candles(iv, start, end):
    b = tx({"type": "candleSnapshot", "req": {"coin": str(TX_ID), "interval": iv,
                                               "startTime": start * 1000, "endTime": end * 1000}})
    return {int(r["t"]) // 1000: float(r["c"]) for r in (b.get("data") or [])}


def stats(vals):
    n = len(vals)
    if n < 2:
        return None
    m = sum(vals) / n
    sd = (sum((v - m) ** 2 for v in vals) / (n - 1)) ** 0.5
    return {"n": n, "mean": round(m, 4), "std": round(sd, 4)}


def main():
    out = {}
    for key, (step, span, iv) in WINDOWS.items():
        end = int(time.time()) // step * step
        start = end - span
        rc, tc = rise_candles(step, start, end + step), tx_candles(iv, start, end + step)
        pts = [[t, rc[t], tc[t]] for t in sorted(set(rc) & set(tc))]
        out[key] = pts
        out["stats_" + key] = stats([r - x for _, r, x in pts])
        print(f"{key}: rise={len(rc)} tx={len(tc)} joined={len(pts)}")
    now = int(time.time())
    OUT.write_text(json.dumps({
        "generated_at": now,
        "generated_at_iso": datetime.fromtimestamp(now, timezone.utc).isoformat(),
        "note": "XAU candle closes of both venues; spread = rise_close - tx_close (USD, approx, not fills)",
        "fields": ["t_sec", "rise_close", "tx_close"],
        **out,
    }, separators=(",", ":")))
    print("wrote", OUT, OUT.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
