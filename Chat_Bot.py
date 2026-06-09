# from langchain_aws import BedrockEmbeddings

# embeddings = BedrockEmbeddings(
#     model_id="google.gemma-3-12b-it",
#     region_name="us-east-1"
# )

# r1=embeddings.embed_documents(
#     [
#        "Alpha is the first letter of Greek alphabet",
#        "Beta is the second letter of Greek alphabet", 
#     ]
# )
# print(len(r1[0]))

# result = embeddings.embed_query("What is the second letter of Greek alphabet ")
# print(result)




from langchain_aws import BedrockEmbeddings

embeddings = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v2:0",
    region_name="us-east-1"
)

r1 = embeddings.embed_documents([
    "Alpha is the first letter of Greek alphabet",
    "Beta is the second letter of Greek alphabet",
])

print(len(r1[0]))

result = embeddings.embed_query(
    "What is the second letter of Greek alphabet?"
)

print(result[:5])