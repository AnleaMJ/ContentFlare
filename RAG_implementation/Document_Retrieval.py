#Retrieve the most relevant documents using news APIs like Bing or Google News and apply filters.

import requests

def retrieve_articles(query, date_filter=None):
api_key = &quot;YOUR_BING_NEWS_API_KEY&quot;
endpoint = f&quot;https://api.bing.microsoft.com/v7.0/news/search?q={query}&quot;
headers = {&quot;Ocp-Apim-Subscription-Key&quot;: api_key}

response = requests.get(endpoint, headers=headers).json()
articles = []

for article in response.get(&#39;value&#39;, []):
if date_filter and article[&#39;datePublished&#39;] &lt; date_filter:
continue
articles.append({

&quot;title&quot;: article[&#39;name&#39;],
&quot;url&quot;: article[&#39;url&#39;],
&quot;description&quot;: article[&#39;description&#39;]
})

return articles
