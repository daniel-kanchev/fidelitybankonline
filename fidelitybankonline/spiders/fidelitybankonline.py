import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from fidelitybankonline.items import Article


class fidelitybankonlineSpider(scrapy.Spider):
    name = 'fidelitybankonline'
    start_urls = ['https://www.fidelitybankonline.com/our-news/']

    def parse(self, response):
        links = response.xpath('//a[@class="more-link"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[text()="›"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/a/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="heading"]/p/text()').get()
        if date:
            date = " ".join(date.split()[1:])
        else:
            return

        content = response.xpath('//div[@class="item-content"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
