import boto3
import json

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)


response = bedrock.converse(
    modelId="openai.gpt-oss-120b-1:0",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "text": "Who is sai pallavi explain in simple terms and also provide her hobbies and daily activites"
                }
            ]
        }
    ],
    
    inferenceConfig={
        "maxTokens":1000,
        "temperature":0.5
    }
)


print(json.dumps(response, indent=2, default=str))

print("\n\n======== MODEL OUTPUT ========\n")

content = response["output"]["message"]["content"]

for item in content:
    print(item)

# print(response["output"]["message"]["content"][0]["text"])




# client = boto3.client("bedrock-runtime", region_name="us-east-1")

# response = client.converse(
#     modelId="meta.llama3-3-70b-instruct-v1:0",
#     messages=[
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "text": "who is sai pallavi explain simply"
#                 }
#             ]
#         }
#     ]
# )

# print(response["output"]["message"]["content"][0]["text"])