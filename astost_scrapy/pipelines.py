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

from conf import config


class AstostScrapyPipeline(object):

    def __init__(self):
        self.file = codecs.open('items.jl', 'wb', encoding='utf-8')
        super(AstostScrapyPipeline, self).__init__()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line.decode("unicode_escape"))
        return item


class AstostScrapyPipelineSQL(object):
    """
    mysql> show create table post\G
    *************************** 1. row ***************************
           Table: post
    Create Table: CREATE TABLE `post` (
      `tid` int(11) NOT NULL DEFAULT '0' COMMENT '帖子ID',
      `fid` varchar(20) NOT NULL DEFAULT '' COMMENT '帖子所属分区ID',
      `user` varchar(20) NOT NULL DEFAULT '' COMMENT '发帖人名称',
      `uid` int(11) NOT NULL DEFAULT '0' COMMENT '发帖人UID',
      `title` varchar(255) NOT NULL DEFAULT '' COMMENT '帖子标题',
      `post_time` datetime NOT NULL DEFAULT '1970-01-01 00:00:00' COMMENT '帖子发布时间',
      `alter_time` datetime NOT NULL DEFAULT '1970-01-01 00:00:00' COMMENT '帖子更新时间',
      `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
      `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
      PRIMARY KEY (`tid`),
      KEY `idx_up_time` (`update_time`),
      KEY `idx_post_time` (`post_time`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8

    mysql> show create table post_content\G
    *************************** 1. row ***************************
           Table: post_content
    Create Table: CREATE TABLE `post_content` (
      `tid` int(11) NOT NULL DEFAULT '0' COMMENT '帖子ID',
      `content` mediumtext COMMENT '帖子内容',
      `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
      `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
      PRIMARY KEY (`tid`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    """

    def __init__(self):
        # Connect to the database
        self.__connection = pymysql.connect(host=config.DB_HOST,
                                            user=config.DB_USER,
                                            password=config.DB_PASS,
                                            db=config.DB_NAME,
                                            charset='utf8',
                                            cursorclass=pymysql.cursors.DictCursor)

        self.__sql1 = "INSERT INTO `post` " \
                      "(`tid`, `fid`, `user`, `uid`, `title`, `post_time`, `alter_time`, `create_time`) " \
                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)" \
                      "ON DUPLICATE KEY UPDATE `title` = %s, `alter_time` = %s"

        self.__sql2 = "INSERT INTO `post_content` " \
                      "(`tid`, `content`, `create_time`) " \
                      "VALUES (%s, %s, %s)" \
                      "ON DUPLICATE KEY UPDATE `content` = %s"
        super(AstostScrapyPipelineSQL, self).__init__()

    def process_item(self, item, spider):
        try:
            with self.__connection.cursor() as cursor:
                # Create a new record
                dict_item = dict(item)
                cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                cursor.execute(self.__sql1, (dict_item['tid'], dict_item['fid'], dict_item['user'], dict_item['uid'],
                                             dict_item['title'], dict_item['post_time'], dict_item['alter_time'],
                                             cur_time, dict_item['title'], dict_item['alter_time']))
                cursor.execute(self.__sql2, (dict_item['tid'], dict_item['content'], cur_time, dict_item['content']))
                self.__connection.commit()
        except Exception as e:
            logging.log(logging.ERROR, e)
            pass

    def close_spider(self, spider):
        self.__connection.close()
