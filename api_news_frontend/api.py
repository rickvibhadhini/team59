'''
from flask import Flask, render_template, request
import requests

app = Flask(__name__)



API_KEY = 'fb3012cefcdb483fbaa0fa7d8b673259'
BASE_URL = 'https://newsapi.org/v2/top-headlines'
#BASE_URL = 'https://newsapi.org/v2/everything'


@app.route('/')
def index():
    category = request.args.get('category', 'general')
    response = requests.get(BASE_URL, params={'apiKey': API_KEY, 'category': category, 'country': 'us'})
    news_data = response.json()
    articles = news_data.get('articles', [])
    return render_template('index.html', articles=articles)
     
@app.route('/chat-room')
def chat_room():
    return render_template('chat.html')

if __name__ == '__main__':
    app.run(debug=True)
    '''

#using everything
from flask import Flask, render_template, request
import requests
import ast
from PIL import Image
import pytesseract
import os
import tempfile
import logging

app = Flask(__name__)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

API_KEY = 'fb3012cefcdb483fbaa0fa7d8b673259'
BASE_URL = 'https://newsapi.org/v2/everything'

def get_user_recommendations(user_id):
    try:
        with open(f"gnn.txt", "r") as file:
            # Read the file content, which is in the format of "Recommended categories for user X: [...]"
            content = file.read().strip()
            # Extract the list from the text file content
            start = content.find('[')
            end = content.find(']')
            categories_str = content[start:end+1]
            categories = ast.literal_eval(categories_str)  # Safely convert string to list
            return categories
    except Exception as e:
        print(f"Error reading recommendations: {e}")
        return []

@app.route('/')
def index():
    # Use the 'category' parameter from the URL to map it to keywords
    category = request.args.get('category', 'general')
    
    # Map category to relevant search keywords (this mapping can be customized)
    category_keywords = {
        'business': 'business',
        'entertainment': 'entertainment',
        'technology': 'technology',
        'sports': 'sports',
        'health': 'health',
        'science': 'science',
        'general': 'news'  # Use 'news' or a broad keyword for general category
    }

    # Get the keyword for the selected category
    keyword = category_keywords.get(category, 'news')

    # Send request to the 'everything' endpoint with the keyword
    response = requests.get(BASE_URL, params={'apiKey': API_KEY, 'q': keyword, 'language': 'en'})
    news_data = response.json()
    articles = news_data.get('articles', [])
    
    if not articles:
        return "No articles available for this keyword", 404
    
    return render_template('index.html', articles=articles)

#@app.route('/chat-room')
#def chat_room():
#    return render_template('chat.html')

@app.route('/chat-room', methods=['GET'])
def chat_room():
    message = request.args.get('messageInp')
    if message:
        # Process the message here, or pass it to your chatbot logic
        response_message = f"You said: {message}"
        return {"response": response_message}  # Return JSON response
    return render_template('chat.html')  # Default view if no message is sent


@app.route('/quiz')
def take_quiz():
    # This route renders the quiz HTML template
    return render_template('quiz.html')

@app.route('/scan-articles', methods=['GET', 'POST'])
def scan_articles():
    extracted_text = None
    if request.method == 'POST':
        image_file = request.files['image']
        if image_file:
            # Create a temporary file for the uploaded image
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpeg") as temp_image:
                image_path = temp_image.name
                image_file.save(image_path)

            # Open the temporary image and process with pytesseract
            try:
                with Image.open(image_path) as img:
                    extracted_text = pytesseract.image_to_string(img)
            finally:
                # Ensure the file is deleted after processing
                os.remove(image_path)
    
    # Pass the extracted text to the template
    return render_template('scan.html', extracted_text=extracted_text)


@app.route('/personalized-recommendations')
def personalized_recommendations():
    # For demo, we assume user 1 is logged in. You can dynamically set this based on actual user.
    user_id = 1
    
    # Get recommended categories for the user
    recommended_categories = get_user_recommendations(user_id)
    
    # Fetch articles for each recommended category
    all_articles = []
    for category in recommended_categories:
        response = requests.get(BASE_URL, params={'apiKey': API_KEY, 'q': category, 'language': 'en'})
        news_data = response.json()
        articles = news_data.get('articles', [])
        all_articles.extend(articles)  # Add articles from each category to the list

    if not all_articles:
        return "No personalized articles available for this user", 404
    
    return render_template('personalized_recommendations.html', articles=all_articles)



@app.route('/languages')
def languages():
    # Extract language and keyword from URL parameters
    lang = request.args.get('lang', 'en')
    keyword = request.args.get('keyword', 'news')

    # Build parameters for the API request
    params = {'apiKey': API_KEY}
    if lang:
        params['language'] = lang
    if keyword:
        params['q'] = keyword

    # Log the parameters for debugging purposes
    logging.info(f"Requesting news with parameters: {params}")

    # Send the request to the News API
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Check for HTTP errors

        news_data = response.json()
        articles = news_data.get('articles', [])

        if not articles:
            return "No articles available for this language or keyword", 404

        return render_template('lang.html', articles=articles)
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching news: {e}")
        return "Error fetching news", 500


if __name__ == '__main__':
    app.run(debug=True)
