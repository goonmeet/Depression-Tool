# importing word breaker
from word_breaking import word_breaker
import re, sys
import string
import nltk
import pandas as pd
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer

from nltk.stem import PorterStemmer, WordNetLemmatizer
printable = set(string.printable)
from nltk.corpus import stopwords

stopWords = ["'s","'t","'re","i'm","n't","cq","the","mention","_URL_","_MENTION_","rt","a", "a's", "abaft", "able", "aboard", "about", "above", "abst", "accordance", "according", "accordingly", "across", "act", "actually", "added", "adj", "affected", "affecting", "affects", "afore", "aforesaid", "after", "afterwards", "again", "against", "agin", "ago", "ah", "ain't", "aint", "albeit", "all", "allow", "allows", "almost", "alone", "along", "alongside", "already", "also", "although", "always", "am", "american", "amid", "amidst", "among", "amongst", "an", "and", "anent", "announce", "another", "any", "anybody", "anyhow", "anymore", "anyone", "anything", "anyway", "anyways", "anywhere", "apart", "apparently", "appear", "appreciate", "appropriate", "approximately", "are", "aren", "aren't", "arent", "arise", "around", "as", "aside", "ask", "asking", "aslant", "associated", "astride", "at", "athwart", "auth", "available", "away", "awfully", "b", "back", "bar", "barring", "be", "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand", "begin", "beginning", "beginnings", "begins", "behind", "being", "believe", "below", "beneath", "beside", "besides", "best", "better", "between", "betwixt", "beyond", "biol", "both", "brief", "briefly", "but", "by", "c", "c'mon", "c's", "ca", "came", "can", "can't", "cannot", "cant", "cause", "causes", "certain", "certainly", "changes", "circa", "clearly", "close", "co", "com", "come", "comes", "concerning", "consequently", "consider", "considering", "contain", "containing", "contains", "corresponding", "cos", "could", "couldn", "couldn't", "couldnt", "couldst", "course", "currently", "d", "dare", "dared", "daren", "dares", "daring", "date", "definitely", "described", "despite", "did", "didn", "didn't", "different", "directly", "do", "does", "doesn", "doesn't", "doing", "don", "don't", "done", "dost", "doth", "down", "downwards", "due", "during", "durst", "e", "each", "early", "ed", "edu", "effect", "eg", "eight", "eighty", "either", "else", "elsewhere", "em", "end", "ending", "english", "enough", "entirely", "er", "ere", "especially", "et", "et-al", "etc", "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "ex", "exactly", "example", "except", "excepting", "f", "failing", "far", "few", "ff", "fifth", "first", "five", "fix", "followed", "following", "follows", "for", "former", "formerly", "forth", "found", "four", "from", "further", "furthermore", "g", "gave", "get", "gets", "getting", "give", "given", "gives", "giving", "go", "goes", "going", "gone", "gonna", "got", "gotta", "gotten", "greetings", "h", "had", "hadn", "hadn't", "happens", "hard", "hardly", "has", "hasn", "hasn't", "hast", "hath", "have", "haven", "haven't", "having", "he", "he'd", "he'll", "he's", "hed", "hello", "help", "hence", "her", "here", "here's", "hereafter", "hereby", "herein", "heres", "hereupon", "hers", "herself", "hes", "hi", "hid", "high", "him", "himself", "his", "hither", "home", "hopefully", "how", "how's", "howbeit", "however", "hundred", "i", "i'd", "i'll", "i'm", "i've", "id", "ie", "if", "ignored", "ill", "im", "immediate", "immediately", "importance", "important", "in", "inasmuch", "inc", "indeed", "index", "indicate", "indicated", "indicates", "information", "inner", "inside", "insofar", "instantly", "instead", "into", "invention", "inward", "is", "isn", "isn't", "it", "it'd", "it'll", "it's", "itd", "its", "itself", "j", "just", "k", "keep", "keeps", "kept", "kg", "km", "know", "known", "knows", "l", "large", "largely", "last", "lately", "later", "latter", "latterly", "least", "left", "less", "lest", "let", "let's", "lets", "like", "liked", "likely", "likewise", "line", "little", "living", "ll", "long", "look", "looking", "looks", "ltd", "m", "made", "mainly", "make", "makes", "many", "may", "maybe", "mayn", "me", "mean", "means", "meantime", "meanwhile", "merely", "mg", "mid", "midst", "might", "mightn", "million", "mine", "minus", "miss", "ml", "more", "moreover", "most", "mostly", "mr", "mrs", "much", "mug", "must", "mustn", "mustn't", "my", "myself", "n", "na", "name", "namely", "nay", "nd", "near", "nearly", "neath", "necessarily", "necessary", "need", "needed", "needing", "needn", "needs", "neither", "never", "nevertheless", "new", "next", "nigh", "nigher", "nighest", "nine", "ninety", "nisi", "no", "nobody", "non", "none", "nonetheless", "noone", "nor", "normally", "nos", "not", "noted", "nothing", "notwithstanding", "novel", "now", "nowhere", "o", "obtain", "obtained", "obviously", "of", "off", "often", "oh", "ok", "okay", "old", "omitted", "on", "once", "one", "ones", "oneself", "only", "onto", "open", "or", "ord", "other", "others", "otherwise", "ought", "oughtn", "our", "ours", "ourselves", "out", "outside", "over", "overall", "owing", "own", "p", "page", "pages", "part", "particular", "particularly", "past", "pending", "per", "perhaps", "placed", "please", "plus", "poorly", "possible", "possibly", "potentially", "pp", "predominantly", "present", "presumably", "previously", "primarily", "probably", "promptly", "proud", "provided", "provides", "providing", "public", "put", "q", "qua", "que", "quickly", "quite", "qv", "r", "ran", "rather", "rd", "re", "readily", "real", "really", "reasonably", "recent", "recently", "ref", "refs", "regarding", "regardless", "regards", "related", "relatively", "research", "respecting", "respectively", "resulted", "resulting", "results", "right", "round", "run", "s", "said", "same", "sans", "save", "saving", "saw", "say", "saying", "says", "sec", "second", "secondly", "section", "see", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent", "serious", "seriously", "seven", "several", "shall", "shalt", "shan", "shan't", "she", "she'd", "she'll", "she's", "shed", "shell", "shes", "short", "should", "shouldn", "shouldn't", "show", "showed", "shown", "showns", "shows", "significant", "significantly", "similar", "similarly", "since", "six", "slightly", "small", "so", "some", "somebody", "somehow", "someone", "somethan", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "special", "specifically", "specified", "specify", "specifying", "still", "stop", "strongly", "sub", "substantially", "successfully", "such", "sufficiently", "suggest", "summat", "sup", "supposing", "sure", "t", "t's", "take", "taken", "taking", "tell", "tends", "th", "than", "thank", "thanks", "thanx", "that", "that'll", "that's", "that've", "thats", "the", "thee", "their", "theirs", "them", "themselves", "then", "thence", "there", "there'll", "there's", "there've", "thereafter", "thereby", "thered", "therefore", "therein", "thereof", "therere", "theres", "thereto", "thereupon", "these", "they", "they'd", "they'll", "they're", "they've", "theyd", "theyre", "thine", "think", "third", "this", "tho", "thorough", "thoroughly", "those", "thou", "though", "thoughh", "thousand", "three", "thro", "throug", "through", "throughout", "thru", "thus", "thyself", "til", "till", "tip", "to", "today", "together", "too", "took", "touching", "toward", "towards", "tried", "tries", "true", "truly", "try", "trying", "ts", "twas", "tween", "twere", "twice", "twill", "twixt", "two", "twould", "u", "un", "under", "underneath", "unfortunately", "unless", "unlike", "unlikely", "until", "unto", "up", "upon", "ups", "us", "use", "used", "useful", "usefully", "usefulness", "uses", "using", "usually", "v", "value", "various", "ve", "versus", "very", "via", "vice", "vis-a-vis", "viz", "vol", "vols", "vs", "w", "wanna", "want", "wanting", "wants", "was", "wasn", "wasn't", "wasnt", "way", "we", "we'd", "we'll", "we're", "we've", "wed", "welcome", "well", "went", "were", "weren", "weren't", "werent", "wert", "what", "what'll", "what's", "whatever", "whats", "when", "when's", "whence", "whencesoever", "whenever", "where", "where's", "whereafter", "whereas", "whereby", "wherein", "wheres", "whereupon", "wherever", "whether", "which", "whichever", "whichsoever", "while", "whilst", "whim", "whither", "who", "who'll", "who's", "whod", "whoever", "whole", "whom", "whomever", "whore", "whos", "whose", "whoso", "whosoever", "why", "why's", "widely", "will", "willing", "wish", "with", "within", "without", "won't", "wonder", "wont", "words", "world", "would", "wouldn", "wouldn't", "wouldnt", "wouldst", "www", "x", "y", "ye", "yes", "yet", "you", "you'd", "you'll", "you're", "you've", "youd", "your", "youre", "yours", "yourself", "yourselves", "z", "zero"]
stopWords_short=["abaft", "aboard", "about", "above", "across", "afore", "aforesaid", "after", "again", "against", "agin", "ago", "aint", "albeit", "all", "almost", "alone", "along", "alongside", "already", "also", "although", "always", "am", "american", "amid", "amidst", "among", "amongst", "anent", "another", "any", "anybody", "anyone", "anything", "aren", "aren't", "around", "aslant", "astride", "athwart", "away", "back", "bar", "barring", "because", "been", "before", "behind", "being", "below", "beneath", "beside", "besides", "best", "better", "between", "betwixt", "beyond", "both", "can", "can't", "cannot", "certain", "circa", "close", "concerning", "considering", "cos", "could", "couldn", "couldn't", "couldst", "dare", "dared", "daren", "dares", "daring", "despite", "did", "didn", "didn't", "different", "directly", "do", "does", "doesn", "doesn't", "doing", "don", "don't", "done", "dost", "doth", "down", "during", "durst", "each", "early", "either", "em", "english", "enough", "er", "ere", "even", "ever", "every", "everybody", "everyone", "everything", "except", "excepting", "failing", "far", "few", "first", "five", "following", "four", "from", "further", "gonna", "gotta", "had", "hadn", "hadn't", "hard", "has", "hasn", "hasn't", "hast", "hath", "have", "haven", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "high", "him", "himself", "his", "home", "how", "how's", "howbeit", "however", "i", "i'd", "i'll", "i'm", "i've", "id", "ill", "immediately", "important", "inside", "instantly", "isn", "isn't", "it's", "its", "itself", "just", "large", "last", "later", "least", "left", "less", "lest", "let", "let's", "like", "likewise", "little", "living", "long", "many", "may", "mayn", "me", "mid", "midst", "might", "mightn", "mine", "minus", "more", "most", "much", "must", "mustn", "mustn't", "my", "myself", "near", "neath", "need", "needed", "needing", "needn", "needs", "neither", "never", "nevertheless", "new", "next", "nigh", "nigher", "nighest", "nisi", "nobody", "none", "nor", "nothing", "notwithstanding", "now", "off", "often", "once", "one", "oneself", "only", "onto", "open", "other", "otherwise", "ought", "oughtn", "our", "ours", "ourselves", "out", "outside", "over", "own", "past", "pending", "per", "perhaps", "plus", "possible", "present", "probably", "provided", "providing", "public", "qua", "quite", "rather", "re", "real", "really", "respecting", "right", "round", "s", "same", "sans", "save", "saving", "second", "several", "shall", "shalt", "shan", "shan't", "she", "she'd", "she'll", "she's", "shed", "shell", "short", "should", "shouldn", "shouldn't", "since", "six", "small", "so", "some", "somebody", "someone", "something", "sometimes", "soon", "special", "still", "summat", "supposing", "sure", "t", "than", "that's", "thee", "theirs", "them", "themselves", "there's", "they'd", "they'll", "they're", "they've", "thine", "tho", "those", "thou", "though", "three", "thro", "through", "throughout", "thru", "thyself", "till", "today", "together", "too", "touching", "toward", "towards", "true", "twas", "tween", "twere", "twill", "twixt", "two", "twould", "under", "underneath", "unless", "unlike", "until", "unto", "up", "upon", "us", "used", "usually", "ve", "versus", "very", "via", "vice", "vis-a-vis", "wanna", "wanting", "wasn", "wasn't", "way", "we", "we'd", "we'll", "we're", "we've", "well", "were", "weren", "weren't", "wert", "what", "what's", "whatever", "when", "when's", "whencesoever", "whenever", "where", "where's", "whereas", "whether", "which", "whichever", "whichsoever", "while", "whilst", "who", "who's", "whoever", "whole", "whom", "whore", "whose", "whoso", "whosoever", "why", "why's", "within", "without", "won't", "wont", "would", "wouldn", "wouldn't", "wouldst", "ye", "yet", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"]
punctuation = list(string.punctuation)
#print punctuation
punctuation.remove("'")
stop = stopWords + punctuation
#stop.remove("i")
#stop.remove("my")
#stop.remove("i'm")
#stop.remove("don't")
#+ ["x_num__mention_","u","x_num__mention","x_num_","us","_num_","must","would","however",'rt', 'via','``','http',"RT","''","...","'RT","_mention_","_url_","_mention_."]
def preprocess_tweet(tweet):

    print "Actual--->"+tweet

    # remove url from tweet
    tweet = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', ' ', tweet)

    # remove rt
    tweet = tweet.replace("RT", "")

    # remove non-ascii characters
    tweet = filter(lambda x: x in printable, tweet)
    #tweet = tweet.encode('ascii',errors='ignore')

    # additional preprocessing
    tweet = tweet.replace("\n", "").replace(" https","").replace("http","")

    # punctuation padding
    tweet = re.sub('([.,!?()])', r' \1 ', tweet)
    tweet = re.sub('\s{2,}', ' ', tweet)

    #remove numbers
    #tweet = re.sub(r'[\d-]+', ' ', tweet)

    #remove mentions
    tweet = re.sub(r'(@\w+)', ' ', tweet)

    #for multiple spaces
    #tweet = re.sub(r'(\s+)', ' ', tweet)

    #remove punctuation
    for c in punctuation:
        tweet= tweet.replace(c,"")


    #print tweet
    #tweet = [word for word in tweet.split(" ") if word not in stop ]

    #stemming
    #port = PorterStemmer()
    #tweet=" ".join([port.stem(i) for i in tweet.split()])
    #print "STEMMED------->"+tweet


    #lemmatize
    #wnl = WordNetLemmatizer()
    #tweet= " ".join([wnl.lemmatize(i) for i in tweet.split()])

    print "Lemaatize------->"+tweet



    # break usernames and hashtags +++++++++++++++++++++++++++++++++++++++++++++
    mentions = re.findall(r"@\w+", tweet)
    hashtags = re.findall(r"#\w+", tweet)

    #toBreak = mentions + hashtags
    toBreak = hashtags

    for term in toBreak:
        segments = word_breaker.segment(term[1:])
        segments = ' '.join(segments)

        tweet = tweet.replace(term, segments)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # Split terms in tweet
    for term in tweet.split(" "):
        segments = word_breaker.segment(term)
        segments = " ".join(segments)
        tweet = tweet.replace(term, segments)

    #print tweet

    #sys.exit()

    #stop word and single charectter removal
    tweet = [word for word in tweet.split(" ") if word.lower() not in stop and len(word) > 1]
    tweet = " ".join(tweet)


    print "cleanned------->"+tweet
    return tweet
