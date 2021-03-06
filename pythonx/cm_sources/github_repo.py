
from cm import register_source, Base, getLogger
register_source(name='github-repo',
                   abbreviation='repo',
                   scopes=['gitcommit', 'markdown', 'magit'],
                   word_pattern = r'[\w.\-]+',
                   cm_refresh_length=-1,
                   cm_refresh_patterns=[r'\b(\w+)\/'],
                   priority=9)

from urllib.request import urlopen
from urllib.parse import urlencode
import json
import re

logger = getLogger(__name__)

class Source(Base):

    def __init__(self, nvim):
        Base.__init__(self, nvim)

    def cm_refresh(self, info, ctx):

        typed = ctx['typed']
        base = ctx['base']
        txt = typed[0 : len(typed)-len(base)]

        # `.*` greedy match, push to the the end
        match = re.search(r'.*\b(\w+)\/$', txt)
        if not match:
            logger.debug("match user string failed")
            return

        user = match.group(1)
        query = {
                'q': ctx['base'] + ' in:name user:' + user,
                'sort': 'stars',
                }

        url = 'https://api.github.com/search/repositories?' + urlencode(query)
        logger.debug("url: %s", url)

        matches = []
        with urlopen(url, timeout=30) as f:
            rsp = f.read()
            logger.debug("rsp: %s", rsp)
            rsp = json.loads(rsp.decode())
            for item in rsp['items']:
                matches.append(dict(word=item['name'], menu=item['full_name']))

        logger.debug("matches: %s", matches)
        self.complete(info, ctx, ctx['startcol'], matches, refresh=rsp['incomplete_results'])

