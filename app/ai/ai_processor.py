import json
from typing import Dict, List
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Configure OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TOPICS = [
    "Fundraising",
    "Cybersecurity Incident",
    "Product Launch",
    "Acquisition",
    "Partnership",
    "Executive Change",
    "Market Expansion",
    "Financial Results"
]

def tag_article(article_text: str) -> Dict:
    """
    Uses GPT-3.5 to identify companies and topics in an article.
    """
    if not article_text or not isinstance(article_text, str):
        return {"companies": [], "topics": []}
        
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a business news analyst. Analyze the article and extract:\n"
                              f"1. Company names mentioned\n"
                              f"2. Main topics from this list: {', '.join(TOPICS)}\n"
                              f"Return ONLY a JSON object with 'companies' (list of strings) and 'topics' (list of strings from the provided topics)"
                },
                {
                    "role": "user",
                    "content": article_text
                }
            ],
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return {
            "companies": result.get("companies", []),
            "topics": result.get("topics", [])
        }
    except Exception as e:
        print(f"Error in tag_article: {str(e)}")
        return {"companies": [], "topics": []}

def summarize_article(article_text: str) -> str:
    """
    Uses GPT-4 to generate a 1-2 sentence summary of an article.
    """
    if not article_text or not isinstance(article_text, str):
        return "The article cannot be summarized as the content provided is not sufficient or relevant."
        
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a business news summarizer. Create a concise 1-2 sentence summary of the article that captures the key business implications."
                },
                {
                    "role": "user",
                    "content": article_text
                }
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in summarize_article: {str(e)}")
        return ""