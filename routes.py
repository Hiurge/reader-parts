import os

import collections

from flask import render_template, flash, redirect, request
from wtforms import StringField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired


import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

import re
import spacy
import nltk
#nltk.download('stopwords')
#nltk.download('wordnet')
#nltk.download('punkt')

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize

import textblob
from textblob import TextBlob

from app import app
from app.DataBaseManager import DataBaseManager
from app.reader_input_helpers import get_input_text
from app.TextCleaner import *
from app.TextCleaner import word_counts_text_cleaner, entity_recognition_text_cleaner, sentiment_text_cleaner, handy_cleaner, kw_cleaner
from app.TextToFrame import TextToFrame
from app.TextFeatureEngineering import TextFeatureEngineering
from app.text_statistics_helpers import text_values_counts_dict, select_n_most_occuring_phrases, text_sentiment, get_sentences_with_keyword, phrases_sentiment_in_respect_to_full_text
from app.reader_output_text_helpers import sentences_to_spanned_html, sentences_to_html
from app.PlottingTextData import plot_word_counts, plot_words_sent
from app.forms.reader_form import ReaderForm
from app.forms.keywords_form import AddKeywordsForm, RmvKeywordsForm, RmvSetForm
from app.forms.comparer_form import CompareForm




# Main routes file. Contains all sub-pages code and their imports:
# 1. Index
# 2. Keywords
# 3. Reader
# 4. Form [comparer page]
# 5. (...) tbd.



# 1. INDEX
# --------

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html', title='Home')


# 2. KEYWORDS
# -----------

@app.route('/keywords', methods=['GET', 'POST'])
def keywords_main_page():

	# Clean, unify later
	credentials = { 'dbname': 'reader_keywords', 'dbuser': 'luke'} # TEMP: into a file.
	keywords_table_name = 'keywords_test'
	keywords_columns_types = 	[
									#('id serial', 'PRIMARY KEY'),
									('set_name', 'text'),
									('keyword', 'text'),
									# ...
								]
	DBM = DataBaseManager(credentials, keywords_table_name, keywords_columns_types)


	add_kwds_form = AddKeywordsForm()
	if add_kwds_form.validate_on_submit():
		
		keywords = add_kwds_form.add_kwds.data
		set_name = add_kwds_form.add_kwds_set_name.data
		
		DBM.add_keywords(set_name, keywords)

		x = 'add'
		print(x)

	rmv_kwds_form = RmvKeywordsForm()
	if rmv_kwds_form.validate_on_submit():
		
		keywords = rmv_kwds_form.rmv_keywords.data
		set_name = rmv_kwds_form.rmv_kwds_set_name.data

		DBM.rmv_keywords(set_name, keywords)

		x = 'rm kw'
		print(x)

	rmv_set_form = RmvSetForm()
	if rmv_set_form.validate_on_submit():

		set_name = rmv_set_form.rmv_set_name.data

		DBM.rmv_kwd_set(set_name)

		x = 'rm set'
		print(x)

	# ADD DISPLAY CURRENT KWS
	DBM.get_names_of_sets()

	return render_template('keywords.html', title='Keywords',add_kwds_form=add_kwds_form, rmv_kwds_form=rmv_kwds_form, rmv_set_form=rmv_set_form, )



# 3. KEYWORDS
# -----------

@app.route('/reader', methods=['GET', 'POST'])
def reader_main_page():

	# Clean, unify later
	credentials = { 'dbname': 'reader_keywords', 'dbuser': 'luke'} # TEMP: into a file.
	keywords_table_name = 'keywords_test'
	keywords_columns_types = 	[
									#('id serial', 'PRIMARY KEY'),
									('set_name', 'text'),
									('keyword', 'text'),
									# ...
								]

	DBM = DataBaseManager(credentials, keywords_table_name, keywords_columns_types)
	RF = ReaderForm()
	
	link_validation = RF.link_field.validate(RF)
	select_validation = RF.select.validate(RF)

	if select_validation and not link_validation:
		set_name = RF.select.data
		keywords =  DBM.get_set_keywords(set_name)
		return render_template('reader.html', title='Reader', reader_form=RF, keywords=keywords)

	if link_validation and select_validation:

		
		##### Universal Base.
		set_name = RF.select.data
		keywords = DBM.get_set_keywords(set_name)
		keywords = [k.lower() for k in keywords]
		full_text = get_input_text(RF.link_field.data)

		# Computation costs reduction - further fix.
		if RF.reader_mode_select.data == 'Keyword sentences + hints':
			READER_MODE_FRAME_TYPE = 'Full'		
		# elif RF.reader_mode_select.data == 'Keyword sentences':
		# 	READER_MODE_FRAME_TYPE = 'Handy'
		else:
			READER_MODE_FRAME_TYPE = 'Full'

		# General statistics:
		# --------------------------------------------------------

		# Word counts
		general_word_counts = text_values_counts_dict(full_text)

		# Full text sentiment [useless?]
		full_text_sentiment = text_sentiment(full_text) # int 
		

		# TextFrame ( future: CompCost minimalization: df types (handy, spec, lightweight)
		# - Text to sentences frame
		# - Feature Engineering
		# ---------------------

		# Frame with a raw and cleaned sentences.
		TTF = TextToFrame(full_text, keywords)
		df_sentences = TTF.prepare_sentence_dataframe()

		# Dataframe with defined features pick.
		TTE = TextFeatureEngineering(df_sentences, keywords)
		df = TTE.run(READER_MODE_FRAME_TYPE)

		# Sentences with a keyword
		keyword_sentences = get_sentences_with_keyword(df)




		# DataFrame to Results: Minimalization
		# ------------------------------------

		# Keywords display.
		keywords_display = ', '.join([k for k in keywords if k != ''])


		# Features out

		# N nouns display.
		if RF.nouns_display.data == True:
			n_nouns = RF.nouns_amount.data
			nouns = select_n_most_occuring_phrases(df, 'nouns', general_word_counts, n_nouns)
		else:
			nouns = None

		# N entities display.
		if RF.ent_display.data == True:
			n_ent = RF.ent_amount.data
			ents_org = select_n_most_occuring_phrases(df, 'ent_org', general_word_counts, n_ent)

			# ents org sentiment test:
			all_sentences = sent_tokenize(full_text) 
			phrases_group = ents_org.split(', ')
			ents_org_sent = phrases_sentiment_in_respect_to_full_text(all_sentences, phrases_group)
			for k, v in ents_org_sent.items():
				print(k, v)

			ents_p = select_n_most_occuring_phrases(df, 'ent_person', general_word_counts, n_ent)
			ents_gpe = select_n_most_occuring_phrases(df, 'ent_gpe', general_word_counts, n_ent)
			ents_norp = select_n_most_occuring_phrases(df, 'ent_norp', general_word_counts, n_ent)
		else:
			ents_org, ents_p, ents_gpe, ents_norp = None, None, None, None
		

		if RF.summary_display.data == True:
			summary_part = True
		else:
			summary_part = None
		




		if RF.graphs_display.data == True:
			fig1 =plot_word_counts(general_word_counts, 10)
			fig3 =plot_words_sent(ents_org_sent)
			graph_test = '/static/images/word_counts_graph_xx.png' # Recode
			graph_test3 = '/static/images/word_counts_graph_xx3.png' # Recode
			graphs = [graph_test, graph_test3]
		else:
			graphs = None



		# Render template display
		featured_sentences = []
		for i in range(len(df)):
		    idx = i
		    is_sent = df.loc[i, 'keywords']
		    words = str(df.loc[i, 'named_ents_nouns'])
		    sent = str(df.loc[i, 'sentence'])
		    featured_sentence = [idx, is_sent, words, sent]
		    featured_sentences.append(featured_sentence)



		#reader_frame_type_validation = RF.reader_frame_select.data
		reader_frame = RF.reader_mode_select.data
		if RF.reader_mode_select.data == 'Keyword sentences + hints':
			sentences_html = sentences_to_spanned_html(featured_sentences)
		elif RF.reader_mode_select.data == 'Keyword sentences':
			sentences_html = sentences_to_html(featured_sentences)





		return render_template('reader.html', title='Reader', spanned_test=sentences_html, reader_form=RF, summary_part=summary_part, graphs=graphs, keywords=keywords_display, ks=keyword_sentences, eo=ents_org, nn=nouns, ep=ents_p, eg=ents_gpe, en=ents_norp)

	# Display link contents [from above]. Graphs
	# Modify contnet according to a settings.

	return render_template('reader.html', title='Reader', reader_form=RF)




# 4. COMPARER.
# ------------

@app.route('/form', methods=['GET', 'POST'])
def input_data():

	class DataFromURL():	
		def get_raw_page_contents(self, link):
			html = urllib.request.urlopen(link).read()
			soup = BeautifulSoup(html, "lxml")
			return soup
		def run(self, link):
			out = self.get_raw_page_contents(link)
			return out

	scraper = DataFromURL()
	form = CompareForm()

	if form.validate_on_submit():

		
		link_1 = form.input_link1.data
		link_2 = form.input_link2.data
		
		# GET DATA

		link_1_contents = scraper.run(link_1)
		link_2_contents = scraper.run(link_2)

		# PREPARE

		# UPLOAD TO DB - OPTIONAL FOR NOW

		# THROUGH A MODEL

		# GET OUTPUT

		# VISUALISE

		# SHOW RESULTS

		data_out = {
		'link1' : link_1,
		'link2' : link_2,
		'link1_contents' : link_1_contents,
		'link2_contents' : link_2_contents,
		}
		return render_template('result.html', title='Result', data_out=data_out) # hmm.

	else:
		flash('Link 1 and Link 2 are required')
		return render_template('form.html', title='Compare', form=form)