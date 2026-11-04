"""일정 비교(compare.html)와 일정별 상세(trip-6/7/9.html)를 만든다.

사용법: python3 -I build_pages.py <시트를 xlsx로 내려받은 저장 파일 3개>
없으면 data/trips.json(마지막으로 읽은 시트 내용)으로 만든다.
"""
import base64, datetime, html, io, json, os, re, sys, zipfile
import xml.etree.ElementTree as ET

M = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
IDS = {'1jB53AJZHaoadYfwTCR3kw6RIRa9xWmapLsVsm4Qe7E4': '6',
       '1JGlaEhrE8_JIDEwztkn9RI6Whd6qA4sgzvq7LxXx6nY': '7',
       '1vFtOh2XIg6UYEzWnLGLMb325odbyIyd4QXgoptDE13M': '9'}


def read_sheet(path):
    j = json.load(open(path, encoding='utf8'))
    z = zipfile.ZipFile(io.BytesIO(base64.b64decode(j['content'])))
    ss = [''.join(t.text or '' for t in si.iter(M + 't'))
          for si in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    cells = {}
    for c in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).iter(M + 'c'):
        v = c.find(M + 'v')
        if v is None:
            continue
        m = re.match(r'([A-Z]+)(\d+)', c.get('r'))
        cells[(int(m[2]), m[1])] = ss[int(v.text)] if c.get('t') == 's' else v.text
    rows = sorted({r for r, c in cells if c == 'A' and str(cells[(r, c)]).startswith('DAY')})
    days = []
    for r in rows:
        g = lambda c: str(cells.get((r, c), '')).strip()
        date = g('B')
        if re.fullmatch(r'\d+(\.0)?', date):  # 시트의 날짜값 → '7월 31일'
            d = datetime.date(1899, 12, 30) + datetime.timedelta(days=int(float(date)))
            date = f'{d.month}월 {d.day}일'
        days.append(dict(no=g('A'), date=date, area=g('C'), move=g('D'), time=g('E'), plan=g('F'), meal=g('G')))
    head = lambda r, c='C': str(cells.get((r, c), '')).strip()
    return IDS[j['id']], dict(title=head(3, 'A'), people=head(5), price=head(5, 'F'), base=head(6),
                              inc=head(7), exc=head(8), note=head(9), days=days)


META = {
    '6': dict(name='6일 레닌봉', nights='4박 6일', tag='입문, 짧은 휴가', course='lenin', air='티웨이, 화 출발·일 귀국',
              trek='2일', passes='트래블러스 패스', peak='4,150m', stay='2박 (유르트 1)', city='오시', inner='비슈케크-오시 항공',
              card='아침에 베이스캠프로 올라 정비한 뒤 트래블러스 패스를 다녀옵니다. 다음 날 일출을 보고 내려오며, 오시 1박으로 귀국편 여유가 있습니다.',
              lead='레닌봉 하나에 집중하는 가장 짧은 일정입니다. 베이스캠프 유르트에서 하룻밤 자며 트래블러스 패스와 일출을 봅니다.'),
    '7': dict(name='7일 알라이·레닌봉', nights='5박 7일', tag='핵심 코스 전체', course='alay', air='티웨이, 토 출발·금 귀국',
              trek='3일', passes='집틱 패스, 트래블러스 패스', peak='4,185m', stay='3박 (유르트 2)', city='오시', inner='비슈케크-오시 항공',
              card='집틱 패스를 넘어 두드림유르트에서 자고, 사리모굴을 거쳐 레닌봉으로 이어 갑니다. 새벽 5시에 출발하는 패스 산행이 가장 힘든 날입니다.',
              lead='알라이 산맥과 레닌봉을 이어 걷는 키르기스 트레킹의 핵심 일정입니다.'),
    '9': dict(name='9일 + 사마르칸트', nights='7박 9일', tag='트레킹 + 실크로드', course='alay', air='아시아나, 금 출발·토 귀국',
              trek='3일', passes='집틱 패스, 트래블러스 패스', peak='4,185m', stay='3박 (유르트 2)', city='타슈켄트, 사마르칸트', inner='타슈켄트-오시 항공, 고속열차',
              card='7일과 같은 트레킹에 타슈켄트 시내 관광과 사마르칸트 1박을 더합니다. 패스를 다녀온 날 밤 항공으로 타슈켄트로 이동합니다.',
              lead='7일 일정과 같은 트레킹에 우즈베키스탄 3박을 더한 일정입니다.'),
}
ALT = {
    '6': [('D1', 800, 800), ('D2', 3600, 3000), ('D3', 4150, 3600), ('D4', 3600, 963), ('D5', 963, None)],
    '7': [('D1', 800, 800), ('D2', 2200, 2200), ('D3', 4185, None), ('D4', 3600, 3600), ('D5', 4150, 963), ('D6', 963, None)],
    '9': [('D1', 450, 450), ('D2', 963, 963), ('D3', 2200, 2200), ('D4', 4185, None), ('D5', 3600, 3600), ('D6', 4150, 450), ('D7', 700, 700), ('D8', 700, None)],
}
NAV = [('index.html', '코스 지도'), ('compare.html', '일정 비교'), ('trip-6.html', '6일 레닌봉'),
       ('trip-7.html', '7일 알라이·레닌봉'), ('trip-9.html', '9일 + 사마르칸트')]
ALT_NOTE = '막대는 그날 오른 최고 지점, 점은 자는 곳입니다. 점이 없는 날은 두드림유르트(고도 미측정) 또는 기내 숙박입니다. 코조캘렌은 2,200m(Visit Alay) 기준입니다.'


def esc(s):
    return html.escape(s, quote=False)


def red(s):
    return re.sub(r'\[[^\]\n]*확인 필요\]', lambda m: f'<span class="chk">{m[0]}</span>', esc(s))


def page(cur, title, body):
    on = ' aria-current="page"'
    nav = ''.join(f'<a href="{h}"{on if h == cur else ""}>{n}</a>' for h, n in NAV)
    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | 키르기스 트레킹</title><link href="site.css" rel="stylesheet"></head>
<body><header class="hdr"><a class="logo" href="index.html">두드림 키르기스 트레킹</a><nav aria-label="주 메뉴">{nav}</nav></header>
<main class="wrap">{body}</main>
<footer class="ft">두드림여행사 · 010-2782-2660 · dodreamtour.com</footer></body></html>
'''


def alt_svg(keys):
    width = 760 if len(keys) > 1 else 560
    band = 30 if len(keys) > 1 else 58
    base, k, gap, x = 176, 128 / 4500, 30, 46
    y = lambda v: base - v * k
    s = [f'<line x1="0" x2="{width}" y1="{y(3000):.1f}" y2="{y(3000):.1f}" stroke="#a5abb3" stroke-dasharray="4 4"/>'
         f'<text x="0" y="{y(3000) - 4:.1f}">3,000m</text>']
    for key in keys:
        if len(keys) > 1:
            s.append(f'<text x="{x + 3}" y="14" class="h">{META[key]["name"]}</text>')
        for i, (d, h, sl) in enumerate(ALT[key]):
            bx = x + i * band + 4
            w = band - 12
            c = bx + w / 2
            over = h >= 4000
            s.append(f'<rect x="{bx}" y="{y(h):.1f}" width="{w}" height="{base - y(h):.1f}" rx="3" fill="{"#2a78d6" if over else "#d9d8d1"}"><title>{d} {h:,}m</title></rect>')
            if over:
                s.append(f'<text x="{c}" y="{y(h) - 5:.1f}" text-anchor="middle" class="v">{h:,}</text>')
            if sl:
                s.append(f'<circle cx="{c}" cy="{y(sl):.1f}" r="4.5" fill="#111" stroke="#fff" stroke-width="1.4"><title>자는 곳 {sl:,}m</title></circle>')
            s.append(f'<text x="{c}" y="{base + 15}" text-anchor="middle">{d}</text>')
        x += len(ALT[key]) * band + gap
    s.append(f'<line x1="0" x2="{width}" y1="{base}" y2="{base}" stroke="#b9bec5"/>')
    return f'<svg class="alt" viewBox="0 0 {width} 196" role="img" aria-label="일자별 고도">{"".join(s)}</svg>'


def cards():
    return '<div class="cards">' + ''.join(
        f'<a class="card" href="trip-{k}.html"><b>{m["name"]}</b><div class="d">{m["nights"]} · {m["tag"]}</div>'
        f'<p>{m["card"]}</p><span class="go">상세 일정 보기 →</span></a>' for k, m in META.items()) + '</div>'


def compare():
    rows = [('기간', 'nights'), ('항공 (2026년 기준)', 'air'), ('트레킹 일수', 'trek'), ('넘는 고개', 'passes'),
            ('최고 고도', 'peak'), ('산악 숙박', 'stay'), ('도시 관광', 'city'), ('내부 이동', 'inner')]
    tr = ''.join(f'<tr><td>{n}</td>' + ''.join(f'<td>{META[k][f]}</td>' for k in META) + '</tr>' for n, f in rows)
    head = ''.join(f'<th><a href="trip-{k}.html">{META[k]["name"]}</a></th>' for k in META)
    return page('compare.html', '일정 비교', f'''
<h1>키르기스 트레킹 3종 비교</h1>
<p class="lead">짧은 휴가로 레닌봉만 보려면 6일, 알라이와 레닌봉을 모두 걸으려면 7일, 여기에 사마르칸트까지 더하려면 9일을 권합니다.</p>
{cards()}
<h2>핵심 지표</h2>
<div class="scroll"><table class="cmp"><tr><th>지표</th>{head}</tr>{tr}
<tr><td>인원·요금</td><td colspan="3">출발 8~20명 · 1인 요금 <span class="chk">[확인 필요]</span></td></tr></table></div>
<h2>일자별 고도</h2>
<p class="fig">4,000m를 넘는 날은 6일 1번, 7·9일 2번</p>
<div class="scroll">{alt_svg(['6', '7', '9'])}</div>
<p class="cap">{ALT_NOTE}</p>
<h2>확인할 점</h2>
<ul class="cap">
<li>코조캘렌 고도가 자료마다 다르고(2,200m, 3,000m), 두드림유르트 고도는 없습니다.</li>
<li>항공은 2026년 스케줄 기준입니다. 타슈켄트-오시 항공은 수·토 운항이라 일정이 바뀌면 9일 상품의 틀도 바뀝니다.</li>
</ul>''')


def day_html(d):
    items = []
    stay = ''
    lines = [l.strip() for l in d['plan'].split('\n') if l.strip()]
    for i, l in enumerate(lines):
        if l.startswith('숙박'):
            stay = l.split(':', 1)[-1].strip()
            continue
        cls = ''
        if i == 0 and len(l) <= 26 and ',' not in l and re.search(r'(트레킹|관광|산책)$', l):
            cls = ' class="t"'
        elif re.search(r' - .* / |주변 / ', l):
            cls = ' class="r"'
        items.append(f'<li{cls}>{red(l)}</li>')
    join = lambda s, sep: sep.join(x.strip() for x in s.split('\n') if x.strip())
    meta = [('교통', join(d['move'], ' · ')), ('시간', join(d['time'], ' · ')),
            ('식사', join(d['meal'].replace('조:', '조').replace('중:', '중').replace('석:', '석'), ' · '))]
    if stay:
        meta.insert(0, ('숙박', stay))
    m = ''.join(f'<span><b>{n}</b> {red(v)}</span>' for n, v in meta if v)
    return (f'<article class="day"><div><div class="no">{esc(d["no"])}</div><div class="dt">{esc(d["date"])}</div></div>'
            f'<div><div class="route">{esc(join(d["area"], " → "))}</div><ul>{"".join(items)}</ul><div class="meta">{m}</div></div></article>')


def trip(key, t):
    m = META[key]
    facts = [('기간', m['nights']), ('최고 고도', m['peak']), ('트레킹 일수', m['trek']), ('항공', m['air']),
             ('산악 숙박', m['stay']), ('1인 요금', red(t['price']))]
    f = ''.join(f'<div class="fact"><span>{a}</span><b>{b}</b></div>' for a, b in facts)
    info = [('출발 인원', t['people']), ('숙소·차량', t['base']), ('포함', t['inc']), ('불포함', t['exc']), ('참고', t['note'])]
    dl = ''.join(f'<dt>{a}</dt><dd>{red(b)}</dd>' for a, b in info if b)
    return page(f'trip-{key}.html', m['name'], f'''
<h1>{esc(t["title"])}</h1>
<p class="lead">{m["lead"]}</p>
<div class="facts">{f}</div>
<div class="acts"><a class="btn" href="index.html?course={m["course"]}">코스 지도에서 보기</a><a class="btn sec" href="compare.html">일정 비교로 돌아가기</a></div>
<h2>일자별 일정</h2>
{"".join(day_html(d) for d in t["days"])}
<h2>일자별 고도</h2>
{alt_svg([key])}
<p class="cap">{ALT_NOTE}</p>
<h2>상품 안내</h2>
<dl class="info">{dl}</dl>''')


here = os.path.dirname(os.path.abspath(__file__))
store = os.path.join(here, 'data', 'trips.json')
if len(sys.argv) > 1:
    trips = dict(read_sheet(p) for p in sys.argv[1:])
    json.dump(trips, open(store, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
else:
    trips = json.load(open(store, encoding='utf8'))
open(os.path.join(here, 'compare.html'), 'w', encoding='utf8').write(compare())
for k, t in trips.items():
    open(os.path.join(here, f'trip-{k}.html'), 'w', encoding='utf8').write(trip(k, t))
    print(k, t['title'], len(t['days']), 'days', t['people'], t['price'])
