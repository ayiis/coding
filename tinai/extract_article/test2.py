import requests
from dragnet import extract_content, extract_content_and_comments
import q

# fetch HTML
# url = 'https://moz.com/devblog/dragnet-content-extraction-from-diverse-feature-sets/'
url = 'https://news.cnblogs.com/n/624615/'
url = 'https://tech.sina.com.cn/i/2019-04-29/doc-ihvhiqax5802337.shtml'
r = requests.get(url)


from dragnet.util import load_pickled_model

content_extractor = load_pickled_model(
            'kohlschuetter_readability_weninger_content_model.pkl.gz')
content_comments_extractor = load_pickled_model(
            'kohlschuetter_readability_weninger_comments_content_model.pkl.gz')

content = content_extractor.extract(r.content)

q.d()

content_comments = content_comments_extractor.extract(r.content)

q.d()
