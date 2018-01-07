# -*- coding: utf-8 -*-
import scrapy
from amazon.items import MonitorItem


class BestsellersCatSpider(scrapy.Spider):
    name = "driveway_maker"
    allowed_domains = ["amazon.com"]
    start_urls = [
        'https://www.amazon.com/s/ref=nb_sb_ss_c_1_4?url=search-alias%3Daps&field-keywords=driveway+markers'
    ]

    def parse(self, response):
        sel_div = response.xpath(
            '''//div[@id="resultsCol"]//li//a[@class="a-link-normal s-access-detail-page  s-color-twister-title-link a-text-normal"]''')
        for sel in sel_div:
            title = sel.xpath('@title').extract()
            link = sel.xpath('@href').extract()
            url = response.urljoin(link[0])
            yield scrapy.Request(url, callback=self.get_details, meta={'title': title[0], 'link': link[0]}, dont_filter=True)

        page_cur = response.xpath('//span[@class="pagnCur"]/text()').extract()
        next_href = response.xpath('//a[@title="Next Page"]/@href').extract()
        print "page_cur: ----------------------------%s------------------------------" % page_cur
        print "next_href: ------------%s------------" % next_href
        if next_href:
            next_url = response.urljoin(next_href[0])
            yield scrapy.Request(next_url, callback=self.parse, dont_filter=True)


    def get_details(self, response):
        pack_price = response.xpath('//span[@id="priceblock_ourprice"]/text()').extract()
        if not pack_price:
            pack_price_list = response.xpath('//form[@id="twister"]//li')
            for single in pack_price_list:
                pack_price.append({'package_quantity':single.xpath('span//div[@class="twisterTextDiv text"]/span/text()').extract(),
                                   'package_price': single.xpath('span//div[@class="twisterSlotDiv"]/span//span/text()').extract()})
        details = response.xpath('//table[@id="productDetails_detailBullets_sections1"]//tr')
        customer_review = ''
        best_seller = ''
        for info in details:
            if info.xpath('th/text()').extract()[0].strip() == 'Customer Reviews':
                customer_review = info.xpath('td/text()').extract()[-1].strip()
            if info.xpath('th/text()').extract()[0].strip() == 'Best Sellers Rank':
                best_seller = info.xpath('td/span/span[1]/text()').extract()[0].split('(')[0]
        new = 'New' + response.xpath('//div[@id="olp_feature_div"]//span[1]/a/text()').extract()[0]
        monitor_item = MonitorItem()
        monitor_item['title'] = response.meta['title']
        monitor_item['link'] = response.meta['link']
        monitor_item['price'] = pack_price
        monitor_item['review'] = customer_review
        monitor_item['ranking'] = best_seller
        monitor_item['with_pedlar'] = new

        yield monitor_item

