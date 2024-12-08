from together import Together

client = Together()
response = client.images.generate(
    prompt="[]",
    model="black-forest-labs/FLUX.1-schnell",
    width=1024,
    height=768,
    steps=4,
    n=1,
    response_format="b64_json"
)
print(response.data[0].b64_json)
