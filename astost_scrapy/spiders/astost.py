# -*- coding: utf-8 -*-

import re

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http.request import Request

from astost_scrapy.items import AstostScrapyItem


class AstostSpider(CrawlSpider):
    name = 'astost'
    allowed_domains = ['astost.com']
    start_urls = ['https://www.astost.com/bbs/']

    rules = (
        Rule(LinkExtractor(allow=r'thread.php\?fid=(53|52|50|4|5|42|8|49)(&page=\d+)?$'), follow=True,
             process_request='process_request'),
        Rule(LinkExtractor(allow=r'read.php\?tid=\d+(&fpage=\d+)?$'), callback='parse_item',
             process_request='process_request'),
    )

    def __init__(self, *a, **kw):
        self.__headers = {'Connection': 'keep-alive',
                          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                          'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.6,ja;q=0.4,en;q=0.2',
                          'Accept-Encoding': 'gzip, deflate, sdch, br',
                          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
                                        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
                          }

        self.__cookies = {'0cc61_winduser': 'xxxxxxxxxx'}
        self.__pattern_tid = re.compile(r'.*tid=(\d+)')
        self.__pattern_url = re.compile(r'&?fpage=\d+&?')
        self.__pattern_time = re.compile(r'\d{,4}-[01]\d-[0123]\d\s{1,2}[012]\d:[0-6]\d')
        self.__pattern_uid = re.compile(r'.*uid=(\d+)')
        super(AstostSpider, self).__init__(*a, **kw)

    def parse_item(self, response):
        item = AstostScrapyItem()

        title = response.xpath('//*[@id="main"]/div[1]/table/tr/td/a[3]/text()').extract()
        fid = response.xpath('//*[@id="main"]/div[1]/table/tr/td/a[2]/text()').extract()
        user = response.xpath('//*[@id="main"]/form[1]/div[2]/table/tr[1]/th[1]/b/text()').extract()
        uid = response.xpath('//*[@id="main"]/form[1]/div[2]/table/tr[1]/th[1]/div[2]/table/tr/td[1]/'
                             'a[contains(@href, "uid")]/@href').extract()
        post_time = response.xpath('/html/body/div[@id="wrapA"]/div[@id="main"]/form[1]/div[@class="t t2"][1]/table/'
                                   'tr[@class="tr1 r_one"]/th/div[@class="tipad"]/span[@class="gray"]/text()').extract()
        alter_time = response.xpath('//*[@id="alert_tpc"]/text()').extract()
        content = response.xpath('//*[@id="read_tpc"]').extract()

        tid = self.__pattern_tid.search(response.url)
        item['tid'] = tid.group(1) if tid else ""

        item['title'] = "".join(title)
        item['fid'] = "".join(fid)
        item['user'] = "".join(user)

        uid = self.__pattern_uid.search("".join(uid))
        item['uid'] = uid.group(1) if uid else "0"

        post_time = self.__pattern_time.search("".join(post_time))
        item['post_time'] = post_time.group() if post_time else "1970-01-01 00:00:00"

        alter_time = self.__pattern_time.search("".join(alter_time))
        item['alter_time'] = alter_time.group() if alter_time else "1970-01-01 00:00:00"

        item['content'] = "".join(content)

        return item

    def process_request(self, request):
        url = self.__pattern_url.sub('', request.url)
        request = request.replace(url=url, cookies=self.__cookies, headers=self.__headers)
        return request

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, cookies=self.__cookies, headers=self.__headers)
