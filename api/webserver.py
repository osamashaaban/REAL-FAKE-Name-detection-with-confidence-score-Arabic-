from flask import Flask, request
from environs import Env
from flask_restful import Resource, Api
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
import time
import pyarabic.araby as araby
from textblob import TextBlob
from tashaphyne.stemming import ArabicLightStemmer
import pickle
import nltk
import re

tok = Tokenizer(oov_token="oov")
nltk.download('punkt')

with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

model = load_model("./model.h5")

ArListem = ArabicLightStemmer()

app = Flask(__name__)

api = Api(app)

env = Env()

env.read_env()

port =  env("PORT")


def stem(text):
    
    zen = TextBlob(text)
    
    words = zen.words
    
    cleaned = list()
    for w in words:
        ArListem.light_stem(w)
        cleaned.append(ArListem.get_root())
    
    return " ".join(cleaned)

def normalizeArabic(text):
    
    text = text.strip()
    
    text = re.sub("[إأٱآا]", "ا", text)
    text = re.sub("ى", "ي", text)
    text = re.sub("ؤ", "ء", text)
    text = re.sub("ئ", "ء", text)
    text = re.sub("ة", "ه", text)
    
    noise = re.compile(""" ّ    | # Tashdid
                             َ    | # Fatha
                             ً    | # Tanwin Fath
                             ُ    | # Damma
                             ٌ    | # Tanwin Damm
                             ِ    | # Kasra
                             ٍ    | # Tanwin Kasr
                             ْ    | # Sukun
                             ـ     # Tatwil/Kashida
                         """, re.VERBOSE)
    
    text = re.sub(noise, '', text)
    
    text = re.sub(r'(.)\1+', r"\1\1", text)
    
    return araby.strip_tashkeel(text)
def clean_text(text):
    ## Remove punctuations
    text = re.sub('[%s]' % re.escape("""!"#$%&'()*+,،-./:;<=>؟?@[\]^_`{|}~"""), ' ', text)
    ## remove extra whitespace
    text = re.sub('\s+', ' ', text)  
    ## Convert text to lowercases
    text = text.lower()
    ## Remove numbers
    text = re.sub("\d+", " ", text)
    ## Remove Tashkeel
    text = normalizeArabic(text)
    #text = re.sub('\W+', ' ', text)
    text = re.sub('[A-Za-z]+',' ',text)
    text = re.sub(r'\\u[A-Za-z0-9\\]+',' ',text)
    ## remove extra whitespace
    text = re.sub('\s+', ' ', text)  
    #Stemming
    text = stem(text)
    return text


class CheckName(Resource):
    def get(self):
        return f"<h1>Hello from port {port}</h1>"

    def post(self):
        """
        Save the name to an existing dict key of "name".
        Then commence the proccess.
        """    
        try:       
            start = time.time()
            name = [request.form['data']]
            testing = []
            testing.append(clean_text(name[0]))
            
            padding_type='post'
            tok.fit_on_texts(name)
            sample_sequences = tokenizer.texts_to_sequences(testing)
            
            fakes_padded = pad_sequences(sample_sequences, padding=padding_type, maxlen=26)  
            
            classes = model.predict(fakes_padded)
            
            end = time.time() 
            excution_time = end - start
            out = classes[0][0]
            results = {"Name Confidence": float(round(out,5)),
                        "Excution Time(s)":round(excution_time,4)}
            return results
        except Exception as e:
                print(e)
                return "Erroe!!"


api.add_resource(CheckName, '/')


if __name__ == '__main__':
    app.run(debug=True,port = port,load_dotenv=True,host="0.0.0.0")
    

    