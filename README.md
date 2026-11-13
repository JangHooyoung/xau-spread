정적 페이지는 `index.html` 하나만 있으면 됩니다. GitHub Pages에 이 파일을 올리세요. 브라우저가 RISEx 호가 GET과 TXFlow `POST /info`를 직접 호출합니다. RISEx REST는 github.io Origin을 허용하지 않아서, 막히면 공식 웹소켓 `wss://ws.rise.trade/ws`로 같은 XAU 호가를 받습니다. 상세 CORS 결과는 상위 README를 보세요. 저장소 생성이나 푸시는 이 폴더만으로는 하지 않습니다.

## 과거 스프레드 내역 그래프

- `history.json`: 두 거래소 XAU 캔들 종가(7일·1시간, 3일·5분)를 묶은 파일. 스프레드 = RISE 종가 − TXFlow 종가 (USD, 체결가가 아닌 근사치).
- RISEx REST는 github.io에서 CORS로 막혀서 브라우저가 직접 못 받으므로, `build_history.py`로 미리 만들어 같이 올립니다.
- 갱신: `python3 build_history.py` 실행 후 `history.json`을 다시 푸시. 안 하면 그래프는 만든 시각에서 멈추고, 그 이후는 이 브라우저의 최근 실시간 기록(최대 2시간)만 이어집니다.
