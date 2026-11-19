import sys,re,urllib.request,html
u,out=sys.argv[1],sys.argv[2]
try:
    r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=100).read().decode("utf8","ignore")
    r=re.sub(r"(?s)<(script|style|nav|footer|header)[^>]*>.*?</\1>","",r)
    t=html.unescape(re.sub(r"<[^>]+>","\n",r)); t=re.sub(r"\n\s*\n+","\n",t)
    open(out,"w").write(t)
except Exception as e: open(out,"w").write("ERR "+str(e))
