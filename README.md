# 알라이·레닌봉 트레킹 코스 지도

맵박스 지도 웹페이지. 코스선, 거점 마커, 고도계, 트레일 미리보기(지형 위 카메라 이동).

- 페이지: `index.html`(코스 지도), `compare.html`(일정 비교), `trip-6/7/9.html`(일정 상세). 헤더는 `index.html`과 `build_pages.py`의 NAV에 있다.
- 일정표가 바뀌면 시트를 xlsx로 받아 `python3 -I build_pages.py <저장 파일 3개>`로 다시 만든다. 파일 없이 실행하면 `data/trips.json`을 쓴다.
- 미리보기 카메라: 경로를 미리 계산(`buildPath`)하고 `setPitchBearing`으로 움직인다. `lookAtPoint`는 각도 한계(85°)에 걸려 카메라 높이가 튄다. 지형 과장값 EX를 바꾸면 카메라 높이 계산에도 같이 반영된다.
- 실행: `python3 -m http.server 3011` (launch.json `alay-lenin-map`)
- 데이터 다시 만들기: `python3 -I build.py` → `data.js`
- 토큰: `config.js`. 공개 배포 때는 dolomiti.co.kr로 주소가 제한된 토큰으로 바꾼다.
- 경로: OSM 등산로를 BRouter(hiking-mountain)로 연결(`data/*-brouter.json`). 차량 구간은 OSRM, 오시-코조캘렌-CBT 유르트는 개략 직선.
- 추정 위치: CBT 유르트(3,050m 지점), 두드림유르트(패스에서 약 3km), 차도 끝(패스에서 약 11km). 현장 GPS로 `build.py`의 S, E 값과 yurt 계산을 고친다.
