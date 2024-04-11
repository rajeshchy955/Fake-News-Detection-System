import re
import pandas as pd
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

class Preprocessing:
    def text_preprocessing_user(self):
        # Initialize WordNetLemmatizer
        lm = WordNetLemmatizer()
        preprocess_data = []
        
        # Load stopwords
        stopwords_set = set(stopwords.words('english'))
        
        # Read the CSV file
        df = pd.read_csv('news.csv')
        
        # Preprocess each title in the CSV file
        for title in df['title']:
            review = re.sub(r'[^a-zA-Z0-9\s\.\,\:\-]', '', title)  # Include punctuation in regular expression
            review = review.lower()
            review = review.split()
            review = [lm.lemmatize(x) for x in review if x not in stopwords_set]
            review = " ".join(review)
            preprocess_data.append(review)
        
        return preprocess_data

# Example usage
preprocessor = Preprocessing()
titles = preprocessor.text_preprocessing_user()

