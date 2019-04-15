# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy.http import Request
from zhihuuser.items import UserItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['zhihu.com']
    start_urls = ['http://zhihu.com/']
    start_user = "excited-vczh"
    # 个人账号页面url#
    user_url = "https://www.zhihu.com/api/v4/members/{user}?include={user_query}"
    user_query = "allow_message%2Cis_followed%2Cis_following%2Cis_org%2Cis_blocking%2Cemployments%2Canswer_count%2Cfollower_count%2Carticles_count%2Cgender%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics"
    # 关注的列表url#
    follows_url = "https://www.zhihu.com/api/v4/members/{user}/followees?include={follows_query}&offset={offset}&limit={limit}"
    follows_query = "data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics"
    # 被关注的列表#
    followers_url = "https://www.zhihu.com/api/v4/members/{user}/followers?include={followers_query}&offset={offset}&limit={limit}"
    followers_query = "data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics"

    def start_requests(self):
        yield Request(url=self.follows_url.format(user=self.start_user, follows_query=self.follows_query, offset=0, limit=20),callback=self.parse_follows)
        yield Request(url=self.user_url.format(user=self.start_user, user_query=self.user_query),callback=self.parse_user)
        yield Request(url=self.followers_url.format(user=self.start_user, followers_query=self.followers_query, offset=0,limit=20),callback=self.parse_followers)

    def parse_user(self, response):
        res = json.loads(response.text)
        item = UserItem()
        for field in item.fields:
            if field in res.keys():
                item[field] = res.get(field)
        print(item)
        yield item
        yield Request(
            url=self.follows_url.format(user=item["url_token"], follows_query=self.follows_query, limit=20, offset=0),
            callback=self.parse_follows)

    def parse_follows(self, response):
        res = json.loads(response.text)
        if "data" in res.keys():
            for item in res["data"]:
                yield Request(url=self.user_url.format(user=item["url_token"], user_query=self.user_query),
                              callback=self.parse_user)
        if "paging" in res.keys() and res.get("paging").get("is_end") == False:
            page = res.get("paging").get("next")
            next_page = page.split("com")[0] + "com/api/v4" + page.split("com")[1]
            yield Request(url=next_page, callback=self.parse_follows)

    def parse_followers(self, response):
        res = json.loads(response.text)
        if "data" in res.keys():
            for item in res["data"]:
                yield Request(url=self.user_url.format(user=item["url_token"], user_query=self.user_query),
                              callback=self.parse_user)
        if "paging" in res.keys() and res.get("paging").get("is_end") == False:
            page = res.get("paging").get("next")
            next_page = page.split("com")[0] + "com/api/v4" + page.split("com")[1]
            yield Request(url=next_page, callback=self.parse_followers)
