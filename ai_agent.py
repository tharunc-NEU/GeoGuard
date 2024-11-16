from textblob import TextBlob
import json

def analyze_threats(articles):
    """
    Analyze articles for potential threats to the United States with balanced threat levels.
    """
    threats = []

    # Keyword categories for scoring
    critical_keywords = [
        "missile", "terrorism", "invasion", "nuclear", "war", "bioweapon",
        "cyberattack", "espionage", "assassination", "explosion", "genocide", "china","ukraine","russia","israel"
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

    # U.S.-specific terms
    us_terms = ["united states", "america", "u.s.", "us", "american", "washington", "pentagon"]

    for article in articles:
        try:
            full_content = article.get("full_content", "")
            title = article.get("title", "")
            description = article.get("description", "")
            url = article.get("url", "URL not available")

            # Combine text fields for analysis
            combined_text = f"{title} {description} {full_content}".lower()
            sentiment = TextBlob(combined_text).sentiment.polarity

            print(f"Analyzing article: {title}")

            # Check for U.S.-specific relevance
            if not any(term in combined_text for term in us_terms):
                print("Article not relevant to the U.S.; skipping.")
                continue

            # Initialize threat score
            threat_score = 0

            # Calculate scores based on keywords
            for word in combined_text.split():
                if word in critical_keywords:
                    threat_score += 3  # Highest weight
                elif word in important_keywords:
                    threat_score += 2  # Medium weight
                elif word in contextual_keywords:
                    threat_score += 1  # Lowest weight

            # Adjust thresholds dynamically for better distribution
            # Include sentiment analysis impact
            if threat_score >= 15 or sentiment < -0.6:
                threat_level = "HIGH"
            elif 6 <= threat_score < 15 or -0.6 <= sentiment <= 0:
                threat_level = "MODERATE"
            else:
                threat_level = "LOW"

            # Append the results to the threats list
            threats.append({
                "title": title,
                "description": description,
                "url": url,
                "threat_level": threat_level
            })

        except Exception as e:
            print(f"Error processing article: {article}. Error: {e}")
            continue

    return threats

def main():
    try:
        # Load articles from the JSON file
        with open("news_data.json", "r") as f:
            articles = json.load(f)
        print("Loaded articles successfully.")
    except Exception as e:
        print(f"Error loading data: {e}")
        articles = []

    # Analyze the threats
    threats = analyze_threats(articles)

    # Save analyzed data to a JSON file
    try:
        with open("analyzed_threats.json", "w") as f:
            json.dump(threats, f, indent=4)
        print("Threat analysis saved to 'analyzed_threats.json'.")
    except Exception as e:
        print(f"Error saving analysis: {e}")

if __name__ == "__main__":
    main()

