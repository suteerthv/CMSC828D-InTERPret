import argparse
import bs4
import os
import textblob
from keywords import get_keywords, initialize_keywords
import csv
import psycopg2  # use this package to work with postgresql
import psycopg2.sql  # use this package to work with postgresql
from pytorch_pretrained_bert import BertTokenizer, BertForMaskedLM
import re
import nltk
import torch
import textblob
from enchant.checker import SpellChecker
from difflib import SequenceMatcher

credentials = {
    "host": "127.0.0.1",
    "port": "15432",
    "dbname": "newspapers",
    "user": "cmsc828d",
}


def clean_text(text):
    text_original = str(text)
    rep = {'\n': ' ',
           '\\': ' ',
           '-': ' ',
           '"': ' " ',
           ',': ' , ',
           '.': ' . ',
           '!': ' ! ',
           '?': ' ? ',
           "n't": " not" ,
           "'ll": " will",
           '*': ' * ',
           '(': ' ( ',
           ')': ' ) ',
           "s'": "s '"}
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)

    def get_personslist(text):
        personslist = []
        for sent in nltk.sent_tokenize(text):
            for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
                if isinstance(chunk, nltk.tree.Tree)\
                        and chunk.label() == 'PERSON':
                    personslist.insert(0, (chunk.leaves()[0][0]))
        return list(set(personslist))
    personslist = get_personslist(text)
    ignorewords = personslist + ["!", ",", ".", '"', "?", "(", ")", "*", "'"]
    d = SpellChecker("en_US")
    words = text.split()
    incorrectwords = [w for w in words
                      if not d.check(w)
                      and w not in ignorewords]
    suggestedWords = [d.suggest(w) for w in incorrectwords]
    for w in incorrectwords:
        text = text.replace(w, '[MASK]')
        text_original = text_original.replace(w, '[MASK]')

    tokenizer = BertTokenizer.from_pretrained('bert-based-uncased')
    tokenized_text = tokenizer.tokenize(text)
    indexed_tokens = tokenizer.converttokenized_text_to_ids(tokenized_text)
    MASKIDS = [i for i, e in enumerate(tokenized_text) if e == '[MASK]']

    segs = [i for i, e in enumerate(tokenized_text) if e == "."]
    segments_ids = []
    prev = -1
    for k, s in enumerate(segs):
        segments_ids = segments_ids + [k] * (s - prev)
        prev = s
    segments_ids = segments_ids + [len(segs)] * [(len(tokenized_text) - len(segments_ids))]
    segment_tensors = torch.tensor([segment_ids])

    tokens_tensor = torch.tensor([indexed_tokens])

    model = BertForMaskedLM.from_pretrained('bert-base-uncased')

    with torch.no_grad():
        prediction = model(tokens_tensor, segment_tensors)


def get_text(xml_file, strip_unicode=True):
    with open(xml_file, encoding='utf-8') as f:
        xml_string = f.read()
    soup = bs4.BeautifulSoup(xml_string, 'lxml')

    # Combines the words to form all the sentences
    sentences = " ".join(
        map(lambda l:
            # Combines the words found in the tags
            " ".join(
                map(lambda w:
                    # Converts the tags into words
                    w["content"], l.find_all("string"))),
            # Finds all the sentences.
            soup.find_all("textline")))

    if strip_unicode:
        # Since we have an English newspaper we are converting to ASCII
        sentences = sentences.encode("ascii", "ignore").decode()
    return sentences


def process_article(title, date, file):
    return None


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("paper_name",
                        help="This is the name of the paper",
                        type=str)

    parser.add_argument("data_root",
                        help="This is the data folder",
                        type=str)

    parser.add_argument("--meta_data",
                        help="This is the meta data csv default: Issue_metadata.csv",
                        type=str,
                        default="Issue_metadata.csv")

    parser.add_argument("--debug",
                        help="This is the put the upload in debug mode and\
                            pushes the number of papers to the database.\
                            With out this flag it takes 20 mins to upload",
                        type=int,
                        default=-1)

    # Parse the arguments
    cmd_args = parser.parse_args()
    csvfp = os.path.join(cmd_args.data_root, cmd_args.meta_data)
    print("Reading meta data file: {}...".format(csvfp))
    relavent_keys = ["Title", "Date", "FILES"]

    initialize_keywords()
    # Make the database connection
    con = psycopg2.connect(
        host=credentials["host"],
        database=credentials["dbname"],
        user=credentials["user"],
        port=credentials["port"]
    )

    # Ensure that the changes to the database are recorded
    con.autocommit = True

    cur = con.cursor()
    debug_cntr = cmd_args.debug
    with open(csvfp) as csvf:
        csvreader = csv.DictReader(csvf)

        # For each row in the metadatacsv
        for row in csvreader:
            title = row["Title"].strip()
            date = row["Date"]
            # The files associated with each paper are ';' separated
            files = row["FILES"].split(";")
            for f in files:
                # Join the root of the data file and the file mentioned to get xml
                xml_f = os.path.join(cmd_args.data_root, f)
                p_id = row["URI"].split('/')[-1]
                xml_f = os.path.join(cmd_args.data_root,
                                     os.path.join(p_id, f.split("/")[-1]))

                # This converts the xml to a string and removes any trailing spaces
                text = get_text(xml_f).strip()
                data_article = (title, text, date, cmd_args.paper_name, text)

                # Insert into the database and get the id of the article
                query = "INSERT INTO\
                    articles(title, body, year, paper, tokens, paper_id)\
                    VALUES (%s, %s, %s, %s, to_tsvector(%s), %s)\
                    RETURNING id"
                cur.execute(query, data_article + (p_id,))
                new_id = cur.fetchone()[0]

                print("Inserting '{}' from '{}' into '{}' with id:'{}' and paper_id:"
                      .format(title, date, cmd_args.paper_name, new_id, p_id))
                assert(new_id and p_id)

                # Uses the get_keywords function from the keywords modle
                keywords = get_keywords(text)
                query = "INSERT INTO keywords(keyword, id) VALUES (%s, %s)"
                for word in keywords:
                    tup = (word, new_id)
                    cur.execute(query, tup)

            # Incase you run in debug mode, break after number
            if debug_cntr > 0:
                debug_cntr -= 1
            elif debug_cntr == 0:
                break

    cur.close()
    con.close()
    print("Completed uploading to {}".format(credentials["dbname"]))
