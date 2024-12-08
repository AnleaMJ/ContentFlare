def add_citations(summaries):
return [
f&quot;{summary[&#39;summary&#39;]}\nSource: {summary[&#39;source&#39;]}&quot;

for summary in summaries
]
