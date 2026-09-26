#!/usr/bin/env python3
"""Check explicit public copy paths. Human clarity and cover review remain required."""
import argparse,json,re
from pathlib import Path
from html.parser import HTMLParser

DEFAULT_TERMS=['Music Fastball','Music Moneyball','Music Moneyball Fastball']
class VisibleHTML(HTMLParser):
    def __init__(self): super().__init__(); self.hidden=0; self.parts=[]
    def handle_starttag(self, tag, attrs):
        if tag in ('style','script'): self.hidden+=1
        self.parts += [v for k,v in attrs if k in ('alt','title') and v]
    def handle_endtag(self, tag):
        if tag in ('style','script'): self.hidden=max(0,self.hidden-1)
    def handle_data(self,data):
        if not self.hidden: self.parts.append(data)

def public_text(text,suffix):
    if suffix in ('.html','.svg'):
        parser=VisibleHTML();parser.feed(text);return ' '.join(parser.parts)
    if text.startswith('---\n'):
        parts=text.split('---',2)
        if len(parts)==3:
            # Titles and subjects are public; provenance and approval data are not.
            front='\n'.join(line for line in parts[1].splitlines() if re.match(r'^(title|subject|hook):',line))
            text=front+'\n'+parts[2]
    return text

def check(path,terms):
    text=public_text(path.read_text(),path.suffix)
    flags=[]
    for term in terms:
        if re.search(r'(?<!\w)'+re.escape(term)+r'(?!\w)',text,re.I): flags.append('excluded-reference: '+term)
    if re.search(r'(?:clients|pipeline|integrations|signals)/[^\s)]+',text): flags.append('private-source-path')
    # Diagnostics deliberately do not certify readability or fail publication alone.
    long_sentences=sum(len(s.split())>40 for s in re.split(r'(?<=[.!?])\s+',text))
    return {'file':str(path),'blocking_flags':flags,'long_sentences_over_40_words':long_sentences,'manual_review_required':['plain-language','claim-attribution','cover-comprehension-if-present']}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files',nargs='+',type=Path)
    parser.add_argument('--policy',type=Path,help='JSON with additional excluded_public_names list')
    args=parser.parse_args()
    terms=DEFAULT_TERMS[:]
    if args.policy: terms+=json.loads(args.policy.read_text()).get('excluded_public_names',[])
    results=[check(p,terms) for p in args.files]
    print(json.dumps(results,indent=2))
    return int(any(r['blocking_flags'] for r in results))
if __name__=='__main__': raise SystemExit(main())
