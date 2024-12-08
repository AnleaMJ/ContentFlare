from sentence_transformers import SentenceTransformer
import pinecone

# Initialize embedding model

embedding_model = SentenceTransformer(&#39;all-MiniLM-L6-v2&#39;)

# Initialize vector database (Pinecone example)
pinecone.init(api_key=&quot;YOUR_API_KEY&quot;, environment=&quot;us-west1-gcp&quot;)
index = pinecone.Index(&quot;proprietary-data-index&quot;)

# Step 1: Add proprietary data to the database
documents = [
{&quot;id&quot;: &quot;doc1&quot;, &quot;text&quot;: &quot;Company revenue grew by 20% in 2023.&quot;},
{&quot;id&quot;: &quot;doc2&quot;, &quot;text&quot;: &quot;The company was founded in 2010.&quot;}
]
for doc in documents:
embedding = embedding_model.encode(doc[&quot;text&quot;]).tolist()
index.upsert([(doc[&quot;id&quot;], embedding)])

# Step 2: User query
query = &quot;What was the company’s growth in 2023?&quot;
query_embedding = embedding_model.encode(query).tolist()

# Step 3: Search for relevant context
search_results = index.query(query_embedding, top_k=1, include_metadata=True)
context = search_results[&quot;matches&quot;][0][&quot;metadata&quot;][&quot;text&quot;]

# Step 4: Pass context and query to LLM
from openai import ChatCompletion

response = openai.ChatCompletion.create(
model=&quot;gpt-4&quot;,
messages=[
{&quot;role&quot;: &quot;system&quot;, &quot;content&quot;: context},
{&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: query}
]
)

print(response[&quot;choices&quot;][0][&quot;message&quot;][&quot;content&quot;])
