from nltk.stem import WordNetLemmatizer
import re
from nltk.corpus import stopwords

class Preprocessing:
    
    def __init__(self, data):
        self.data = data
        
    def text_preprocessing_user(self):
        lm = WordNetLemmatizer()
        pred_data = [self.data]    
        preprocess_data = []
        
        # Load stopwords
        stopwords_set = set(stopwords.words('english'))
        
        for data in pred_data:
            review = re.sub(r'[^a-zA-Z0-9\s\.\,\:\-]', '', data)  # Include punctuation in regular expression
            review = review.lower()
            review = review.split()
            review = [lm.lemmatize(x) for x in review if x not in stopwords_set]  # Use stopwords_set
            review = " ".join(review)
            preprocess_data.append(review)
        
        # Join all the preprocessed strings into a single string
        processed_string = " ".join(preprocess_data)
        return processed_string

data = 'FLYNN: Hillary Clinton, Big Woman on Campus - Breitbart'
#print(Preprocessing(data).text_preprocessing_user())
