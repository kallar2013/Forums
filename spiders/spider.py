from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from forums.items import Reply, User, Thread
from scrapy import Request
import re

class CNMOSpier(CrawlSpider):
    name = 'cnmo'
    allowed_domains = ['cnmo.com',]
    start_urls = ['http://bbs.cnmo.com/forum-16049-1.html', 
                  'http://bbs.cnmo.com/forum-2139-1.html',
                  'http://bbs.cnmo.com/forum-16048-1.html',
                  'http://bbs.cnmo.com/forum-16046-1.html',
                  'http://bbs.cnmo.com/forum-1772-1.html',
                  'http://bbs.cnmo.com/forum-16292-1.html',
                  'http://bbs.cnmo.com/forum-16050-1.html',
                  'http://bbs.cnmo.com/forum-2136-1.html'
                  ]
    rules = (
         Rule(LinkExtractor(allow=('thread'), restrict_css=('div.wrap2.feaList')), follow=True, callback='parse_thread'),
         Rule(LinkExtractor(restrict_css=('div.List-pages.fr>a[title]')), follow=True, callback='parse_thread'),
         Rule(LinkExtractor(allow=('forum'), restrict_xpaths=('//div[@class="pagebox mt20"]/a[@title="下一页"]'))),
         )
    uids = set()           
    
    def parse_user(self, response):
        user = User()
        user['uid'] = response.meta['uid']
        user['uname'] = ''.join(response.css('p.per-infotit>strong::text').extract())
        user['level'] = ''.join(response.css('span.level::text').extract())
        user['posts'] = response.css('a.num::text').extract()[0]
        user['register'], user['recent'] = response.css('ul.list.fr span.date::text').extract()
        yield user
        
    def make_user_request(self, uid):
        base = 'http://i.cnmo.com/space-uid-%s.html'
        if uid not in self.uids:
            return Request(base % uid, callback=self.parse_user, meta={'uid': uid})
            
    def parse_thread(self, response):
        tid, curr = re.search('thread-(\d+)-(\d+)',response.url).groups()
        if curr == '1':
            thread = Thread()
            thread['tid'] = tid
            thread['title'] = ''.join(response.css('div.topicNav>h2>a::text').extract())
            thread['see'] = ''.join(response.css('span[id="publish_views"]::text').extract())
            thread['msg'] = ''.join(response.css('span[id="publish_replies"]::text').extract())
            thread['ptime'] = ''.join(response.css('span[id="publish_at"]::text').extract())
            thread['module'] = '/'.join(response.css('div.C1000.crumbs a::text').extract()[:3])
            thread['text'] = ''.join(''.join(response.xpath('//div[@class="bbs_Div"]//text()').extract()))
            thread['img'] = ';'.join(response.css('div.bbs_Div img::attr(lazy_img)').extract())
            tuid = response.css('#post_list > div:nth-child(1) > dl > dt > a::attr(href)').re('uid-(\d+)')[0]
            thread['uid'] = tuid
            yield thread
            yield self.make_user_request(tuid)
        for div in response.css('div.topic-con[id]'):
            reply = Reply()
            reply['rid'] = ''.join(div.xpath('./@id').re('post-list-(\d+)'))
            reply['tid'] = tid
            uid = ''.join(div.css('dl.fl.topic-conL>dt>a::attr(href)').re('uid-(\d+)'))
            reply['uid'] = uid
            reply['rtime'] = ''.join(div.css('div.sofa>span::text').extract())
            reply['content'] = ''.join(div.xpath('.//div[@class="R-txt"]/p//text()').extract())
            yield reply
            yield self.make_user_request(uid)