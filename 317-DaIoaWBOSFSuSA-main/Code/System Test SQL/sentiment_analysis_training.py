import pandas as pd
import string
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.metrics import classification_report
import joblib

# Load the dataset
try:
    data = pd.read_csv('office_feedback_dataset.csv')
except FileNotFoundError:
    print("Error: Dataset file 'office_feedback_dataset.csv' not found.")
    exit()

# Define preprocessing function
def preprocess_text(text):
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Convert to lowercase
    text = text.lower()
    return text

# Apply preprocessing to the feedback column
data['processed_feedback'] = data['feedback'].apply(preprocess_text)

# Check the first few rows of the loaded data
print("First few rows of the dataset:")
print(data.head())

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(data['processed_feedback'], data['sentiment'], test_size=0.2, random_state=42)

# Feature extraction using TF-IDF vectorization
vectorizer = TfidfVectorizer(max_features=1000)  # You can adjust max_features as needed
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Train the SVM classifier
svm_classifier = SVC(kernel='linear')
svm_classifier.fit(X_train_tfidf, y_train)

# Save the trained model
joblib.dump(svm_classifier, 'sentiment_analysis_model.pkl')

# Save the vectorizer
joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')

print("Model trained and saved successfully.")
