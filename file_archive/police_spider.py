import scrapy

class PoliceReport(scrapy.Item):
    link = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    location = scrapy.Field()
    event = scrapy.Field()

class PoliceReportsSpider(scrapy.Spider):
    name = "police_reports_spider"
    allowed_domains = ['berlin.de']
    start_urls = [
        'https://www.berlin.de/polizei/polizeimeldungen/archiv/2025/?page_at_1_0=1'
    ]
    BASE_URL = 'https://www.berlin.de'

    def parse(self, response):
        articles = response.css("li")

        for article in articles:
            relative_link = article.css("div.cell.text a::attr(href)").get()
            if relative_link:
                absolute_link = response.urljoin(relative_link)
                yield scrapy.Request(absolute_link, callback=self.parse_report)

        # Szukanie kolejnej strony
        next_page = response.css("ul.pagination li.next a::attr(href)").get()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def parse_report(self, response):
        item = PoliceReport()
        item["link"] = response.url
        item["title"] = response.css("h1.title::text").get().strip()

        # Data (pierwszy .polizeimeldung)
        item["date"] = response.css("div.polizeimeldung::text").re_first(r"\d{2}\.\d{2}\.\d{4}")

        # Lokalizacja (jeśli występuje w <strong>)
        location = response.css("p strong::text").get()
        item["location"] = location.strip() if location else ""

        # Treść zdarzenia (wszystkie paragrafy)
        paragraphs = response.css("div.textile p::text").getall()
        clean_paragraphs = [p.strip() for p in paragraphs if p.strip()]
        item["event"] = " ".join(clean_paragraphs)

        yield item
