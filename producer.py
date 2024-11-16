from kafka import KafkaProducer
import requests
import json
import time
from bs4 import BeautifulSoup

from dotenv import load_dotenv
import os

load_dotenv()


# Kafka Configuration
KAFKA_TOPIC = "news_topic"
KAFKA_SERVER = "localhost:9092"

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",  # Change to your Kafka broker address if needed
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)


# NewsAPI Configuration
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
def fetch_news():
    """Fetch news related to global threats."""
    keywords = [
        "Russia", "North Korea", "China", "cyber-attack", "military movement",
        "AI weapons", "autonomous systems", "nuclear weapons", "Pentagon",
        "sanctions", "espionage", "Israel", "Ukraine", "Iran", "Palestine",
        "Syria", "Afghanistan", "Pakistan", "Libya", "Yemen", "Somalia",
        "Turkey", "Belarus", "Venezuela", "Saudi Arabia", "Taiwan", "India",
        "South Korea", "Japan", "United States"
    ]

    query = " OR ".join(keywords)  # Combine keywords with OR
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=relevancy&pageSize=20&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("articles", [])
    else:
        print("Failed to fetch news:", response.json())
        return []

def scrape_full_article(url):
    """Scrape the full article content from the URL."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract paragraphs from the article
            paragraphs = soup.find_all('p')
            full_content = ' '.join([p.get_text() for p in paragraphs])
            return full_content
        else:
            return "Unable to fetch the full article."
    except Exception as e:
        return f"Error occurred while scraping: {str(e)}"

counter = 1
while True:
    articles = fetch_news()
    for article in articles:
        url = article.get("url", "")
        full_content = scrape_full_article(url)

        # Prepare the data to be sent to Kafka
        data = {
            "title": article["title"],
            "description": article.get("description", ""),
            "source": article["source"]["name"],
            "url": url,
            "full_content": full_content
        }

        # Send the message to Kafka
        producer.send(KAFKA_TOPIC, value=data)
        
        # Print the message to the console
        print("=" * 50)
        print(f"\nMessage {counter}:")
        print(json.dumps(data, indent=4))
        print("=" * 50)

        counter += 1
    
    # Fetch news every 10 seconds
    time.sleep(10)