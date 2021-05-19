from pytorch_pretrained_bert import BertTokenizer, BertForMaskedLM
from rake_nltk import Rake
import re
import nltk
import torch
import textblob
from difflib import SequenceMatcher


def initialize_keywords():
    nltk.download('punkt')
    nltk.download('brown')
    nltk.download('stop words')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')


def get_keywords_heurestic(text):
    return list(
        filter(
            lambda x: len(x) > 6 and len(x) < 64,
            textblob.TextBlob(text).noun_phrases))


def get_keywords(text):
    r = Rake()
    r.extract_keywords_from_text(text)
    return r.get_ranked_phrases()
