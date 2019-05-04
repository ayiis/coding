import requests
from readability import Document
import q

url = 'https://news.cnblogs.com/n/624615/'
url = 'https://tech.sina.com.cn/i/2019-04-29/doc-ihvhiqax5802337.shtml'

response = requests.get(url)
doc = Document(response.content)
doc.title()
s_html = doc.summary(True)
# s_html = doc.get_clean_html()

from dragnet import extract_content, extract_content_and_comments

print(s_html)
q.d()

content = extract_content(s_html)

print(content)
q.d()

# get article and comments
content_comments = extract_content_and_comments(content)

print(content_comments)

q.d()
