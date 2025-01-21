import os
import re
import nltk
import pandas as pd
import sys
from nltk.tokenize import word_tokenize, sent_tokenize
from transformers import BertTokenizer, BertForSequenceClassification, pipeline
from tqdm import tqdm
from gtabview import view
import torch  # Existing import
import time  # Added import

nltk.download('punkt')

# Check GPU availability and set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

finbert = BertForSequenceClassification.from_pretrained('ZiweiChen/FinBERT-FOMC',num_labels=3).to(device)  # Move model to device
tokenizer = BertTokenizer.from_pretrained('ZiweiChen/FinBERT-FOMC')
finbert_fomc = pipeline("text-classification", 
                        model=finbert, 
                        tokenizer=tokenizer,
                        device=0 if torch.cuda.is_available() else -1)  # Create pipeline with device specified

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

# remove punktuations and " symbols
def remove_punctuation(text):
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'["]+', '', text)
    return text

def clean_text(text):
    if isinstance(text, str):
        text_no_newlines = re.sub(r'[\n\r\t]+', ' ', text)
        text_no_white = re.sub(r'[\s;]+', ' ', text_no_newlines).strip()
        text_lowercase = text_no_white.lower()
    return text_lowercase

def extract_sentiment(text):
    try:
        result = finbert_fomc(text)[0]
        return pd.Series([result['label'], result['score']], index=['sentiment', 'sentiment_score'])
    except RuntimeError as e:
        if "size of tensor" in str(e):
            return pd.Series(['neutral', 0.0], index=['sentiment', 'sentiment_score'])
        print(f"Error: {e} with sentence: {text}")
        raise e

tqdm.pandas(desc='Applying Sentiment Analysis')

def process_text_to_sentences(text):
    sentences = sent_tokenize(text)
    clean_sentences = [remove_punctuation(s) for s in sentences]
    result = []
    for sentence in clean_sentences:
        if sentence_length(sentence) > 512:
            result.extend(split_long_sentence(sentence))
        else:
            result.append(sentence)
    return result

def process_file(data, output_path):
    df = pd.read_csv(data, sep=';')
    df['Date'] = pd.to_datetime(df['Date'], errors='raise')

    df['Text'] = df['Text'].progress_apply(lambda x: clean_text(x))

    # Create expanded DataFrame with sentences
    df_expanded = df.apply(lambda x: pd.Series({
        'sentence': process_text_to_sentences(x['Text']),
        'Type': [x['Type']] * len(process_text_to_sentences(x['Text'])),
        'Date': [x['Date']] * len(process_text_to_sentences(x['Text'])),
        'Month': [x['Month']] * len(process_text_to_sentences(x['Text']))
    }), axis=1)

    # Explode the lists to create individual rows
    df_processed = df_expanded.apply(pd.Series.explode).reset_index(drop=True)

    # Add sentiment analysis
    sentiment_results = df_processed['sentence'].progress_apply(extract_sentiment)
    df_processed = pd.concat([df_processed, sentiment_results], axis=1)

    # Format dates
    df_processed['Year'] = df_processed['Date']).dt.year

    # Reorder columns
    df_processed = df_processed[['Year', 'Month', 'Type', 'sentiment', 'sentiment_score', 'sentence']]

    # Save to CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_processed.to_csv(output_path, index=False, sep=';')

def main():
    start_time = time.time()  # Start timing
    base_path = 'data/raw_pdf/kaggledata_month/'
    output_path = 'data/datasets/fed_kaggle'

    for year_dir in os.listdir(base_path):
        year_path = os.path.join(base_path, year_dir)
        if not os.path.isdir(year_path):
            continue

        for month_file in os.listdir(year_path):
            month_file_path = os.path.join(year_path, month_file)
            if not os.path.isfile(month_file_path):
                continue

            output_month_path = os.path.join(output_path, year_dir, month_file)
            process_file(month_file_path, output_month_path)
            print('Done')

    print(f"Process completed in {time.time() - start_time:.2f} seconds.")  # End timing

if __name__ == '__main__':
    main()

