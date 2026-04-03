# Quant

개인 투자 분석을 위한 Python 도구 모음입니다. 미국·한국·글로벌 주식, 암호화폐, 환율 데이터를 수집하고, RSI·볼린저밴드 등 기술적 지표와 연도별 수익률·CAGR·베타 등 통계를 계산하여 엑셀로 출력합니다.

## 핵심 스크립트

### price.py — 기술적 지표 + 가격 이력

`ticker.txt`에 등록된 종목의 과거 종가 데이터를 다운로드하고, 일봉·주봉·월봉 기준 RSI와 볼린저밴드 %B를 계산합니다. 캘린더 기준 일별 데이터(주말·공휴일 포함, 전일 종가로 채움)와 기술적 지표를 합쳐 `price.xlsx`로 출력합니다.

```bash
python price.py              # 기본 16년치 데이터
python price.py --years 10   # 10년치 데이터
```

### stats.py — 종목 펀더멘탈 + 연도별 수익률

시가총액(USD 기준 $B, KRW 기준 억 원), 베타, Trailing/Forward PER, S&P 500 대비 상대 변동성(`beta"`) 및 2011년부터 현재까지 연도별 수익률(%)을 계산합니다. 메타데이터는 멀티스레딩으로 병렬 수집합니다.

```bash
python stats.py              # ticker.txt 사용
python stats.py stats.txt    # 한국 주식 등 다른 티커 파일 지정
```

### premarket.py — 프리마켓/애프터마켓 가격 조회

장 시작 전·후 시간 외 거래 포함 최신 가격을 1분봉 기준으로 조회합니다. 10개 스레드로 병렬 처리하여 빠르게 `premarket.xlsx`로 출력합니다.

```bash
python premarket.py
```

### korea.py — 한국 주식 전용 분석

`kor_ticker.dat` 파일의 한국 종목(ETF + 개별주)을 FinanceDataReader로 다운로드하고, RSI·볼린저밴드·180일 Historical Volatility를 계산합니다. HV는 기준 종목(삼성전자) 대비 정규화하여 상대적 변동성을 비교할 수 있습니다.

```bash
python korea.py
```

### crypto.py — 암호화폐 지표 분석

BTC, ETH, SOL, XRP, DOGE, ADA의 KRW 가격을 yfinance로 다운로드하고, 일봉·주봉·월봉 기준 RSI와 볼린저밴드 %B를 계산하여 `crypto.xlsx`로 출력합니다.

```bash
python crypto.py
```

### upbit.py — 업비트 BTC 실시간 조회

업비트 API를 통해 BTC 현재가, 전고점 대비 등락률, 일일 변동률, 보유 잔고 평가금액을 콘솔에 출력합니다.

```bash
python upbit.py
```

### exchange.py — 환율 조회

서울외국환중개(SMBS) API에서 USD, EUR, JPY 기준 환율을 조회합니다.

```bash
python exchange.py            # 오늘 날짜 기준
python exchange.py 2025-06-01 # 특정 날짜 지정
```

### screening/screen.py — 종목 스크리닝

섹터별 티커 목록 파일을 입력받아 연도별 수익률, 1·3·5·10년 CAGR, RSI, 볼린저밴드, PER, 배당수익률, 베타 등을 한 번에 분석합니다. 미국 시장과 해외 시장을 자동 분리하여 별도 시트에 저장합니다.

```bash
python screening/screen.py screening/tech_comm.txt     # 기술/통신 섹터
python screening/screen.py screening/healthcare.txt    # 헬스케어
python screening/screen.py screening/japan.txt         # 일본 시장
python screening/screen.py screening/kingdom.txt       # 영국 시장
```

## 프로젝트 구조

```
quant/
├── price.py                 # 기술적 지표 + 가격 이력 → price.xlsx
├── stats.py                 # 펀더멘탈 + 연도별 수익률 → stats.xlsx
├── premarket.py             # 프리/애프터마켓 가격 → premarket.xlsx
├── korea.py                 # 한국 주식 분석 → kdrx.xlsx
├── crypto.py                # 암호화폐 지표 → crypto.xlsx
├── upbit.py                 # 업비트 BTC 실시간 조회
├── exchange.py              # USD/EUR/JPY 환율 조회
├── ticker.txt               # 글로벌 종목 리스트 (미국·대만·유럽·일본)
├── stats.txt                # 한국 주식 티커 리스트 (yfinance용 .KS/.KQ)
├── kor_ticker.dat           # 한국 종목 리스트 (종목코드 → 종목명)
├── prompt.txt               # AI 뉴스 요약·영상 분석용 프롬프트 모음
├── nanobanana.txt           # 이미지 생성 프롬프트
├── screening/
│   ├── screen.py            # 섹터별 종목 스크리닝
│   ├── all_tickers.csv      # 전체 티커 목록
│   ├── tech_comm.txt        # 기술/통신 (526개)
│   ├── healthcare.txt       # 헬스케어 (438개)
│   ├── indus_util.txt       # 산업재/유틸리티 (532개)
│   ├── consumer.txt         # 소비재 (215개)
│   ├── japan.txt            # 일본 시장 (500개)
│   └── kingdom.txt          # 영국 시장 (100개)
└── draft/
    └── history.py           # 특정 기간 평균 종가 조회 (실험용)
```

## 설치

```bash
pip install yfinance pandas ta xlsxwriter finance-datareader requests
```

## 필요 환경

- Python 3.10+
- Windows 환경 권장 (`os.startfile()`로 엑셀 자동 실행, macOS/Linux에서는 수동으로 파일을 열어야 함)

## 사용되는 기술적 지표

| 지표 | 설명 | 기본 설정 |
|------|------|-----------|
| RSI | 상대강도지수 (일봉/주봉/월봉) | 14일 |
| BB %B | 볼린저밴드 내 현재가 위치 (0~100%) | 14일, 2σ |
| HV | Historical Volatility (연율화) | 180일 |
| beta" | S&P 500 대비 상대 변동성 | 전체 기간 |

## 참고사항

- 모든 출력은 `.xlsx` 엑셀 파일로 저장되며, Windows에서는 자동으로 열립니다.
- `ticker.txt`를 수정하여 관심 종목을 자유롭게 추가·삭제할 수 있습니다. `#`으로 시작하는 줄은 주석 처리됩니다.
- yfinance의 API 제한에 따라 대량 종목 조회 시 속도가 느려질 수 있습니다.
