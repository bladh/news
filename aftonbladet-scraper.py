#!/usr/bin/env python3
import httplib2
import html2text
import time
import dominate
from dominate.tags import *
from bs4 import BeautifulSoup, SoupStrainer
from multiprocessing.dummy import Pool as ThreadPool

def parse_article(article_data, full_url):
    h = html2text.HTML2Text()
    h.ignore_links = True
    output = h.handle(article_data)
    a = output.split("LÄS OCKSÅ")[0]
    content = a.splitlines()
    title = content[0].split("|")[0]
    body = [ c + " " for c in content[1:] if "FÖLJ" not in c if "|" not in c if "NYHETER" not in c if "LÄS" not in c if "DRYCK" not in c if "KULTUR" not in c if "LEDARE" not in c if "DEBATT" not in c if "RESA" not in c if "SENASTE" not in c if "NYTT" not in c if "VIKT" not in c if "KLUBBA" not in c if "ARTIKEL" not in c]
    article_text = "".join(body[1:]).strip()
    return {"title": title, "body": article_text, "url":full_url}


def extract_article(article_url):
    full_url = base_aftonbladet + article_url
    status, response = httplib2.Http().request(full_url)
    article_soup = BeautifulSoup(response, features="html.parser")
    # Remove scripts and styles
    for script in article_soup(["script", "style"]):
        script.extract()
    text = article_soup.get_text()
    return parse_article(text, full_url)


def make_html(articles):
    doc = dominate.document(title="News")
    with doc.head:
        link(rel='stylesheet', href='style.css')

    with doc:
        for article in articles:
            with div():
                attr(cls='article')
                h3(article["title"])
                p(article["body"])
                p(article["url"])

    return doc


def get_links(base_url):
    http = httplib2.Http()
    status, response = http.request(base_aftonbladet)
    soup = BeautifulSoup(response, parse_only=SoupStrainer('a'), features="html.parser")
    newslinks = []
    for link in soup:
        if link.has_attr('href'):
            a = link['href']
            if a.startswith('/nyheter'):
                newslinks.append(a)
            if a.startswith('/nojesbladet/a/'):
                newslinks.append(a)
    return newslinks


def get_aftonbladet():
    base_aftonbladet = 'http://www.aftonbladet.se'
    newslinks = get_links(base_aftonbladet)
    pool = ThreadPool(4)
    articles = pool.map(extract_article, newslinks)
    pool.close()
    pool.join()
    return articles


if __name__ == "__main__":
    articles = get_aftonbladet()
    print(make_html(articles))
