"""Graphics per chapter for build.py. Synthetic example: write the real one in <project>/edit/specs.py.

Anchors are (speaker, "exact phrase from the transcript", raw_seconds_to_search_after); speaker 'h' = host,
'g' = guest. 'at' starts a card, 'end' ends it on that word's end (+ 'tail', default 0.4s; 'lead' default -0.2s).
shot 'B' = card with the two anchors shrunk to a picture-in-picture column; 'C' = full-frame card.
Facts on cards: the guest's own words (attributed "on this episode") or a source you have READ and dated.
Anything inside a quote card must be verbatim (ellipses allowed); paraphrase goes on non-quote cards.
"""
EP = 'Jane Doe, on this episode'
LT_G = dict(who='g', k='Guest', n='Jane Doe', t='Founder & CEO, Example Rights Co', dur=6.5)
LT_H = dict(who='h', k='Host', n='Patrick Sweetman', t='Cofounder, Recoup', dur=6.0)

SPECS = {
'ch00': {'no_chapter': True, 'ticker': ['Recoup Podcast · Royalty statements will reconcile themselves'],
         'lower_thirds': [dict(LT_G, k='Coming up', at=('g', 'the statement is the product', 1170), dur=8.0)], 'cards': []},
'ch01': {
  'ticker': ['Example Trade Weekly · Statement formats survey · Sep 2026', 'Example Rights Co · example.com'],
  'lower_thirds': [dict(LT_H, at=('h', 'Today', 0)), dict(LT_G, at=('g', 'Thanks for having me', 10))],
  'cards': [
    dict(type='headline', shot='C', at=('h', 'last month a survey', 20), end=('h', 'formats', 30),
         src='Example Trade Weekly', meta='September 2026', h='Most publishers still receive statements in 40+ formats',
         p='One line summarising the article you read.', foot=['example.com', 'Survey of 120 publishers'], stamp=('Survey', '40+', 'formats')),
    dict(type='list', shot='B', at=('g', 'there are four things', 60), end=('g', 'and that is it.', 60),
         src='What breaks', meta=EP, h='Where statement data goes wrong', items=['Titles', 'Splits', 'ISRCs', 'Territories']),
    dict(type='stat', shot='B', at=('g', 'about thirty percent', 90), end=('g', 'never claimed', 90),
         src='Unclaimed', meta=EP, num='30%', unit='of lines never matched', left='Received', right='Paid', q='"We just <em>never claimed</em> it."'),
    dict(type='versus', shot='B', at=('g', 'used to take a week', 120), end=('g', 'an afternoon', 120),
         src='Then vs now', meta=EP, a=('Then', 'A week', 'Manual matching in spreadsheets.'), b=('Now', 'An afternoon', 'An agent drafts, a person approves.')),
    dict(type='tline', shot='B', at=('h', 'walk me through', 150), end=('g', 'live in March', 150),
         src='Timeline', meta=EP, h='How the rollout went', rows=[('Jan', 'Pilot on one catalog', False), ('Feb', 'Second catalog', False), ('Mar', 'Live', True)]),
    dict(type='quote', shot='C', at=('g', 'the statement is the product', 1170), end=('g', 'product', 1170), tail=1.0,
         src='Jane Doe', meta='On this episode', q='The statement <em>is</em> the product.'),
  ]},
}
