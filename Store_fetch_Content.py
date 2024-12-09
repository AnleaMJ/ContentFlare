
import pinecone
import webbrowser
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import os
from pinecone import Pinecone, ServerlessSpec
from pytrends.request import TrendReq

pc = Pinecone(api_key="pcsk_3vvfsm_E4DBQKku1MWsButZ1QtL2r8jcGaKkZRgBPjGM4mdu2hdx9kSjVMJpqvZocQtpE7")
pc.list_indexes()
url = "https://www.news18.com/cricket/india-women-vs-australia-women-live-cricket-score-2nd-odi-match-today-india-women-national-cricket-team-vs-australia-women-national-cricket-team-latest-scorecard-liveblog-9148747.html"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser') # Extract meaningful content (e.g., paragraphs)
paragraphs = soup.find_all('p')
content = " ".join(p.get_text() for p in paragraphs)
model = SentenceTransformer('all-MiniLM-L6-v2')
model.encode(content).tolist()
index=pc.Index(host="https://fetchcontent-3mznwow.svc.aped-4627-b74a.pinecone.io")
index.upsert(
            vectors=[
                   {"id":"1","values":[0.1,0.3],"metadata":{"content":content}}])
#get the content from vector
response = index.fetch(ids=["1"])
print(response)