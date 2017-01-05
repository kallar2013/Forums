# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from forums.items import Reply, User, Thread
from scrapy.exceptions import DropItem
import sqlite3

class ForumsPipeline(object):

    def open_spider(self, spider):
        self.conn = sqlite3.connect('forums.db')
        self.conn.text_factory = str
        self.cur = self.conn.cursor()
        
    def close_spider(self, spider):
        self.conn.close()
    def handle_reply(self, item):
        str_tag = ['rid', 'rtime', 'uid', 'content', 'reply_to', 'tid']
        qmark = ','.join(len(str_tag) * ['?'])
        cols = '"' + '","'.join(str_tag) + '"'
        sql = 'INSERT INTO replies (%s) VALUES (%s)' % (cols, qmark)
        data = [item.get(x, '') for x in str_tag]
        self.cur.execute(sql, data)
        self.conn.commit()
        
    def handle_user(self, item):
        str_tag = ['uid', 'level', 'posts', 'uname', 'register', 'recent']
        qmark = ','.join(len(str_tag) * ['?'])
        cols = '"' + '","'.join(str_tag) + '"'
        sql = 'INSERT INTO users (%s) VALUES (%s)' % (cols, qmark)
        data = [item.get(x, '') for x in str_tag]
        self.cur.execute(sql, data)
        self.conn.commit()
    
    def handle_thread(self, item):
        str_tag = ['tid', 'title', 'see', 'msg', 'ptime', 'module', 'text', 'img', 'uid']
        qmark = ','.join(len(str_tag) * ['?'])
        cols = '"' + '","'.join(str_tag) + '"'
        sql = 'INSERT INTO threads (%s) VALUES (%s)' % (cols, qmark)
        data = [item.get(x, '') for x in str_tag]
        self.cur.execute(sql, data)
        self.conn.commit()
        
    def process_item(self, item, spider):
        if isinstance(item, Reply):
            self.handle_reply(item)
        elif isinstance(item, User):
            self.handle_user(item)
        elif isinstance(item, Thread):
            self.handle_thread(item)
        else:
            DropItem
        return item