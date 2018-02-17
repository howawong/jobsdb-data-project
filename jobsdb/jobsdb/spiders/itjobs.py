# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from bs4 import BeautifulSoup

class ItjobsSpider(scrapy.Spider):
    name = "itjobs"
    allowed_domains = ["hk.jobsdb.com"]
    start_urls = ["https://hk.jobsdb.com/hk/jobs/information-technology/%d" % i for i in range(1, 136)]

    def parse(self, response):
        soup = BeautifulSoup(response.body, "html.parser")
        job_links = soup.find_all("a", {"class": "posLink"})
        for link in job_links:
            #print(link["href"])
            yield Request(link["href"], callback=self.parse_detail)

    def parse_detail(self, response):
        soup = BeautifulSoup(response.body, "html.parser")
        title = ""
        try:
            title = soup.find("h1", {"itemprop": "title"}).text.strip()
        except Exception as e:
            #Retry
            yield Request(response.url, callback=self.parse_detail)
            return
        company = ""
        url = response.url
        try:
            company = soup.find("h2", {"class": "jobad-header-company"}).text.strip()
        except Exception as e:
            print(url)
            print(e)

        description = soup.find("div", {"itemprop": "responsibilities"}).text.strip()
        meta_container = soup.find("div", {"class": lambda x: x is not None and x.find("jobad-primary-meta") >= 0 })
        #print(description)
        #print(url)
        #print(company)
        meta = {}
        for row in meta_container.find_all("div"):
            children = list(row.findChildren())
            meta_type = children[0].text.strip()
            meta_value = ""
            if meta_type == "Benefits":
                meta_value = [s.text.strip() for s in children[1].find_all("span")]
            else:
                meta_value = [children[1].text.strip()]
            meta[meta_type] = meta_value
        yield {"title": title, "company": company, "url": url, "description": description, "meta": meta}
            
