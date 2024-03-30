# import anthropic library
import anthropic

client = anthropic.Anthropic(
    api_key="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",
)
query_input = input("Enter your PromQL query: ")
# create the prompt and call the API
message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=100,
    temperature=0.0,
    system="Please provide a PromQL query for me to execute against prom api.",
    messages=[
        {
          "role": "user",
          "content": query_input
        }
    ]
)

print(message.content,query_input)