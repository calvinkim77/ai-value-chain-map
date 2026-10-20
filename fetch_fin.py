import re, json, sys, time, urllib.request, os

UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}
TICKERS = {
 # US
 "VRT":"stocks/vrt","GEV":"stocks/gev","ETN":"stocks/etn","PWR":"stocks/pwr","VST":"stocks/vst","BE":"stocks/be",
 "ASML":"stocks/asml","AMAT":"stocks/amat","LRCX":"stocks/lrcx","KLAC":"stocks/klac","TSM":"stocks/tsm",
 "INTC":"stocks/intc","AMKR":"stocks/amkr","ASX":"stocks/asx","MU":"stocks/mu","SNDK":"stocks/sndk",
 "NVDA":"stocks/nvda","AMD":"stocks/amd","AVGO":"stocks/avgo","ALAB":"stocks/alab","MRVL":"stocks/mrvl",
 "CRDO":"stocks/crdo","RMBS":"stocks/rmbs","PSTG":"stocks/pstg","WDC":"stocks/wdc","DELL":"stocks/dell",
 "SMCI":"stocks/smci","HPE":"stocks/hpe","CRWV":"stocks/crwv","NBIS":"stocks/nbis","IREN":"stocks/iren",
 "APLD":"stocks/apld","ORCL":"stocks/orcl","DLR":"stocks/dlr","EQIX":"stocks/eqix","GOOGL":"stocks/googl",
 "META":"stocks/meta","MSFT":"stocks/msft","AMZN":"stocks/amzn","TSLA":"stocks/tsla",
 # KR
 "005930":"quote/krx/005930","000660":"quote/krx/000660","267260":"quote/krx/267260","298040":"quote/krx/298040",
 "010120":"quote/krx/010120","062040":"quote/krx/062040","018260":"quote/krx/018260","035420":"quote/krx/035420",
 "030200":"quote/krx/030200","012330":"quote/krx/012330",
 "403870":"quote/kosdaq/403870","240810":"quote/kosdaq/240810","036930":"quote/kosdaq/036930",
 "039030":"quote/kosdaq/039030","357780":"quote/kosdaq/357780","108490":"quote/kosdaq/108490",
 # JP / TW / CN
 "8035":"quote/tyo/8035","285A":"quote/tyo/285A","2382":"quote/tpe/2382","2317":"quote/tpe/2317","688008":"quote/sha/688008",
}
NQ = 8

def get(url):
    req=urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as f:
        return f.read().decode('utf-8','ignore')

def parse(h):
    i=h.find('data:{datekey:[')
    if i<0: return None
    seg=h[i:i+250000]
    dk=re.search(r'datekey:\[([^\]]*)\]', seg)
    rev=re.search(r'revenue:\[([^\]]*)\]', seg)
    op=re.search(r'opinc:\[([^\]]*)\]', seg)
    if not (dk and rev and op): return None
    num=lambda s:[float(x) for x in s.split(',') if x.strip() not in ('','null')]
    dates=[x.strip().strip('"') for x in dk.group(1).split(',') if x.strip()]
    r=num(rev.group(1)); o=num(op.group(1))
    n=min(len(dates),len(r),len(o))
    rows=[]
    for k in range(n):
        if r[k] and o[k] is not None:
            rows.append({"d":dates[k],"rev":r[k],"op":o[k]})
    return rows[:NQ]

out={}
lo,hi=int(sys.argv[1]),int(sys.argv[2])
keys=list(TICKERS)[lo:hi]
for t in keys:
    url=f"https://stockanalysis.com/{TICKERS[t]}/financials/?p=quarterly"
    rows=None
    for attempt in range(2):
        try:
            rows=parse(get(url)); 
            if rows: break
        except Exception as e:
            pass
        time.sleep(1.5)
    out[t]=rows
    print(t, len(rows) if rows else 0, flush=True)
    time.sleep(0.7)

p="data/fin_part%d.json"%lo
json.dump(out, open(p,"w"), ensure_ascii=False)
print("saved", p, len(out))
