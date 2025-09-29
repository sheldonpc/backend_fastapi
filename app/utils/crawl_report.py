import asyncio
import os
import re
import requests
from fake_useragent import UserAgent
from lxml import etree


async def crawl_report_func(url):
    headers = {
        "User-Agent": UserAgent().random,
    }

    session = requests.Session()
    response = session.get(url, headers=headers)

    file_name = "temp_early_report.html"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(response.text)

    await asyncio.sleep(2)

    parser = etree.HTMLParser()
    tree = etree.parse(file_name, parser)
    raw_texts = tree.xpath('//*[@id="ContentBody"]//text()')

    full_text = ''.join(raw_texts)
    full_text = full_text.strip()
    full_text = full_text.replace('\u3000', ' ')

    full_text = re.sub(r'\s+', '', full_text)
    sentences = re.split(r'(?<=[。！？])\s+', full_text)

    sentences = [s.strip() for s in sentences if s.strip()]
    result = ' '.join(sentences)
    if os.path.exists(file_name):
        os.remove(file_name)
    return result

if __name__ == "__main__":
    url = ""
    print(crawl_report_func(url))