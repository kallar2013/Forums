from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from forums.items import Reply, User, Thread
from scrapy import Request
import re, json

class HUAWEISpider(CrawlSpider):
    name = 'huawei'
    allowed_domains = ['vmall.com', 'huawei.com']
    start_urls = ['http://club.huawei.com/forum.html', 
                  'http://club.huawei.com/group.php?gid=594',
                  'http://club.huawei.com/group.php?gid=595',
                  'http://club.huawei.com/group.php?gid=597',
                  ]

    rules = (
        Rule(LinkExtractor(restrict_css=('div.hfa-gls div.hfg-ldt',))),
        Rule(LinkExtractor(allow=('forum-\d+',), restrict_css=('div.bm.bmw',))),
        Rule(LinkExtractor(allow=('thread-\d+-\d+',), restrict_css=('a.s.xst', 'a.nxt')), follow=True, callback="parse_thread"),
        Rule(LinkExtractor(allow=('forum.+\.html'),restrict_xpaths=('//a[contains(text(), "下一页")]'))),
             )
    def make_user_request(self, uid):
        base = 'http://club.huawei.com/space-uid-%s.html'
        return Request(base % uid, callback=self.parse_user, meta={'uid': uid})
    
    def parse_user1(self, response):
        uid = response.meta['uid']
        user = User()
        user['uname'] = ''.join(response.css('p.cl.cardclearfix>strong>a::text').extract())
        user['uid'] = uid
        user['level'] = ''.join(response.xpath('//p[@class="cardclearfix"]/span[2]//text()').extract())
        user['posts'] = ''.join(response.css('div.card-info>p>span:nth-child(1)>a::text').extract())
        yield user
        
    def parse_user(self, response):
        uid = response.meta['uid']
        if '隐私设置，您不能访问当前内容' not in response.text:
            return Request('http://cn.club.vmall.com/space-uid-%s.html?\
            ajaxmenu=1&inajax=1&ajaxtarget=ajaxid_0.6672837195885954_menu_content' % uid, \
            callback=self.parse_user1, meta={'uid': uid})
        user = User()
        user['uid'] = uid
        level = ''.join(response.css('ul.xl.xl2.cl>li:nth-child(1)>span::text').extract())
        if not level:
            level = ''.join(response.css('ul.xl.xl2.cl>li:nth-child(2)>span>font::text').extract())
            user['register'] = ''.join(response.css('div.mtm.pbm.mbm>ul.xl.xl2.cl>li:nth-child(3)::text').extract())
            user['recent'] = ''.join(response.css('div.mtm.pbm.mbm>ul.xl.xl2.cl>li:nth-child(5)::text').extract())
        user['register'] = ''.join(response.css('div.mtm.pbm.mbm>ul.xl.xl2.cl>li:nth-child(2)::text').extract())
        user['recent'] = ''.join(response.css('div.mtm.pbm.mbm>ul.xl.xl2.cl>li:nth-child(4)::text').extract())
        user['uname'] = ''.join(response.css('p.mtm.xw1.xi2.xs2>a::text').extract())
        user['posts'] =  response.css('td.xs1>ul.pbm.mbm.bbda.cl.xl.xl2>li:nth-child(4)::text').extract()[0]
        yield user
        
    def parse_thread(self, response):
        try:
            tid, curr = re.search('thread-(\d+)-(\d+)', response.url).groups()
        except AttributeError:
            return
        cells = response.xpath('//div[@class="pl bm"]/div[@id][not(@class)]')
        if curr == '1':
            try:
                thread = Thread(tid=tid)
                temp = response.css('div.bm.cl>div.z a::text').extract()
                thread['module'] = '/'.join(temp[:-1])
                thread['title'] = temp[-1]
                thread['see'], thread['msg'] = response.css('p.pdh-misc>span::text').extract()
                main = cells[0]
                ptime = ''.join(main.xpath('.//em[starts-with(@id, "authorposton")]/span/@title').extract())
                if not ptime:
                    ptime = ''.join(main.xpath('.//em[starts-with(@id, "authorposton")]/text()').extract())
                thread['ptime'] = ptime
                thread['text'] = ''.join(main.xpath('.//td[@class="t_f"]//text()').re('[\S]+'))
                thread['img'] = ';'.join(main.xpath('.//div[@class="t_fsz"]/table//tr//img/@zoomfile').extract())
                uid = main.css('div.authi>a::attr(href)').re('uid-(\d+)')[0]
                yield self.make_user_request(uid)
                thread['uid'] = uid
                l1 = []; l2 = []; l3 = []; l4 = []; l5 = []
                for tr in main.css('tbody.ratl_l>tr'):
                    l1.append(tr.xpath('./td/a[1]/@href').re('uid-(\d+)')[0])
                    l2.append(''.join(tr.css('td:nth-child(2)::text').extract()))
                    l3.append(''.join(tr.css('td:nth-child(3)::text').extract()))
                    l4.append(''.join(tr.css('td:nth-child(4)::text').extract()))
                    l5.append(''.join(tr.css('td:nth-child(5)::text').extract()))
                thread['reviews'] = json.dumps(dict(zip(l1, zip(l2, l3, l4, l5))), ensure_ascii=False)
                yield thread
            except:
                return
            del cells[0]
        for cell in cells:
            reply = Reply(tid=tid)
            reply['uid'] = cell.css('div.authi>a::attr(href)').re('uid-(\d+)')[0]
            rtime = ''.join(cell.xpath('.//em[starts-with(@id, "authorposton")]/span/@title').extract())
            if not rtime:
                rtime = ''.join(cell.xpath('.//em[starts-with(@id, "authorposton")]/text()').extract())
            reply['rtime'] = rtime
            reply['rid'] = ''.join(cell.xpath('./@id').re('post_(\d+)'))
            reply['content'] = ''.join(cell.css('td.t_f::text').re('[\S]+'))
            temp = cell.css('div.quote>blockquote>font::text').extract()
            if temp:
                reply['reply_to'] = str([temp[0].split(' ', 1), temp[1]])
            yield reply
            
            
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
            
class XIAOMISpider(CrawlSpider):
    name = 'xiaomi'
    allowed_domains = ['xiaomi.cn',]
    start_urls = [
                 'http://city.xiaomi.cn/', # 同城会 & 板块
                 'http://bbs.xiaomi.cn/f-410', # 校园俱乐部
                 'http://bbs.xiaomi.cn/f-475',
                 'http://bbs.xiaomi.cn/f-385',
                 'http://bbs.xiaomi.cn/f-451',
                 'http://bbs.xiaomi.cn/f-458',
                 'http://bbs.xiaomi.cn/f-353',
                 'http://bbs.xiaomi.cn/f-467',
                 'http://bbs.xiaomi.cn/f-360',
                 'http://bbs.xiaomi.cn/f-361',
                 'http://bbs.xiaomi.cn/f-9',
                 'http://bbs.xiaomi.cn/f-364',
                 'http://bbs.xiaomi.cn/f-480',
                 'http://bbs.xiaomi.cn/f-354',
                 'http://bbs.xiaomi.cn/f-358',
                 'http://bbs.xiaomi.cn/f-450',
                 'http://bbs.xiaomi.cn/f-459',
                 'http://bbs.xiaomi.cn/f-362',
                 'http://bbs.xiaomi.cn/f-452',
                 'http://bbs.xiaomi.cn/f-456',
                 'http://bbs.xiaomi.cn/f-479',
                 'http://bbs.xiaomi.cn/f-368',
                 'http://bbs.xiaomi.cn/f-455',
                 'http://bbs.xiaomi.cn/f-439',
                 'http://bbs.xiaomi.cn/f-431',
                 'http://bbs.xiaomi.cn/f-379',
                 'http://bbs.xiaomi.cn/f-417',
                 'http://bbs.xiaomi.cn/f-363',
                 'http://bbs.xiaomi.cn/f-10',
                 'http://bbs.xiaomi.cn/f-454',
                 'http://bbs.xiaomi.cn/f-471',
                 'http://bbs.xiaomi.cn/f-367',
                 'http://bbs.xiaomi.cn/f-469',
                 'http://bbs.xiaomi.cn/f-457',
                 'http://bbs.xiaomi.cn/f-461',
                 'http://bbs.xiaomi.cn/f-429',
                 'http://bbs.xiaomi.cn/f-446',
                 'http://bbs.xiaomi.cn/f-390',
                 'http://bbs.xiaomi.cn/f-391',
                 'http://bbs.xiaomi.cn/f-394',
                 'http://bbs.xiaomi.cn/f-426',
                 'http://bbs.xiaomi.cn/f-410',
                 'http://bbs.xiaomi.cn/f-393',
                 'http://bbs.xiaomi.cn/f-392',
                 'http://bbs.xiaomi.cn/f-465',
                 'http://bbs.xiaomi.cn/f-472',
                 'http://bbs.xiaomi.cn/f-463',
                 'http://bbs.xiaomi.cn/f-464',
                 'http://bbs.xiaomi.cn/f-6',
                 'http://bbs.xiaomi.cn/f-389',
                 'http://bbs.xiaomi.cn/f-397',
                 'http://bbs.xiaomi.cn/f-419',
                 'http://bbs.xiaomi.cn/f-17',
                 'http://bbs.xiaomi.cn/f-473',
                 'http://bbs.xiaomi.cn/f-400',
                 'http://bbs.xiaomi.cn/f-434',
                 'http://bbs.xiaomi.cn/f-474'
                 ]
    rules = (
        #Rule(LinkExtractor(allow=('f-(\d+)'), restrict_css=('div.header_menu_list'))),
        Rule(LinkExtractor(allow=('f-\d+',), restrict_css=('div.samecity ul.clearfix'))),
        Rule(LinkExtractor(allow=('city',), restrict_css=('div.rom.box',))),
        Rule(LinkExtractor(restrict_css=('li.next'))),
        Rule(LinkExtractor(restrict_css=('div.title')), follow=False, callback='parse_thread')
    )
    
    def parse_user(self, response):
        user = User()
        user['uid'] = response.meta['uid']
        user['level'] = ''.join(response.xpath('//div[@class="score"]/dl[1]/dt/span/text()').extract())
        user['posts'] = ''.join(response.xpath('//div[@class="wrap lively"]/ul[1]/li[1]/span[2]/text()').extract())
        user['uname'] = ''.join(response.css('strong.username::text').extract())
        user['register'] = ''.join(response.xpath('//div[@class="wrap lively"]/dl/dd[5]/span/text()').extract())
        user['recent'] = ''.join(response.xpath('//div[@class="wrap lively"]/dl/dd[3]/span/text()').extract())
        yield user
        
    def make_user_request(self, uid):
        base = 'http://bbs.xiaomi.cn/u-detail-%s'
        return Request(base % uid, callback=self.parse_user, meta={'uid': uid}) 
            
    def parse_thread(self, response):
        tid, curr = re.search('t-(\d+)-*(\d*)', response.url).groups()
        if not curr:
            thread = Thread()
            thread['tid'] = re.search('t-(\d+)', response.url).groups()[0]
            thread['title'] = ''.join(response.css('div.invitation_con span.name::text').extract())
            thread['module'] = response.css('div.plateinfor>a::text').extract()[0]
            ptime = response.css('div.invitation_con p.txt>span.time::text').re('[\S]+')[0]
            if len(ptime.split('-')) == 2:
                ptime = '2017-' + ptime
            thread['ptime'] = ptime
            thread['msg'], thread['see'] = response.css('div.invitation_con p.txt>span.f_r::text').re('[\S]+')
            thread['text'] = ''.join(response.xpath('//div[@class="invitation_content"]/p/text()').re('[\S]+'))
            thread['img'] = ';'.join(response.xpath('//div[@class="invitation_content"]//img/@src').extract())
            uid = response.css('div.personLayer_msg>a::attr(href)').re('detail-(\d+)')[0]
            thread['uid'] = uid
            review_uids = response.css('div.invitation_grade tr[data-value] td.first>a::attr(u-id)').extract()
            reviews = dict(zip(review_uids, list(zip(response.css('div.invitation_grade tr[data-value] td.second::text')\
                    .re('[\S]+'), response.css('div.invitation_grade tr[data-value] td.third::text').re('[\S]+')))))
            thread['reviews'] = json.dumps(reviews, ensure_ascii=False)
            yield thread
            yield self.make_user_request(uid)
            for review_uid in review_uids:
                yield self.make_user_request(review_uid)
            
        for li in response.css('li.clearfix[post-id]'):
            reply = Reply()
            reply['rid'] = ''.join(li.xpath('./@post-id').extract())
            reply['tid'] = tid
            rtime = li.css('span.time::text').extract()[1]
            reply['rtime'] = rtime
            reply['content'] = ''.join(li.xpath('.//div[@class="reply_txt"]/p/text()').extract())
            uid = li.xpath('./@u-id').extract()[0]
            reply['reply_to'] = str([li.css('div.reply_txt>blockquote::text').extract(), \
                    ''.join(li.css('div.reply_txt>blockquote>p::text').extract())])
            reply['uid'] = uid
            yield reply
            yield self.make_user_request(uid)
        
            