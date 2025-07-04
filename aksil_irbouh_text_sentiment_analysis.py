# -*- coding: utf-8 -*-
"""Aksil_IRBOUH_Text_Sentiment_Analysis.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/16ltt_g1ozuiIQqmH2LzZGfQv1a870R9k

### Aksil IRBOUH - Student ID : 52200124019

# Natural Language Processing - Text Sentiment Analysis - Pattern Recognition Project

# Part 1 - Detecting sarcasm in a sentence
"""

import json
import tensorflow as tf

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

vocab_size = 10000
embedding_dim = 16
max_length = 100
trunc_type='post'
padding_type='post'
oov_tok = "<OOV>"
training_size = 20000

!wget --no-check-certificate \
    https://storage.googleapis.com/learning-datasets/sarcasm.json \
    -O /tmp/sarcasm.json

with open("/tmp/sarcasm.json", 'r') as f:  #We load the sarcasm json file using the json library
    datastore = json.load(f)

sentences = []   #We create lists for the headlines and the labels, we don't use urls
labels = []

for item in datastore:                    #We iterate through the json by loading the requisite values into a Python list
    sentences.append(item['headline'])
    labels.append(item['is_sarcastic'])

training_sentences = sentences[0:training_size]  #Seperating training and testing sets using Python list slicing
testing_sentences = sentences[training_size:]
training_labels = labels[0:training_size]
testing_labels = labels[training_size:]

tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_tok) #We start the preprocessing on the text
tokenizer.fit_on_texts(training_sentences)    #We create tokens for every word in the training corpus

word_index = tokenizer.word_index

training_sequences = tokenizer.texts_to_sequences(training_sentences)  #We turn our sentences into sequences of tokens
training_padded = pad_sequences(training_sequences, maxlen=max_length, padding=padding_type, truncating=trunc_type)  #We pad them to the same length

testing_sequences = tokenizer.texts_to_sequences(testing_sentences)  #We do the same for our testing sentences
testing_padded = pad_sequences(testing_sequences, maxlen=max_length, padding=padding_type, truncating=trunc_type)

import numpy as np
training_padded = np.array(training_padded)
training_labels = np.array(training_labels)
testing_padded = np.array(testing_padded)
testing_labels = np.array(testing_labels)

model = tf.keras.Sequential([  #Creation of our Neural Network
    tf.keras.layers.Embedding(vocab_size, embedding_dim, input_length=max_length), #The top layer is an embedding where the direction of each word will be learned epoch by epoch
    tf.keras.layers.GlobalAveragePooling1D(),  #We pool, it means we add up the vectors
    tf.keras.layers.Dense(24, activation='relu'), #We feed it into a Deep Neural Network
    tf.keras.layers.Dense(1, activation='sigmoid')
])
model.compile(loss='binary_crossentropy',optimizer='adam',metrics=['accuracy'])

num_epochs = 30  #We train our model
history = model.fit(training_padded, training_labels, epochs=num_epochs, validation_data=(testing_padded, testing_labels), verbose=2)

"""We have 96% accuracy for our training data and 84% for our testing set."""

model.summary()

import matplotlib.pyplot as plt


def plot_graphs(history, string):
  plt.plot(history.history[string])
  plt.plot(history.history['val_'+string])
  plt.xlabel("Epochs")
  plt.ylabel(string)
  plt.legend([string, 'val_'+string])
  plt.show()

plot_graphs(history, "accuracy")
plot_graphs(history, "loss")

reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])

def decode_sentence(text):
    return ' '.join([reverse_word_index.get(i, '?') for i in text])

print(decode_sentence(training_padded[0]))
print(training_sentences[2])
print(labels[2])

e = model.layers[0]
weights = e.get_weights()[0]
print(weights.shape) # shape: (vocab_size, embedding_dim)

import io

out_v = io.open('vecs.tsv', 'w', encoding='utf-8')
out_m = io.open('meta.tsv', 'w', encoding='utf-8')
for word_num in range(1, vocab_size):
  word = reverse_word_index[word_num]
  embeddings = weights[word_num]
  out_m.write(word + "\n")
  out_v.write('\t'.join([str(x) for x in embeddings]) + "\n")
out_v.close()
out_m.close()

try:
  from google.colab import files
except ImportError:
  pass
else:
  files.download('vecs.tsv')
  files.download('meta.tsv')

#Now we can predict the sarcasm of our own sentences

sentence = ["Sure, because binge-watching TV shows totally counts as exercise.", "Attack On Titan season finale showing this sunday night at cinema."]
sequences = tokenizer.texts_to_sequences(sentence) #We use the tokenizer we created earlier to convert our 2 sentences to sequences
#The words will have the same tokens as the training set
padded = pad_sequences(sequences, maxlen=max_length, padding=padding_type, truncating=trunc_type) #We pad the sequences to have the same dimensions as the training set
print(model.predict(padded))

"""# Part 2 - Restaurant review"""

!pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

!pip install transformers requests beautifulsoup4 pandas numpy

from transformers import AutoTokenizer, AutoModelForSequenceClassification  #A tokenizer is going pass through a string and convert it into a sequence of numbers
import torch
import requests  #used to grab the data from Yelp website
from bs4 import BeautifulSoup
import re #regex function to extract comments that we want

#Initialization of our Model

tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')  #loading of our pretrained model

model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

#Calculation of Sentiment

tokens = tokenizer.encode("Exceptionnel", return_tensors='pt') #We replace our comment here

result = model(tokens)  #The output from the model is a one-hot encoding list of scores.

result.logits  #The position with the highest scores represent the sentiment rating. Here 2.0598 is the highest number so we return its position in the list which is 4

int(torch.argmax(result.logits))+1 #We get the highest value result. Pytorch rating is from 0 to 4 so we add 1 because our model's rating is from 1 to 5

#Reviews Collection

r = requests.get('https://www.yelp.com/biz/din-tai-fung-kuala-lumpur-2?osq=Restaurants') #We request the website

soup = BeautifulSoup(r.text, 'html.parser')  #r.text is the response

regex = re.compile('.*comment.*') #When we inspect reviews on Yelp web page we find out they belong to a class which starts with "comment".
                                  #So we're parsing our regex to our soup

results = soup.find_all('p', {'class':regex}) #We're looking for paragraphs that match our regex class "comment"

reviews = [result.text for result in results] #We use ".text" to remove html tags we don't need, we just keep the text

reviews

#Storing reviews and score in a dataframe

import numpy as np
import pandas as pd

df = pd.DataFrame(np.array(reviews), columns=['review']) #We get our reviews into a dataframe

df['review'].iloc[0] #We look at our first review stored in the dataframe

def sentiment_score(review):  #Function to convert a string into sentiment result
    tokens = tokenizer.encode(review, return_tensors='pt')
    result = model(tokens)
    return int(torch.argmax(result.logits))+1

sentiment_score(df['review'].iloc[1])

df['sentiment'] = df['review'].apply(lambda x: sentiment_score(x[:512])) #We loop through every reviews in a column using a lambda function

#Every NLP pipeline is limited as how many tokens we pass throuhg it, in our case the BERT model is limited to 512 tokens
#So we just grab the first 512 tokens from each review. It may influence the results for more accuracy we would need more tokens.

df

df['review'].iloc[3]

"""##End"""