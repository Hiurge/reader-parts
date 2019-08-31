

# def text_to_df_keywords_only(text, keywords):
# 	sentences = sent_tokenize(text)
# 	df = pd.DataFrame(sentences, columns=['sentence'])
	
# 	for k in keywords:
# 		df[k] = 0
# 		for i in range(len(df)):
# 			sentence = df.loc[i, 'sentence']
# 			words = handy_cleaner(sentence).split()
# 			if k in words:
# 				df.loc[i, k] += 1
# 	return df


# def get_dependencies():
# 	return ', '.join(['('+w.text+' '+w.dep_+')' for w in nlp(text)])





# # =========================================================================================================






# FLASK CONFIG PATHS
# ------------------

# PEOPLE_FOLDER = os.path.join('static', 'people_photo')

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER

# @app.route('/')
# @app.route('/index')
# def show_index():
#     full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'shovon.jpg')

# ================================================================
# ================================================================
# ================================================================
# ========================== NOT USED ============================
# ================================================================
# ================================================================


# def filter_keyword_sentences(text, keyword):
# 	sentences_with_keyword = []
# 	for sent in sent_tokenize(text): 
# 		sent = handy_cleaner(sent)
# 		for w in sent.split(): # ?!
# 			if w == keyword:
# 				sentences_with_keyword.append(sent)
# 	sentences_with_keyword = list(set(sentences_with_keyword))
# 	return sentences_with_keyword # list

# def filter_keywords_sentences(text, keywords):
# 	keyword_sentences = {}
# 	for keyword in keywords:
# 		keyword_sentences[keyword] = filter_keyword_sentences(text, keyword)
# 	return keyword_sentences # dict




# TEXT ENTITIES GRUPPED [OR ANY DICT GRUPPED] (Unused)
# ================================================================

# def text_entities(text):
# 	text = entity_recognition_text_cleaner(text)
# 	entities_with_labels = [(w.text, w.label_) for w in nlp(str(text)).ents]
# 	#ent_labels = [w.label_ for w in nlp(text).ents]
# 	#ent_words = [w.text for w in nlp(text).ents]
# 	return entities_with_labels
# #entities = text_entities(full_text) # check 


# # Group entities:
# def group_entities(entities):
# 	entity_groups = {}
	
# 	for e in entities:
# 		entity_groups[e[1]] = []

# 	for e in entities:
# 		entity_groups[e[1]].append(e[0])

# 	for e in entity_groups.keys():
# 		#print(e, entity_groups[e])
# 		entity_groups[e] = list(set(entity_groups[e]))

# 	entity_groups_counts = entity_groups.copy()
# 	return entity_groups
# #groupped_entities = group_entities(entities) # dict # entities_to_filter = ['ORG', 'PERSON', 'NORP' , 'GPE']


