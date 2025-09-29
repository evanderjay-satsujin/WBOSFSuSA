from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
import joblib
import MySQLdb

app = Flask(__name__)

# Load the trained model
model = joblib.load('sentiment_analysis_model.pkl')

# Load the vectorizer
vectorizer = joblib.load('tfidf_vectorizer.pkl')

# Define database connection parameters
DB_HOST = '192.185.48.158'
DB_USER = 'bisublar_bisux'
DB_PASSWORD = 'bisublar_bisux'
DB_NAME = 'bisublar_bisux'
DB_PORT = 3306

# Create database connection
db = MySQLdb.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, port=DB_PORT)

# Define preprocessing function
def preprocess_text(text):
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.lower()
    return text

@app.route('/')
def index():
    return render_template('feedback_form.html')

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
    query = "INSERT INTO feedback (email, feedback, rating, sentiment) VALUES (%s, %s, %s, %s)"
    values = (email, feedback, rating, sentiment)
    cursor.execute(query, values)
    db.commit()
    cursor.close()

    # Redirect to the thank_you.html page
    return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

if __name__ == '__main__':
    app.run(debug=True)
