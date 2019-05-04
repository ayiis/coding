from boilerpipe.extract import Extractor
import q
import requests
from readability import Document

url = 'https://news.cnblogs.com/n/624615/'
url = 'https://tech.sina.com.cn/i/2019-04-29/doc-ihvhiqax5802337.shtml'
url = 'http://forthxu.com/blog/article/73.html'
url = 'http://forthxu.com/blog/article/91.html'
url = 'http://forthxu.com/blog/article/gmail-sub-account.html'

response = requests.get(url)

doc = Document(response.content)

print(doc.title())

s_html = doc.summary(True)

print("s_html:", s_html)

extractor = Extractor(extractor='ArticleExtractor', html=s_html)
# extractor = Extractor(extractor='ArticleExtractor', url=url)

extracted_text = extractor.getText()

print("extracted_text:", extracted_text)

# extracted_html = extractor.getHTML()

q.d()
