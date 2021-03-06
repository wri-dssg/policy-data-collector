import scrapy
import json
import datetime
from scrapy_official_newspapers.items import ScrapyOfficialNewspapersItem
from scrapy_official_newspapers.spiders import BaseSpider

class USFR(BaseSpider):
    name = "USFR"
    country = "USA"
    country_code = "US" # You can find the ISO3166 country code here: https://gist.github.com/ssskip/5a94bfcd2835bf1dea52
    state_name = "Federal"
    satate_code = "" # As per the Holidays package, you can find the code here https://pypi.org/project/holidays/ if avaiable.
    source = "Federal Register"
    spider_builder = "Jordi Planas"
    scrapable = "True"
    allowed_domains = ["api.govinfo.gov"]
    start_date = "2021-01-01"
    # API_key_file = 'C:/Users/user/Google Drive/Els_meus_documents/projectes/CompetitiveIntelligence/WRI/Notebooks/credentials/us_gov_api_key.json'
    API_key_file = '/home/propietari/Documents/claus/us_gov_api_key.json'

    def __init__(self):
        # First we import the two dictionaries that we are going to use to filter the policies.
        self.keyword_dict = self.import_json('./keywords_and_dictionaries/keywords_knowledge_domain_EN.json')
        self.negative_keyword_dict = self.import_json('./keywords_and_dictionaries/negative_keywords_knowledge_domain_EN.json')
        # We upload the credentials to access the API
        self.API_key = self.import_json(self.API_key_file)["us gov apikey jp"]
        # This is to set the time span variables. 
        self.from_date, self.today = self.create_date_span(self.start_date)
    
    def start_requests(self):
        for day in self.create_date_list(self.from_date, self.today, 1, "days", self.country_code):
            #print(day)
            start_url = f'https://api.govinfo.gov/packages/FR-{day}/granules?offset=0&pageSize=300&api_key={self.API_key}'
            #print(start_urls)
            yield scrapy.Request(start_url, dont_filter=True, callback=self.parse)

    def parse(self, response):
        for granule in json.loads(response.text)["granules"]:
            url = granule["granuleLink"] + f'?api_key={self.API_key}'
            self.debug(url)
            yield scrapy.Request(url, dont_filter=True, callback=self.parse_other)

    def parse_other(self, response):
        summary_full = response.json()
        #self.debug(summary_full)
        title = summary_full["title"]
        if "summary" in summary_full:
            summary = summary_full["summary"]
        else:
            summary = ""
        text_to_search = summary_full["title"] + " " + summary
        if self.search_keywords(text_to_search, self.keyword_dict, self.negative_keyword_dict):
            item = ScrapyOfficialNewspapersItem()
            item['country'] = self.country
            item['state'] = self.state_name
            item['data_source'] = self.source
            item['law_class'] = summary_full['category']
            item['title'] = summary_full['title']
            item['reference'] = summary_full['granuleId']
            item['authorship'] = summary_full['agencies'][0]['name']
            item['summary'] = summary
            item['publication_date'] = summary_full['dateIssued']
            item['url'] = summary_full['download']['txtLink'].replace('htm', 'summary?api_key=')
            item['doc_url'] = summary_full['download']['txtLink'] + '?api_key='
            item['doc_name'] = self.HSA1_encoding(summary_full['download']['txtLink'] + f'?api_key={self.API_key}')

            yield item




