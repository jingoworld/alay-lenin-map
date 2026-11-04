import json,math
def load(f): return json.load(open('data/'+f))
def dist(a,b): return math.hypot((a[0]-b[0])*math.cos(math.radians(a[1]))*111.32,(a[1]-b[1])*111.32)
def smooth(z,w=4):
    return [sum(z[max(0,i-w):i+w+1])/len(z[max(0,i-w):i+w+1]) for i in range(len(z))]
def prep(c):
    z=smooth([p[2] for p in c]);out=[];d=0
    for i,p in enumerate(c):
        if i: d+=dist(c[i-1],p)
        out.append([round(p[0],5),round(p[1],5),round(z[i]),round(d,3)])
    return out
def stats(t):
    up=dn=0;last=t[0][2]
    for p in t:
        e=p[2]-last
        if abs(e)>=8:
            if e>0: up+=e
            else: dn-=e
            last=p[2]
    return dict(km=round(t[-1][3]-t[0][3],1),up=round(up),dn=round(dn),max=max(p[2] for p in t),min=min(p[2] for p in t))
A=prep(load('alay-brouter.json')['features'][0]['geometry']['coordinates'])
L=prep(load('lenin-brouter.json')['features'][0]['geometry']['coordinates'])
S,E=17.0,38.0
seg=[p for p in A if S<=p[3]<=E]; d0=seg[0][3]
at=[[p[0],p[1],p[2],round(p[3]-d0,3)] for p in seg]
def nearest(t,km): return min(t,key=lambda p:abs(p[3]-km))
peak=max(at,key=lambda p:p[2]); yurt=nearest(at,peak[3]+3.0)
bc=min(L,key=lambda p:dist(p,[72.915,39.4805]))
road=lambda f:[[round(x,5),round(y,5)] for x,y in load(f)['routes'][0]['geometry']['coordinates']][::3]
data=dict(courses=dict(
 alay=dict(name='알라이 트레킹',sub='코조캘렌 · CBT 유르트 · 집틱 패스 · 두드림유르트 · 차도',track=at,stats=stats(at),note='CBT 유르트 → 집틱 패스 → 두드림유르트 → 차도까지 걷는 구간입니다.',
   cuts=[dict(name='CBT 유르트',km=0),dict(name='집틱 패스',km=peak[3]),dict(name='두드림유르트',km=yurt[3]),dict(name='차도',km=at[-1][3])]),
 lenin=dict(name='레닌봉 트레킹',sub='툴파르콜 · 베이스캠프 · 트래블러스 패스',track=L,stats=stats(L),note='편도 기준입니다. 패스에서 베이스캠프로 돌아옵니다.',
   cuts=[dict(name='툴파르콜',km=0),dict(name='베이스캠프',km=bc[3]),dict(name='트래블러스 패스',km=L[-1][3])])),
 jeep=[[[72.80,40.53],[72.9657,39.9696]],[[72.9657,39.9696],at[0][:2]],[p[:2] for p in A if p[3]>=E][::4],road('osh_sary.json'),road('sary_tulpar.json')],
 pois=[
 dict(id='osh',name='오시',ele=963,kind='city',lng=72.80,lat=40.53,text='출발 도시. 여기서 전용 지프로 산에 들어갑니다.'),
 dict(id='kojo',name='코조캘렌',ele=None,kind='stay',lng=72.9657,lat=39.9696,text='알라이 코스 첫 숙박. 도착 후 시간이 남으면 주변 고소적응 트레킹을 합니다.'),
 dict(id='cbt',name='CBT 유르트',ele=at[0][2],kind='est',lng=at[0][0],lat=at[0][1],text='코조캘렌에서 차량으로 오는 트레킹 시작점. 위치는 추정입니다.',course='alay'),
 dict(id='jiptik',name='집틱 패스',ele=4185,kind='pass',lng=72.93419,lat=39.80697,text='알라이 코스 최고점. 파미르 산맥과 레닌봉을 조망합니다.',course='alay'),
 dict(id='dd',name='두드림유르트',ele=yurt[2],kind='est',lng=yurt[0],lat=yurt[1],text='패스에서 1시간 하산한 중간 유르트(가칭). 위치는 추정입니다.',course='alay'),
 dict(id='end',name='차도 끝',ele=at[-1][2],kind='est',lng=at[-1][0],lat=at[-1][1],text='유르트에서 3시간 하산. 여기서 차량으로 사리모굴로 갑니다. 위치는 추정입니다.',course='alay'),
 dict(id='sary',name='사리모굴',ele=3000,kind='stay',lng=72.8841,lat=39.6737,text='알라이 계곡의 마을. 레닌봉 트레킹의 거점입니다.'),
 dict(id='tulpar',name='툴파르콜',ele=3500,kind='lake',lng=72.9367,lat=39.5071,text='지프로 오는 호수. 레닌봉 트레킹 시작점입니다.',course='lenin'),
 dict(id='bc',name='레닌봉 베이스캠프',ele=3600,kind='stay',lng=bc[0],lat=bc[1],text='유르트 캠프가 모인 곳. 여기서 자고 패스를 다녀옵니다.',course='lenin'),
 dict(id='tp',name='트래블러스 패스',ele=4150,kind='pass',lng=72.89935,lat=39.4372,text='레닌봉 코스 최고점. 레닌봉과 빙하를 가까이 봅니다.',course='lenin'),
 dict(id='lenin',name='레닌봉',ele=7134,kind='peak',lng=72.87918,lat=39.34698,text='파미르의 7,000m급 봉우리. 트레킹 목표가 아니라 조망 대상입니다.')])
data['courses']['alay']['stats']['max']=4185;data['courses']['lenin']['stats']['max']=4150
open('data.js','w',encoding='utf8').write('window.TREK='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n')
for k,c in data['courses'].items(): print(k,c['stats'],len(c['track']),c['cuts'])
