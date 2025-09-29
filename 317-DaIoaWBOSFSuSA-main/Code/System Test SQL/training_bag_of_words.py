import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from collections import Counter
import pickle

# Download NLTK data (needed for POS tagging)
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Function to extract meaningful phrases
def extract_phrases(comment):
    phrases = []
    words = word_tokenize(comment)
    tagged_words = nltk.pos_tag(words)
    for i in range(len(tagged_words) - 2):
        word1, tag1 = tagged_words[i]
        word2, tag2 = tagged_words[i + 1]
        word3, tag3 = tagged_words[i + 2]
        if tag1.startswith('JJ') and (tag2.startswith('JJ') or tag2.startswith('NN')) and tag3.startswith('NN'):
            phrases.append(word1.lower() + ' ' + word2.lower() + ' ' + word3.lower())
    return phrases

# Load data from CSV file
def load_data(csv_file):
    data = pd.read_csv(csv_file)
    return data

# Train model
def train_model(data):
    all_phrases = []
    for comment in data['Comment']:
        all_phrases.extend(extract_phrases(comment))

    # Count phrase occurrences
    phrase_counts = Counter(all_phrases)

    return phrase_counts

# Save model and related files
def save_model(phrase_counts, model_file, phrases_file):
    with open(model_file, 'wb') as f:
        pickle.dump(phrase_counts, f)

    with open(phrases_file, 'w') as f:
        for phrase, count in phrase_counts.items():
            f.write(f"{phrase}: {count}\n")

# Main function
def main():
    # Load data
    csv_file = "bag_of_words.csv"  # Change this to the path of your CSV file
    data = load_data(csv_file)

    # Train model
    phrase_counts = train_model(data)

    # Save model and related files
    model_file = "phrase_model.pkl"
    phrases_file = "top_phrases.txt"
    save_model(phrase_counts, model_file, phrases_file)

    print("Model trained and saved successfully.")

if __name__ == "__main__":
    main()
