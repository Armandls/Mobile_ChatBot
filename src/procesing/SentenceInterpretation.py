import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('averaged_perceptron_tagger')

# Words that cannot be removed
not_stop_words = ["more", "less","about","like", "around", "no", "not", "€", "$"]


# Function to tokenize, remove punctuation marks and filter stop words
def process_input(sentence):
    # Remove punctuation marks
    sentence = re.sub(r'[^\w\s.,$€]', '', sentence)

    # Tokenize the string and convert it to lowercase
    tokens = nltk.word_tokenize(sentence.lower())

    # Define stop words
    stop_words = set(stopwords.words('english'))
    
    # Filter stop words
    filtered_tokens = [word for word in tokens if word not in stop_words or word in not_stop_words]

    return filtered_tokens
