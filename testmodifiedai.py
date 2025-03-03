import openai
import pymongo
import speech_recognition as sr
import pyttsx3

# Configuration
API_KEY = "your_openai_api_key"
MONGO_URI = "your_mongodb_connection_string"
DB_NAME = "ai_database"
COLLECTION_NAME = "queries"

# Initialize MongoDB client
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Initialize speech engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Extract keywords from query
def extract_keywords(query):
    words = query.lower().split()
    return " ".join(sorted(set(words)))  # Sort for consistency

# Fetch response from OpenAI
def fetch_openai_response(query):
    openai.api_key = API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": query}]
    )
    return response["choices"][0]["message"]["content"]

# Main function to handle queries
def handle_query(query):
    keyword_query = extract_keywords(query)
    
    # Check if query exists in MongoDB
    existing_entry = collection.find_one({"query": keyword_query})
    if existing_entry:
        return existing_entry["response"]
    
    print("Query not recognized. Fetching response from OpenAI...")
    response = fetch_openai_response(query)
    
    # Store the response in MongoDB
    collection.insert_one({"query": keyword_query, "response": response})
    
    return response

# Capture speech input
def get_speech_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""

if __name__ == "__main__":
    while True:
        print("Say something or type your command: ")
        user_query = get_speech_input()
        
        if not user_query:
            user_query = input("Enter your command: ")
        
        if user_query.lower() in ["exit", "quit"]:
            break
        
        response = handle_query(user_query)
        print("AI Response:", response)
        speak(response)
