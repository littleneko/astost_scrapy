# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AstostScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    tid = scrapy.Field()
    title = scrapy.Field()
    fid = scrapy.Field()
    user = scrapy.Field()
    uid = scrapy.Field()
    post_time = scrapy.Field()
    alter_time = scrapy.Field()
    content = scrapy.Field()

