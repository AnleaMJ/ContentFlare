#Use GPT-4 or similar LLMs to summarize retrieved articles and adjust the tone.

import openai

openai.api_key = &quot;YOUR_OPENAI_API_KEY&quot;

def summarize_and_adjust_tone(articles, tone):
summaries = []
for article in articles:
content = f&quot;Summarize the following in a {tone} tone:\n{article[&#39;description&#39;]}&quot;
response = openai.ChatCompletion.create(
model=&quot;gpt-4&quot;,
messages=[{&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: content}]
)
summaries.append({
&quot;summary&quot;: response.choices[0].message[&#39;content&#39;],
&quot;source&quot;: article[&#39;url&#39;]

})
return summaries
