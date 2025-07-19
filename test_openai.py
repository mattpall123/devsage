from openai import OpenAI

client = OpenAI(
  api_key="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"
)

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": "write a haiku about ai"}
  ]
)

print(completion.choices[0].message);

