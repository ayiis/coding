import requests
from dragnet import extract_content, extract_content_and_comments
import q

# fetch HTML
# url = 'https://moz.com/devblog/dragnet-content-extraction-from-diverse-feature-sets/'
url = 'https://tech.sina.com.cn/i/2019-04-29/doc-ihvhiqax5802337.shtml'
r = requests.get(url)

# get main article without comments
content = extract_content(r.content)

print(content)
q.d()

# get article and comments
content_comments = extract_content_and_comments(r.content)

print(content_comments)

q.d()
