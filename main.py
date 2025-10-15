from fastapi import FastAPI, Request
from mangum import Mangum
import boto3
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

client = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

@app.post("/mcp")
async def mcp_handler(request: Request):
    try:
        body = await request.json()
        query_text = body.get("input", {}).get("text", "")
        if not query_text:
            return {"output": {"text": "Missing 'input.text' in request body."}}

        logging.info(f"Received MCP request: {body}")

        response = client.retrieve_and_generate(
            input={'text': query_text},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': 'YMQMMQDPUJ',
                    'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-pro-v1:0',
                    'generationConfiguration': {
                        'promptTemplate': {
                            'textPromptTemplate': (
                                "Using the following search results, answer the question clearly and concisely:\n\n"
                                "$search_results$\n\n"
                                "Question: $query$"
                            )
                        }
                    },
                    'orchestrationConfiguration': {
                        'promptTemplate': {
                            'textPromptTemplate': (
                                "Conversation so far:\n$conversation_history$\n\n"
                                "Search results:\n$search_results$\n\n"
                                "Instructions: $output_format_instructions$\n\n"
                                "Query: $query$"
                            )
                        }
                    }
                }
            }
        )

        return {"output": {"text": response['output']['text']}}

    except Exception as e:
        logging.error("MCP error", exc_info=True)
        return {"output": {"text": f"Error: {str(e)}"}}

# ✅ For API Gateway (via Mangum)
def handler(event, context):
    return Mangum(app)(event, context)

# ✅ For direct Lambda console testing
def lambda_handler(event, context):
    try:
        query_text = event.get("input", {}).get("text", "")
        if not query_text:
            return {"output": {"text": "Missing 'input.text' in request body."}}

        logging.info(f"Received Lambda test event: {event}")

        response = client.retrieve_and_generate(
            input={'text': query_text},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': 'YMQMMQDPUJ',
                    'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-pro-v1:0',
                    'generationConfiguration': {
                        'promptTemplate': {
                            'textPromptTemplate': (
                                "Using the following search results, answer the question clearly and concisely:\n\n"
                                "$search_results$\n\n"
                                "Question: $query$"
                            )
                        }
                    },
                    'orchestrationConfiguration': {
                        'promptTemplate': {
                            'textPromptTemplate': (
                                "Conversation so far:\n$conversation_history$\n\n"
                                "Search results:\n$search_results$\n\n"
                                "Instructions: $output_format_instructions$\n\n"
                                "Query: $query$"
                            )
                        }
                    }
                }
            }
        )

        return {"output": {"text": response['output']['text']}}

    except Exception as e:
        logging.error("Lambda test error", exc_info=True)
        return {"output": {"text": f"Error: {str(e)}"}}
