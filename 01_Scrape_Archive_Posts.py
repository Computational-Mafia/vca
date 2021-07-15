# %% [markdown]
# ## Scrape Archived Mini Normals from Mafiascum.net

# %% [markdown]
# #### Scrapy Structure/Lingo:
# **Spiders** extract data **items**, which Scrapy send one by one to a configured **item pipeline** (if there is possible) to do post-processing on the items.)

# %% [markdown]
# ## Import relevant packages...

# %%
import scrapy
import math
import logging
import json
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.item import Item, Field
from scrapy.selector import Selector
from tqdm import tqdm
import os

# %% [markdown]
# ## Initial variables...

# %%
perpage = 25

class PostItem(scrapy.Item):
    pagelink = scrapy.Field()
    forum = scrapy.Field()
    thread = scrapy.Field()
    number = scrapy.Field()
    timestamp = scrapy.Field()
    user = scrapy.Field()
    content = scrapy.Field()


# %% [markdown]
# ## Define what happens to scrape output...

# %%
# The following pipeline stores all scraped items (from all spiders) 
# into a single items.jl file, containing one item per line serialized 
# in JSON format:
class JsonWriterPipeline(object):

    # operations performed when spider starts
    def open_spider(self, spider):
        self.file = open('data/posts.jsonl', 'w')

    # when the spider finishes
    def close_spider(self, spider):
        self.file.close()

    # when the spider yields an item
    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


# %% [markdown]
# ## Define spider...

# %%
class MafiaScumSpider(scrapy.Spider):
    name = 'mafiascum'
     
    # settings
    custom_settings = {'LOG_LEVEL': logging.WARNING,
                      'ITEM_PIPELINES': {'__main__.JsonWriterPipeline': 1}}
    
    def start_requests(self):
        
        # define set of threads we're going to scrape from (ie all of them)
        urls = [each[:each.find('\n')] for each in open('data/archive.txt').read().split('\n\n\n')]
        for url in tqdm(urls):
            yield scrapy.Request(url=url, callback=self.parse)

    # get page counts and then do the REAL parse on every single page
    def parse(self, response):
        # find page count 
        try:
            postcount = Selector(response).xpath(
                '//div[@class="pagination"]/text()').extract()
            postcount = int(postcount[0][4:postcount[0].find(' ')])

            # yield parse for every page of thread
            for i in range(math.ceil(postcount/perpage)):
                yield scrapy.Request(response.url+'&start='+str(i*perpage),
                                    callback=self.parse_page)
        except IndexError: # if can't, the thread probably doesn't exist
            return
        
        
    def parse_page(self, response):
        # scan through posts on page and yield Post items for each
        sel = Selector(response)
        location = sel.xpath('//div[@id="page-body"]/h2/a/@href').extract()[0]
        forum = location[location.find('f=')+2:location.find('&t=')]
        if location.count('&') == 1:
            thread = location[location.find('&t=')+3:]
        elif location.count('&') == 2:
            thread = location[
                location.find('&t=')+3:location.rfind('&')]
        
        posts = (sel.xpath('//div[@class="post bg1"]') +
                 sel.xpath('//div[@class="post bg2"]'))
        
        for p in posts:
            post = PostItem()
            post['forum'] = forum
            post['thread'] = thread
            post['pagelink'] = response.url
            try:
                post['number'] = p.xpath(
                    'div/div[@class="postbody"]/p/a[2]/strong/text()').extract()[0][1:]
            except IndexError:
                post['number'] = p.xpath(
                    'div[@class="postbody"]/p/a[2]/strong/text()').extract()[0][1:]
            
            try:
                post['timestamp'] = p.xpath(
                    'div/div/p/text()[4]').extract()[0][23:-4]
            except IndexError:
                post['timestamp'] = p.xpath(
                    'div[@class="postbody"]/p/text()[4]').extract()[0][23:-4]
            
            try:
                post['user'] = p.xpath('div/div/dl/dt/a/text()').extract()[0]
            except IndexError:
                post['user'] = '<<DELETED_USER>>'
                
            try:
                post['content'] = p.xpath(
                    'div/div/div[@class="content"]').extract()[0][21:-6]
            except IndexError:
                post['content'] = p.xpath(
                    'div[@class="postbody"]/div[@class="content"]').extract()[0][21:-6]
            
            yield post

# %% [markdown]
# ## Start scraping...

# %%
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(MafiaScumSpider)
process.start()
print('done!')

# %% [markdown]
# ...and output should be a json file in same directory as this notebook! 

# %% [markdown]
# ## Separate Results into Unique Files

# %%
posts = open('data/posts.jsonl')
for post in posts:
    with open('data/posts/{}.jsonl'.format(json.loads(post)['thread']), 'a') as f:
        f.write(post)

# %% [markdown]
# ## Clean Up Results
# Remove duplicate entries and sort by post number for every scraped game.

# %%
# loop through every file in directory
for path, subdirs, files in os.walk('data/posts'):
    for name in files:
        
        # don't consider non-jsonl files
        if name[-5:] != 'jsonl':
            continue
            
        # load as dictionary, remove redundancies, and sort by post number
        with open('data/posts/{}'.format(name)) as f:
            gameposts = [dict(t) for t in {tuple(d.items()) for d in [json.loads(l) for l in f]}]
            gameposts = sorted(gameposts, key=lambda x: (int(x['thread']), int(x['number'])))
        
        # save result
        with open('data/posts/{}'.format(name), 'w') as f:
            f.write('\n'.join([json.dumps(post) for post in gameposts]))

# %%
