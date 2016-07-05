# -*- coding: utf-8 -*-

import re

from scrapy.dupefilters import RFPDupeFilter


class AstostUrlFilter(RFPDupeFilter):

    def __init__(self, path=None, debug=False):
        self.pattern = re.compile(r'&?fpage=\d+&?')
        super(AstostUrlFilter, self).__init__(path, debug)

    def _get_id(self, url):
        return self.pattern.sub('', url)

    def request_fingerprint(self, request):
        style_id = self._get_id(request.url)
        return style_id

