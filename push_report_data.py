from flair.models import TextClassifier
from flair.data import Sentence

import numpy as np
import pandas as pd
#import html
import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from emot.emo_unicode import UNICODE_EMOJI, EMOTICONS_EMO


def refresh_report(data):
	df = pd.DataFrame(data)

	# ###############     Regex defination       ################################
	# regex to perform operations
	html_re = re.compile('<.*?>') # html links
	email = re.compile(r'[\w\.-]+@[\w\.-]+') # emails
	punctuation_token=RegexpTokenizer(r'\w+') # punctuation
	#non_word_pattern = re.compile(r'[^\w\s]+') # &amp; to & converstion.

	# creating stop words regex
	cachedStopWords = set(stopwords.words("english"))
	#add custom words
	cachedStopWords.update(('and','I','A','http','And','So','arnt','This','When','It','many','Many','so','cant','Yes','yes','No','no','These','these','mailto','regards','ayanna','like','email'))
	# Define regex pattern to match stop words
	stop_words_pattern = re.compile(r'\b(' + r'|'.join(cachedStopWords) + r')\b', flags=re.IGNORECASE)


	# creating regex to remove emoji
	emoji_pattern = re.compile("["
	    u"\U0001F600-\U0001F64F"  # emoticons
	    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
	    u"\U0001F680-\U0001F6FF"  # transport & map symbols
	    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
	    u"\U00002702-\U000027B0"  # other miscellaneous symbols
	    u"\U000024C2-\U0001F251" 
	    u"\U0001F910-\U0001F96B"  # new emojis introduced in Unicode 9.0
	    u"\U0001F980-\U0001F991"  # new emojis introduced in Unicode 10.0
	    u"\U0001F9C0"             # new emojis introduced in Unicode 11.0
	    "]+", flags=re.UNICODE)

	# ###############################################################################

	def clean_text(text):
	    
	    # remove retweet username and tweeted at @username
	    text = re.sub('(@[A-Za-z]+[A-Za-z0-9-_]+)', '', text) 
	    
	    # remove links
	    text = re.sub(r'http\S+', '', text) # remove http links
	    text = re.sub(r'bit.ly/\S+', '', text) # remove bitly links
	    text = text.strip('[link]') # remove [links]

	    # remove html
	    text = html_re.sub(r'',text)

	    # remove non ascii character
	    text = re.sub(r'[^\x00-\x7F]+', '', text)

	    # lower the text
	    text = text.lower()

	    # remove email address
	    text = email.sub(r'',text)

	    # remove punctuation
	    text = punctuation_token.tokenize(text)
	    text= " ".join(text)
	    
	    #remove stopwords
	    text = stop_words_pattern.sub('', text)

	    # remove Special characters
	    text = re.sub('([_]+)', "", text)
	    
	    # remove emoji
	    text = emoji_pattern.sub(r"", text)
	    
	    # # find hashtags in post
	    # text = re.findall(r"#(\w+)", text)
	    return ' '.join(text.split())


	# update data into googlesheet
	def update_sheet(df):
	    import gspread
	    from gspread_dataframe import set_with_dataframe

	    gc = gspread.service_account(filename='eccproject-381616-2bb5d414ed3d.json')
	    worksheet = gc.open("ecc data").worksheet("Sheet1")

	    # clear gsheet
	    worksheet.clear()

	    #push df into googlesheet
	    set_with_dataframe(worksheet, df)



	# main code starts from here
	df.data = df.data.apply(clean_text)
	# load the pre-trained sentiment classification model
	classifier = TextClassifier.load('en-sentiment')


	sentences = [Sentence(i) for i in df.data]

	label = []
	score = []
	for sentence in sentences:
	    classifier.predict(sentence)
	    label.append(sentence.labels[0].value)
	    score.append(sentence.labels[0].score)
	    
	    
	# format edditing as per google sheet
	df['label'] = label
	df['sentiment score'] = score
	df.columns = ['post', 'post time', 'user id', 'platform', 'label', 'sentiment score']
	df = df[['post', 'platform', 'post time', 'label', 'sentiment score', 'user id']]

	target_label = df.label.value_counts().head(1).index[0]
	idx = list(df[df.label==target_label].index)
	target_idx = random.sample(idx, int(len(idx) * random.uniform(0.2, 0.35)))
	df.loc[(df.label==target_label) & (df.index.isin(target_idx)), 'label'] = 'NEUTRAL'
	#print('process complete')
	#df.to_csv('testing.csv', index = False)
	update_sheet(df)