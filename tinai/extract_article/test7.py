import q
import requests
from readability import Document
from newspaper import fulltext

from newspaper import Article
url = 'https://news.cnblogs.com/n/624615/'
url = 'https://tech.sina.com.cn/i/2019-04-29/doc-ihvhiqax5802337.shtml'
url = 'http://wb.sznews.com/PC/content/201902/22/content_567647.html'
url = 'http://ipingshan.sznews.com/content/2018-12/08/content_21265915.htm'
url = 'http://www.sohu.com/a/280148326_675286'
url = 'http://news.sznews.com/content/2019-04/26/content_21699029.htm'
url = 'http://forthxu.com/blog/article/73.html'
url = 'http://bm.szhk.com/2019/04/30/283029943930124.html'

a = Article(url, language='zh') # Chinese

a.download()
a.parse()

print(a.title)
print(a.text)

response = requests.get(url)
doc = Document(response.content)
title = doc.title()
html = doc.summary(True)

article = Article(url, language='zh')
article.download(input_html=html)
article.parse()

q.d()
print(article.title)
print(article.text)
exit(1)

response = requests.get(url)

doc = Document(response.content)
title = doc.title()
html = doc.summary(True)
q.d()
text = fulltext(html)
print(text)
