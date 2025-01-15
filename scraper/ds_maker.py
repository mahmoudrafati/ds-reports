import os
import re
import pandas as pd
import sys
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from pandas.core.algorithms import isin
from transformers import pipeline, AutoTokenizer
from tqdm import tqdm
import time  # Added import

nltk.download('punkt_tab')

pipe = pipeline("text-classification", model="ProsusAI/finbert", )
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")

def head_remove(text):
    match = re.search(r"Federal\s+Open\s+Market\s+Committee\s+held\s+on", text, re.IGNORECASE)
    if match:
        return text[match.start():]
    print("no head")
    return text

def split_long_sentence(sentence):
    chunks = re.split(r',\s*', sentence)  # Split by commas, preserving remaining parts
    return chunks
    
def sentence_length(sentence):
    words = word_tokenize(sentence)
    return len(words)

def clean_text(text):
    if isinstance(text, str):
        text_no_newlines = re.sub(r'[\n\r\t]+', ' ', text)
        text_no_white = re.sub(r'[\s;]+', ' ', text_no_newlines).strip()
        text_lowercase = text_no_white.lower()
    return text_lowercase

tqdm.pandas(desc='Applying Sentiment Analysis')

def process_file(file_path, output_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    #tokenize using nltk and labeling with prosus finbert pipe
    headless_text = head_remove(text)
    cleaned_text = clean_text(headless_text)
    
    sentences = sent_tokenize(cleaned_text)
    for sentence in sentences:
        if sentence_length(sentence) > 512:
            chunks = split_long_sentence(sentence)
            sentences.remove(sentence)
            sentences.extend(chunks)

    df = pd.DataFrame(sentences, columns=['sentence'])
    df['sentiment'] = df['sentence'].progress_apply(lambda x: pipe(x)[0]["label"])

    # save as csv
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, sep=';')
    print(f"Data saved to {os.path.abspath(output_path)}")

def main():
    start_time = time.time()  # Start timing
    if len(sys.argv) != 2:
        print("Usage: python script.py <URL>")
        sys.exit(1)

    raw_path_string = sys.argv[1]
    raw_path = os.path.abspath(raw_path_string)
    dataset_dir_name = 'datasets'
    dataset_path = os.path.join(os.path.dirname(raw_path), dataset_dir_name)

    # recusive search of all subdirectorys and apllication in directory 
    for bank_dir in os.listdir(raw_path):
            if bank_dir == '.DS_Store':
                continue
            bank_path = os.path.join(raw_path, bank_dir)

            if not os.path.isdir(bank_path):
                continue

            for year_dir in os.listdir(bank_path):
                if year_dir == '.DS_Store':
                    continue
                year_path = os.path.join(bank_path, year_dir)

                if not os.path.isdir(year_path):
                    continue
                
                links_file = os.path.join(year_path, 'links.json')
                if os.path.exists(links_file):
                    print(f"Verarbeite: {links_file}")
                    
                    for subyear_dir in os.listdir(year_path):
                        if subyear_dir == '.DS_Store' or subyear_dir == 'links.json':
                            continue
                        subyear_path = os.path.join(year_path, subyear_dir)

                        if not os.path.exists(subyear_path):
                            continue

                        # edit files in subyear dir 
                        for txt_file in os.listdir(subyear_path):
                            txt_path = os.path.join(subyear_path, txt_file)
                            # create output dir 
                            output_dir = os.path.join(dataset_path, bank_dir, year_dir, subyear_dir)
                            output_csv_path = os.path.join(output_dir, f"{os.path.splitext(txt_file)[0]}.csv")
                            process_file(txt_path, output_csv_path)

    print(f"Process completed in {time.time() - start_time:.2f} seconds.")  # End timing

if __name__ == "__main__": 
    main()
