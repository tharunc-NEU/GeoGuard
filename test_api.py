import requests

API_KEY = "11a47e4ade9d46ae8d4936a6072435c4"

# URL with query parameters
url = f"https://newsapi.org/v2/everything?q=(Russia+OR+China+OR+North+Korea)+AND+(USA+OR+threat+OR+cyberattack+OR+military+OR+sanctions)&language=en&sortBy=relevancy&apiKey={API_KEY}"



# Make the API request
response = requests.get(url)

# Check the response status
if response.status_code == 200:
    print("Filtered News Data:")
    articles = response.json().get("articles", [])
    for article in articles[:5]:  # Print the first 5 articles
        print(f"Title: {article['title']}")
        print(f"Description: {article['description']}")
        print(f"Source: {article['source']['name']}")
        print("-" * 50)
else:
    print("API Test Failed!")
    print("Error:", response.json())




