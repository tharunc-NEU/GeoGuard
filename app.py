import streamlit as st
import requests

# Define the API details again
BASE_URL = "https://api.together.ai/v1/completions"
API_KEY = "4f736ad3c3aea7ca3bd72c090637c8f5378809f92260d663c8bd19c378de42b8"

# Function for threat level detection (same as above)
def assign_threat_level(response_text):
    high_keywords = ["cyberattack", "critical infrastructure", "military", "state-sponsored", "national security", "hacking group", "terrorism", "weaponized"]
    moderate_keywords = ["data breach", "intellectual property", "sensitive data", "espionage", "exfiltration", "espionage"]
    
    if any(keyword in response_text.lower() for keyword in high_keywords):
        return "High"
    elif any(keyword in response_text.lower() for keyword in moderate_keywords):
        return "Moderate"
    else:
        return "Low"

# Function to query Together AI API
def query_together_ai(prompt, model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo", max_tokens=150):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
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
        response = requests.post(BASE_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            response_data = response.json()
            if "choices" in response_data and len(response_data["choices"]) > 0:
                response_text = response_data["choices"][0].get("text", "").strip()
                threat_level = assign_threat_level(response_text)
                return threat_level, response_text
            else:
                return "Error: No valid response found in the AI output."
        else:
            return f"Error: {response.status_code} - {response.json().get('error', {}).get('message', 'Unknown error')}"
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Streamlit UI to interact with the AI agent
def main():
    st.title("Interactive Threat Level Analyzer")
    
    st.write("Enter a query or a piece of news to analyze its threat level:")

    query = st.text_area("Your Query:", "", height=150)
    
    if st.button("Analyze"):
        if query:
            st.write("AI Agent is processing your query...")
            threat_level, analysis = query_together_ai(query)
            
            st.subheader(f"Threat Level: {threat_level}")
            st.text_area("Analysis Result:", analysis, height=300)
        else:
            st.warning("Please enter a query to analyze.")

if __name__ == "__main__":
    main()



# from flask import Flask, send_file

# app = Flask(__name__)

# @app.route("/")
# def serve_map():
#     return send_file("dynamic_threat_map.html")

# if __name__ == "__main__":
#     app.run(debug=True)

