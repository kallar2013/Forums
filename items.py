# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Thread(scrapy.Item):
    tid = scrapy.Field()
    title = scrapy.Field()
    see = scrapy.Field()
    msg = scrapy.Field()
    ptime = scrapy.Field()
    module = scrapy.Field()
    text = scrapy.Field()
    img = scrapy.Field()
    uid = scrapy.Field()
    
class User(scrapy.Item):
    uid = scrapy.Field()
    level = scrapy.Field()
    posts = scrapy.Field()
    uname = scrapy.Field()
    register = scrapy.Field()
    recent = scrapy.Field()
    
class Reply(scrapy.Item):
    rid = scrapy.Field()
    tid = scrapy.Field()
    rtime = scrapy.Field()
    uid = scrapy.Field()
    content = scrapy.Field()
    reply_to = scrapy.Field()
