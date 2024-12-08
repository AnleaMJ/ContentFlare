#import required libraries
#pip install openai pinecone requests flask fastapi pillow transformers synthetize pytorch

#1. User Input (Prompt)
#Create an input handler that takes the user’s content type, tone, and prompt.

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route(&#39;/generate&#39;, methods=[&#39;POST&#39;])
def handle_prompt():
user_input = request.json
prompt = user_input[&#39;prompt&#39;]
tone = user_input.get(&#39;tone&#39;, &#39;formal&#39;)
content_type = user_input.get(&#39;content_type&#39;, &#39;text&#39;)
platform = user_input.get(&#39;platform&#39;, &#39;LinkedIn&#39;)

return jsonify({
&quot;message&quot;: &quot;Processing...&quot;,
&quot;prompt&quot;: prompt,
&quot;tone&quot;: tone,
&quot;content_type&quot;: content_type,
&quot;platform&quot;: platform
})
