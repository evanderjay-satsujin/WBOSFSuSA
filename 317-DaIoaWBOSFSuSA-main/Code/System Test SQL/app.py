from flask import Flask, render_template, request, redirect, url_for, session
from admin_login import admin_login
from data_analytics import feedback_data_bp
import mysql.connector
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.feature_extraction.text import CountVectorizer
import joblib
import pandas as pd
import nltk
import hashlib

# Import the necessary nltk data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Load the trained model
model = joblib.load('sentiment_analysis_model.pkl')

# Load the vectorizer
vectorizer = joblib.load('tfidf_vectorizer.pkl')

# Define database connection parameters
DB_HOST = '192.185.48.158'
DB_USER = 'bisublar_bisux'
DB_PASSWORD = 'bisublar_bisux'
DB_NAME = 'bisublar_bisux'


# Create database connection
db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    port=3306
)

# Define hashing function for passwords
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Define preprocessing function
def preprocess_text(text):
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.lower()
    return text

# Function to extract adjectives from the feedback
def extract_adjectives(text):
    adjectives = []
    words = nltk.word_tokenize(text)
    tagged_words = nltk.pos_tag(words)
    for word, tag in tagged_words:
        if tag.startswith('JJ'):  # Check if the word is an adjective
            adjectives.append(word.lower())
    return adjectives

# Load data from database
def load_database_data():
    # Fetch data from database
    cursor = db.cursor(dictionary=True)
    query = "SELECT feedback, rating FROM feedback"
    cursor.execute(query)
    data = pd.DataFrame(cursor.fetchall())
    cursor.close()
    return data

def extract_top_adjectives(data, num_adjectives=5):
    feedback_adjectives = []
    for feedback in data['feedback']:
        adjectives = extract_adjectives(feedback)
        feedback_adjectives.extend(adjectives)

    # Count occurrences of each adjective
    adjective_counts = {adj: feedback_adjectives.count(adj) for adj in set(feedback_adjectives)}

    # Sort adjectives by count in descending order
    sorted_adjectives = sorted(adjective_counts.items(), key=lambda x: x[1], reverse=True)

    # Take the top num_adjectives
    top_adjectives = sorted_adjectives[:num_adjectives]

    return top_adjectives

@app.route('/home')
def home():
    # Load data from database
    data = load_database_data()

    # Extract adjectives from the feedback
    adjectives = []
    for feedback in data['feedback']:
        adjectives.extend(extract_adjectives(feedback))

    # Count occurrences of each adjective
    adjective_counts = {adj: adjectives.count(adj) for adj in set(adjectives)}

    # Sort adjectives by count in descending order
    sorted_adjectives = sorted(adjective_counts.items(), key=lambda x: x[1], reverse=True)

    # Take the top 5 adjectives
    top_adjectives = sorted_adjectives[:5]

    # Create a dictionary to pass data to HTML template
    feedback_data = {}
    for i, (adjective, count) in enumerate(top_adjectives, start=1):
        feedback_data[f'rank{i}'] = i
        feedback_data[f'adjective{i}'] = adjective
        feedback_data[f'count{i}'] = count

    # Calculate average rating
    average_rating = data['rating'].mean()

    # Add average_rating to feedback_data
    feedback_data['average_rating'] = round(average_rating, 1)

    # Print out the feedback_data dictionary
    print("Top 5 Most Used Adjectives:")
    for key, value in feedback_data.items():
        print(key, value)

    # Render the HTML template with the feedback data
    return render_template('home.html', feedback_data=feedback_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    email = request.form['email']
    feedback = request.form['feedback']
    rating = request.form['rating']
    
    # Preprocess the feedback
    processed_feedback = preprocess_text(feedback)

    # Vectorize input
    vectorized_input = vectorizer.transform([processed_feedback])

    # Make prediction
    sentiment = model.predict(vectorized_input)[0]

    # Store the feedback and prediction in the database
    cursor = db.cursor()
    try:
        cursor.callproc('sp_insert_feedback_data', (email, feedback, rating, sentiment))
        db.commit()
    except Exception as e:
        print("Error:", e)
        db.rollback()
    finally:
        cursor.close()

    # Redirect to the thank_you.html page
    return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/feedback_form')
def feedback_form():
    return render_template('feedback_form.html')

@app.route('/server')
def render_server_page():
    try:
        # Fetch feedback data from the database
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM feedback")  # Modify this query as per your table structure
        feedback_data = cursor.fetchall()
        # Process the result if needed
    except Exception as e:
        # Handle any exceptions
        print("Error fetching feedback data:", e)
        feedback_data = []
    finally:
        if 'cursor' in locals():
            cursor.close()

    # Calculate feedback percentages
    total_feedback = len(feedback_data)
    negative_feedback_count = sum(1 for feedback in feedback_data if feedback.get('sentiment') == 'Negative')
    positive_feedback_count = total_feedback - negative_feedback_count

    if total_feedback > 0:
        negative_percentage = round((negative_feedback_count / total_feedback) * 100, 2)
        positive_percentage = round((positive_feedback_count / total_feedback) * 100, 2)
    else:
        negative_percentage = 0
        positive_percentage = 0

    # Render the template with feedback data and percentages
    return render_template('server.html', feedback_data=feedback_data,
                           negative_percentage=negative_percentage,
                           positive_percentage=positive_percentage)

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # Clear session variables
    # (Optional depending on your implementation)
    session.clear()

    # Redirect to the admin login endpoint
    return redirect(url_for('admin_login.admin_login_route'))


@app.route('/process_signup', methods=['POST'])
def process_signup():
    # Form data
    username = request.form['username']
    password = request.form['password']

    # Hash the password using MD5
    hashed_password = hashlib.md5(password.encode()).hexdigest()

    # Insert new admin user into database
    cursor = db.cursor()
    query = "INSERT INTO admin (username, password) VALUES (%s, %s)"
    values = (username, hashed_password)
    try:
        cursor.execute(query, values)
        db.commit()
        cursor.close()
        return redirect(url_for('render_server_page'))
    except Exception as e:
        error_message = "Error occurred: {}".format(str(e))
        return error_message


# Registering routes from other files
app.register_blueprint(admin_login, url_prefix='/admin')
app.register_blueprint(feedback_data_bp)

if __name__ == '__main__':
    app.run(debug=True)
