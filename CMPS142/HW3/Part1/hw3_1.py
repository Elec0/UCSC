import sys
import string
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

def readFile(fileName):
	f = open(fileName, "r")
	file = f.read()
	f.close()
	return file

reload(sys)
sys.setdefaultencoding('utf-8')

	
# Read the whole file
# Note: it is tab separated: label \t text message
file = readFile("FilesForHW3Part1/train_file_cmps142_hw3")

# STEP1: Convert the file to lowercase
file = file.lower()

# Split the file into individual lines
lines = file.split("\n")

# Parse the file into label and text arrays
# Parsed is 2d array, parsed[i][0] = label, parsed[i][1] = text
parsed = []
for i in range(0, len(lines)):
	parsed.append(lines[i].split("\t"))


# STEP2: Tokenize
# Tokens is a 2d array, with label,[list of tokens]
tokens = []
for val in parsed:
	# Ensure we have label and text data to tokenize
	if len(val) == 2:
		tokens.append([val[0], nltk.word_tokenize(val[1])])
		
# STEP2 (a):
# print "Distinct tokens: ", len(set(allTokens))
#	Output: Distinct tokens:  8703

# STEP3: Remove stopwords
s_words = stopwords.words('english')
for val in tokens:
	# Remove all the stopwords in val[1]
	# Taken from https://stackoverflow.com/questions/4211209/remove-all-the-elements-that-occur-in-one-list-from-another
	nostops = [tok for tok in val[1] if tok not in s_words]
	val[1] = nostops
	
# STEP4: Remove punctuation
punctuation = string.punctuation
for val in tokens:
	nopunc = [tok for tok in val[1] if tok not in list(punctuation)]
	val[1] = nopunc
	
# STEP5: Stemming
stemmer = PorterStemmer()
for val in tokens:
	# Loop through all the tokens, get the stemmed versions, then reset the list to that list
	stems = []
	for token in val[1]:
		stems.append(stemmer.stem(token))
	val[1] = stems

# STEP5 (a):
# print tokens[10]
# 	Output: ["'ve", u'search', 'right', u'word', 'thank', 'breather', u'promis', 'wont', 'take', 'help', u'grant', 'fulfil', u'promis', u'wonder', u'bless', u'time']

# STEP6: Ignoring infrequent tokens
# We need to count the tokens to be able to do this. So we'll use a dictionary with the tokens as keys and values as the counts
# As prior, most of this code could be integrated into a single loop, but it's not *too* slow at the moment.
tok_dict = {}
for val in tokens:
	for tok in val[1]:
		# If the dict has the token as a key
		if tok in tok_dict:
			# Increment it's count
			tok_dict[tok] = tok_dict[tok] + 1
		else: # Initialize the token
			tok_dict[tok] = 1

# Now, check all tokens to make sure they have counts greater than 5
# If they do not, remove them
threshold = 5
for val in tokens:
	new_lst = []
	for tok in val[1]:
		if tok_dict[tok] > threshold:
			new_lst.append(tok)
	
	val[1] = new_lst

# STEP6 (a):
# Total number of distinct tokens in the token set:
# 	Vocabulary: 1184


# STEP7:
# Convert the list of tokens into a dictionary that counts the number of instances of a word per message
# It's literally just step 6 but for each message, not globally
# Note: we are changing the entire training set here to a different data structure
for val in tokens:
	cur_dict = {}
	for tok in val[1]:
		if tok in cur_dict:
			cur_dict[tok] = cur_dict[tok] + 1
		else:
			cur_dict[tok] = 1
	val[1] = cur_dict

# STEP7 (a):
# We need to output that data to a csv file
# Structure: 
# header: word[i]
# count[i], (...), label

csv = open("HW3_steele_train.csv", "w+")
first = True
for tok in tok_dict:
	if not first: csv.write(", ")
	else: first = False
	csv.write(tok)
csv.write(", label")
	
for val in tokens:
	cur_line = ""
	first = True
	for tok in tok_dict:
		if not first: cur_line += ", "
		else: first = False
		if tok in val[1]:
			cur_line += str(val[1][tok])
		else: 
			cur_line += "0"
		
	csv.write(cur_line + ", " + val[0] + "\n")
csv.close()

