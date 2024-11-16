import json
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from dotenv import load_dotenv
import os

load_dotenv()

# Together AI API Configuration
BASE_URL = "https://api.together.ai/v1/completions"

# Load the API key from the environment variables
TOGETHER_API_KEY = os.getenv("TOGETHER_AI_API_KEY")

# Load news data from JSON file
def load_news_data(file_path="news_data.json"):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading news data: {e}")
        return []

# Filter relevant articles using TF-IDF
def filter_relevant_articles(query, articles, max_results=5):
    titles = [article.get("title", "") for article in articles]
    descriptions = [article.get("description", "") for article in articles]
    combined_texts = [f"{title}. {desc}" for title, desc in zip(titles, descriptions)]
    combined_texts.append(query)
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(combined_texts)
    similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]
    scored_articles = list(zip(articles, similarities))
    scored_articles.sort(key=lambda x: x[1], reverse=True)
    return [article for article, score in scored_articles[:max_results] if score > 0.1]

# Assign threat level based on response analysis
def assign_threat_level(response_text):
    high_keywords = ["cyberattack", "critical infrastructure", "military", "state-sponsored", "national security", "hacking group", "terrorism", "weaponized"]
    moderate_keywords = ["data breach", "intellectual property", "sensitive data", "espionage", "exfiltration"]
    
    if any(keyword in response_text.lower() for keyword in high_keywords):
        return "High"
    elif any(keyword in response_text.lower() for keyword in moderate_keywords):
        return "Moderate"
    else:
        return "Low"

# Generate a prompt for the AI model
def generate_prompt(query, relevant_articles):
    citations = "\n".join([f"- {article['title']} (URL: {article['url']})" for article in relevant_articles])
    return (
        f"Analyze this query for potential threats to the USA: '{query}'.\n\n"
        f"Relevant news articles:\n{citations}\n\n"
        f"Provide an in-depth analysis and highlight specific risks based on the provided context."
    )

# Query Together AI model
def query_together_ai(prompt, model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo", max_tokens=300):
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1.2,
        "stream": False
    }
    try:
        response = requests.post(BASE_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()["choices"][0]["text"]
        else:
            return f"Error: {response.status_code} - {response.json()['error']['message']}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def beautify_response(raw_response, threat_level):
    """
    Beautifies the raw response from the AI model into a structured and readable format.

    Args:
        raw_response (str): The raw response text from the AI model.
        threat_level (str): The threat level (High, Moderate, Low) based on the analysis.

    Returns:
        str: A formatted and beautified response.
    """
    # Basic cleanup of the response
    raw_response = raw_response.strip()
    
    # Create a structured format
    beautified_response = "\n".join([
        "===================================",
        "**Analysis and Key Insights:**",
        "===================================",
        raw_response,
        "===================================",
        f"**Threat Level: {threat_level}**",
        "===================================",
        "**End of Analysis**",
        "==================================="
    ])
    return beautified_response


if __name__ == "__main__":
    print("Welcome to the Interactive AI Agent!")
    print("Type your query below (type 'exit' to quit):")
    
    # Load news articles
    news_data = load_news_data()
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        # Filter relevant articles
        relevant_articles = filter_relevant_articles(user_input, news_data)
        
        if not relevant_articles:
            print("AI Agent: No relevant articles found for your query.")
            continue
        
        # Generate a prompt and query the model
        prompt = generate_prompt(user_input, relevant_articles)
        print("AI Agent is processing your query...\n")
        raw_response = query_together_ai(prompt)
        
        # Assign threat level based on the response
        threat_level = assign_threat_level(raw_response)
        
        # Beautify and display the response
        beautified_response = beautify_response(raw_response, threat_level)
        print(f"AI Agent:\n{beautified_response}\n")
