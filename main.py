from fastapi import FastAPI, Request
from mangum import Mangum
import boto3
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Initialize Bedrock Agent Runtime client
client = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

@app.post("/mcp")
async def mcp_handler(request: Request):
    try:
        # Safely parse incoming JSON
        try:
            body = await request.json()
        except Exception as parse_error:
            logging.error("Failed to parse JSON", exc_info=True)
            return {
                "output": {
                    "text": "Invalid JSON input. Please ensure your request body is properly formatted."
                }
            }

        query_text = body.get("input", {}).get("text", "")
        if not query_text:
            return {
                "output": {
                    "text": "Missing 'input.text' in request body."
                }
            }

        logging.info(f"Received MCP request: {body}")

        # Call Bedrock retrieve_and_generate
        response = client.retrieve_and_generate(
            input={'text': query_text},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': 'YMQMMQDPUJ',  # Replace with your actual KB ID
                    'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-nova-pro',
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

        return {
            "output": {
                "text": response['output']['text']
            }
        }

    except Exception as e:
        logging.error("MCP error", exc_info=True)
        return {
            "output": {
                "text": f"Error: {str(e)}"
            }
        }

# ✅ Lambda-compatible handler function
def handler(event, context):
    return Mangum(app)(event, context)
