# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs

import time
import pymysql.cursors

import logging


class AstostScrapyPipeline(object):

    def __init__(self):
        self.file = codecs.open('items.jl', 'wb', encoding='utf-8')
        super(AstostScrapyPipeline, self).__init__()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line.decode("unicode_escape"))
        return item


class AstostScrapyPipelineSQL(object):
    def __init__(self):
        # Connect to the database
        self.__connection = pymysql.connect(host='10.108.102.28',
                                            user='root',
                                            password='794613',
                                            db='astost2',
                                            charset='utf8',
                                            cursorclass=pymysql.cursors.DictCursor)

        self.__sql1 = "INSERT INTO `post` " \
                      "(`tid`, `fid`, `user`, `uid`, `title`, `post_time`, `alter_time`, `update_time`) " \
                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

        self.__sql2 = "INSERT INTO `post_content` " \
                      "(`tid`, `content`, `update_time`) " \
                      "VALUES (%s, %s, %s)"
        super(AstostScrapyPipelineSQL, self).__init__()

    def process_item(self, item, spider):
        try:
            with self.__connection.cursor() as cursor:
                # Create a new record
                dict_item = dict(item)
                cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                cursor.execute(self.__sql1, (dict_item['tid'], dict_item['fid'], dict_item['user'], dict_item['uid'],
                                             dict_item['title'], dict_item['post_time'], dict_item['alter_time'], cur_time))
                cursor.execute(self.__sql2, (dict_item['tid'], dict_item['content'], cur_time))
                self.__connection.commit()
        except Exception as e:
            logging.log(logging.ERROR, e)
            pass

    def close_spider(self, spider):
        self.__connection.close()
