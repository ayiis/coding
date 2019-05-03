from extract_article import extract_article
import requests


if __name__ == "__main__":

    url = 'https://news.cnblogs.com/n/624615/'
    url = 'https://tech.sina.com.cn/i/2019-04-29/doc-ihvhiqax5802337.shtml'
    # url = 'http://wb.sznews.com/PC/content/201902/22/content_567647.html'
    # url = 'http://ipingshan.sznews.com/content/2018-12/08/content_21265915.htm'
    # url = 'http://www.sohu.com/a/280148326_675286'
    # url = 'http://news.sznews.com/content/2019-04/26/content_21699029.htm'
    # url = 'http://forthxu.com/blog/article/73.html'
    # url = 'http://bm.szhk.com/2019/04/30/283029943930124.html'
    response = requests.get(url)

    title, article = extract_article(response.content)
    print("title:", title)
    print("article:", article)
