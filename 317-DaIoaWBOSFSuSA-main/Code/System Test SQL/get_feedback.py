import pandas as pd
import mysql.connector
import pickle
import nltk

# Import the necessary nltk data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Load model and phrases
def load_model(model_file):
    with open(model_file, 'rb') as f:
        model = pickle.load(f)
    return model

# Function to extract meaningful phrases
def extract_phrases(comment):
    phrases = []
    words = nltk.word_tokenize(comment)
    tagged_words = nltk.pos_tag(words)
    for i in range(len(tagged_words) - 2):
        word1, tag1 = tagged_words[i]
        word2, tag2 = tagged_words[i + 1]
        word3, tag3 = tagged_words[i + 2]
        if tag1.startswith('JJ') and (tag2.startswith('JJ') or tag2.startswith('NN')) and tag3.startswith('NN'):
            phrases.append(word1.lower() + ' ' + word2.lower() + ' ' + word3.lower())
    return phrases

# Load data from database
def load_database_data(host, user, password, database_name):
    # Connect to MySQL database
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database_name,
        port=3306
    )
    
    # Fetch data from database
    query = "SELECT feedback FROM feedback"  # Modify this query according to your database structure
    data = pd.read_sql(query, connection)
    
    # Close database connection
    connection.close()
    
    return data

# Function to extract top feedback phrases
def extract_top_feedback(data, model, num_phrases=5):
    top_feedback_phrases = []
    for feedback in data['feedback']:
        phrases = extract_phrases(feedback)
        feedback_scores = {phrase: model.get(phrase, 0) for phrase in phrases}
        sorted_phrases = sorted(feedback_scores.items(), key=lambda x: x[1], reverse=True)[:num_phrases]
        top_feedback_phrases.append(sorted_phrases)
    return top_feedback_phrases

# Main function
def main():
    # Load trained model and phrases
    model_file = "phrase_model.pkl"  # Change this to the path of your trained model file
    model = load_model(model_file)

    # Load data from database
    host = "192.185.48.158"
    user = "bisublar_bisux"
    password = "bisublar_bisux"
    database_name = "bisublar_bisux"
    port=3306
    data = load_database_data(host, user, password, database_name, port)

    # Extract top feedback phrases
    top_feedback_phrases = extract_top_feedback(data, model, num_phrases=5)

    # Create a dictionary to pass data to HTML template
    feedback_data = {}
    for i, phrases in enumerate(top_feedback_phrases, start=1):
        for j, (phrase, _) in enumerate(phrases, start=1):
            feedback_data[f'rank{j}'] = j
            feedback_data[f'phrase{j}'] = phrase

    # Render the HTML template with the feedback data
    with open('home.html', 'r') as file:
        html_content = file.read()

    # Replace placeholders in HTML template with actual feedback data
    html_content = html_content.format(**feedback_data)

    # Write the rendered HTML content to a new file
    with open('rendered_home.html', 'w') as file:
        file.write(html_content)

    print("HTML file generated successfully.")

if __name__ == "__main__":
    main()
