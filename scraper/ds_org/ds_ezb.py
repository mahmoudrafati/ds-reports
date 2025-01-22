import os
import re
import nltk
import pandas as pd
import sys
from nltk.tokenize import word_tokenize, sent_tokenize
from transformers import BertTokenizer, BertForSequenceClassification, pipeline
from tqdm import tqdm
#from gtabview import view
import torch  # Existing import
import time  # Added import

nltk.download('punkt_tab')

# Check GPU availability and set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

finbert = BertForSequenceClassification.from_pretrained('ZiweiChen/FinBERT-FOMC',num_labels=3).to(device)  # Move model to device
tokenizer = BertTokenizer.from_pretrained('ZiweiChen/FinBERT-FOMC')
finbert_fomc = pipeline("text-classification", 
                        model=finbert, 
                        tokenizer=tokenizer,
                        device=0 if torch.cuda.is_available() else -1)  # Create pipeline with device specified

def head_remove(text):
    pattern = r'[\d]?[\+]?Economic\s+[,]?financial\s+and\s+monetary\s+developements|\+\s+3[s+]?ECB\s+Economic\s+Bulletin\s+Issue\s+\d\s+\/\s+{\d\d\d\d}\s+Economic\s+and\s+monEtary\s+dEvElopmEnts|At\s+today’s\s+meeting\s+the\s+Governing\s+Council'
    return re.sub(pattern, '', text)

def split_long_sentence(sentence, tokenizer, max_length=512):
    """Split long sentences into BERT-friendly chunks. NEEDS TO BE REFACTORED"""
    encoded = tokenizer(sentence, truncation=False, add_special_tokens=False)
    tokens = encoded['input_ids']
    
    if len(tokens) <= max_length - 2:  # Account for [CLS] and [SEP]
        return [sentence]
        
    chunks = []
    current_chunk = []
    current_length = 0
    
    for token in tokens:
        if current_length + 1 > max_length - 2:
            chunk_text = tokenizer.decode(current_chunk)
            chunks.append(chunk_text)
            current_chunk = [token]
            current_length = 1
        else:
            current_chunk.append(token)
            current_length += 1
            
    if current_chunk:
        chunks.append(tokenizer.decode(current_chunk))
    
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


tqdm.pandas(desc='Applying Sentiment Analysis')

def process_text_to_sentences(text, tokenizer):
    sentences = sent_tokenize(text)
    clean_sentences = [remove_punctuation(s) for s in sentences]
    result = []
    for sentence in clean_sentences:
        if sentence_length(sentence) > 512:
            result.extend(split_long_sentence(sentence, tokenizer))
        else:
            result.append(sentence)
    return result

def extract_sentiment(text):
    try:
        result = finbert_fomc(text)[0]
        return pd.Series([result['label'], result['score']], index=['sentiment', 'sentiment_score'])
    except RuntimeError as e:
        if "size of tensor" in str(e):
            return pd.Series(['neutral', 0.0], index=['sentiment', 'sentiment_score'])
        print(f"Error: {e} with sentence: {text}")
        raise e

def process_file(data, output_path):
    df = pd.read_csv(data, sep=';')
    df['Date'] = pd.to_datetime(df['Date'], errors='raise')

    df['Text'] = df['Text'].apply(lambda x: clean_text(x))
    df['Month'] = df['Date'].dt.strftime('%B')


    # Create expanded DataFrame with sentences
    df_expanded = df.apply(lambda x: pd.Series({
        'sentence': process_text_to_sentences(x['Text'], tokenizer),
        'Type': [x['Type']] * len(process_text_to_sentences(x['Text'], tokenizer)),
        'Date': [x['Date']] * len(process_text_to_sentences(x['Text'], tokenizer)),
        'Month': [x['Month']] * len(process_text_to_sentences(x['Text'], tokenizer))
    }), axis=1)

    # Explode the lists to create individual rows
    df_processed = df_expanded.apply(pd.Series.explode).reset_index(drop=True)

    # Add sentiment analysis
    sentiment_results = df_processed['sentence'].apply(extract_sentiment)
    df_processed = pd.concat([df_processed, sentiment_results], axis=1)

    # Format dates
    df_processed['Year'] = df_processed['Date'].dt.year

    # Reorder columns
    df_processed = df_processed[['Date', 'Year', 'Month', 'Type', 'sentiment', 'sentiment_score', 'sentence']]

    # Save to CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_processed.to_csv(output_path, index=False, sep=';')

def main():
    start_time = time.time()  # Start timing
    base_path = 'data/raw_pdf/ezb/'
    output_path = 'data/datasets/ezb'

    # for files in os.listdir(base_path):
    #     if files.endswith('.csv'):
    #         print(f"Processing {files}...")
    #         process_file(os.path.join(base_path, files), os.path.join(output_path, files))
    #         print(f"File {files} processed.")

    # changing for new file structure
    for year in os.listdir(base_path):
        year_path = os.path.join(base_path, year)
        if os.path.isdir(year_path):
            for month in tqdm(os.listdir(year_path), desc=f"Processing {month} of {year}"):
                month_path = os.path.join(year_path, month)
                if month.endswith('.csv'):
                    process_file(month_path, os.path.join(output_path, year, month))
        


    print(f"Process completed in {time.time() - start_time:.2f} seconds.")  # End timing

if __name__ == '__main__':
    main()