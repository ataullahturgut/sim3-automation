from html.parser import HTMLParser
from urllib.parse import urljoin
import requests

PAGE='https://www.matteoiacoviello.com/gpr.htm'

class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.href=None; self.text=[]; self.links=[]
    def handle_starttag(self, tag, attrs):
        if tag.lower()=='a':
            self.href=dict(attrs).get('href'); self.text=[]
    def handle_data(self, data):
        if self.href is not None: self.text.append(data)
    def handle_endtag(self, tag):
        if tag.lower()=='a' and self.href is not None:
            text=' '.join(''.join(self.text).split())
            self.links.append((text,self.href)); self.href=None; self.text=[]

r=requests.get(PAGE,timeout=60)
r.raise_for_status()
p=P(); p.feed(r.text)
found=[]
for text,href in p.links:
    key=(text+' '+href).lower()
    if 'vintage' in key or 'archive' in key or ('gpr' in key and 'file' in key):
        found.append((text,urljoin(PAGE,href)))
print(f'PAGE_HTTP={r.status_code}')
for i,(text,url) in enumerate(found,1):
    print(f'LINK_{i}_TEXT={text}')
    print(f'LINK_{i}_URL={url}')
print(f'MATCHED_LINKS={len(found)}')
print('MODEL_SCORE_RUN=NONE')
print('DATABASE_WRITES=NONE')
