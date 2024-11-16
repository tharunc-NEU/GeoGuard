
from kafka import KafkaConsumer
import json
from textblob import TextBlob

# Kafka Consumer Configuration
consumer = KafkaConsumer(
    'news_topic',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='news-consumer-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Analyze Threat
def analyze_threat(article):
    critical_keywords = [
        "missile", "terrorism", "invasion", "nuclear", "war", "bioweapon",
        "cyberattack", "espionage", "assassination", "explosion", "genocide","china","ukraine","russia","israel"
    ]
    important_keywords = [
        "cyber", "attack", "hack", "theft", "data breach", "surveillance",
        "military", "troops", "weapon", "conflict", "sanctions", "propaganda",
        "threat", "missile test", "airstrike", "intelligence"
    ]
    contextual_keywords = [
        "AI", "evolution", "agent", "research", "policy", "diplomacy",
        "negotiation", "defense", "trade", "economy", "technology",
        "communication", "development"
    ]
    us_terms = ["united states", "america", "u.s.", "us", "american", "washington", "pentagon"]

    full_content = article.get("full_content", "")
    title = article.get("title", "")
    description = article.get("description", "")
    url = article.get("url", "URL not available")

    combined_text = f"{title} {description} {full_content}".lower()
    sentiment = TextBlob(combined_text).sentiment.polarity

    if not any(term in combined_text for term in us_terms):
        return None  # Skip non-US relevant articles

    threat_score = sum([
        3 if word in critical_keywords else 2 if word in important_keywords else 1 if word in contextual_keywords else 0
        for word in combined_text.split()
    ])

    if threat_score >= 15 or sentiment < -0.6:
        threat_level = "HIGH"
    elif 6 <= threat_score < 15 or -0.6 <= sentiment <= 0:
        threat_level = "MODERATE"
    else:
        threat_level = "LOW"

    return {
        "title": title,
        "description": description,
        "url": url,
        "threat_level": threat_level
    }

# Assign Coordinates
def assign_coordinates(title):
    """
    Assign coordinates based on keywords in the title.
    Includes both high-threat and low-threat countries.
    """
    title = title.lower()

    # High-threat countries
    if "north korea" in title:
        return [40.3399, 127.5101]  # North Korea
    elif "russia" in title:
        return [61.5240, 105.3188]  # Russia
    elif "ukraine" in title:
        return [48.3794, 31.1656]  # Ukraine
    elif "iran" in title:
        return [32.4279, 53.6880]  # Iran
    elif "china" in title:
        return [35.8617, 104.1954]  # China
    elif "syria" in title:
        return [34.8021, 38.9968]  # Syria
    elif "palestine" in title or "gaza" in title:
        return [31.9522, 35.2332]  # Palestine/Gaza
    elif "yemen" in title:
        return [15.5527, 48.5164]  # Yemen
    elif "somalia" in title:
        return [5.1521, 46.1996]  # Somalia
    elif "belarus" in title:
        return [53.7098, 27.9534]  # Belarus
    elif "venezuela" in title:
        return [6.4238, -66.5897]  # Venezuela

    # Moderate-threat countries
    elif "afghanistan" in title:
        return [33.9391, 67.7100]  # Afghanistan
    elif "iraq" in title:
        return [33.2232, 43.6793]  # Iraq
    elif "pakistan" in title:
        return [30.3753, 69.3451]  # Pakistan
    elif "turkey" in title:
        return [38.9637, 35.2433]  # Turkey
    elif "libya" in title:
        return [26.3351, 17.2283]  # Libya
    elif "saudi arabia" in title:
        return [23.8859, 45.0792]  # Saudi Arabia

    # Low-threat countries
    elif "canada" in title:
        return [56.1304, -106.3468]  # Canada
    elif "japan" in title:
        return [36.2048, 138.2529]  # Japan
    elif "germany" in title:
        return [51.1657, 10.4515]  # Germany
    elif "united kingdom" in title or "uk" in title:
        return [55.3781, -3.4360]  # United Kingdom
    elif "france" in title:
        return [46.6034, 1.8883]  # France
    elif "australia" in title:
        return [-25.2744, 133.7751]  # Australia
    elif "new zealand" in title:
        return [-40.9006, 174.8860]  # New Zealand
    elif "sweden" in title:
        return [60.1282, 18.6435]  # Sweden
    elif "norway" in title:
        return [60.4720, 8.4689]  # Norway
    elif "finland" in title:
        return [61.9241, 25.7482]  # Finland

    # Default location for unspecified or global topics
    else:
        return [20.0, 0.0]  # Default global location


# Save Threats to JSON
def save_to_json(threats, file_path="threats.json"):
    with open(file_path, "w") as file:
        json.dump(threats, file, indent=4)
    print(f"Threats saved to {file_path}")

# Main Consumer Logic
def consume_messages():
    threats = []
    for message in consumer:
        article = message.value
        print(f"Received: {article['title']}")
        threat = analyze_threat(article)
        if threat:
            threat["coordinates"] = assign_coordinates(threat["title"])
            threats.append(threat)
            save_to_json(threats)

if __name__ == "__main__":
    consume_messages()
