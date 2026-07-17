import json
import pandas as pd
from tqdm import tqdm
from ollama import chat
from pydantic import BaseModel

# Define the exact data structure we want from the local LLM
class TranslationExample(BaseModel):
    example: str
    meaning: str

# Configuration
input_file = "/home/miku/Code/AnkiGenerater/ankigen/word/chinese_words.csv"
output_file = "/home/miku/Code/AnkiGenerater/ankigen/word/chinese_words_local_examples.csv"
model_name = "qwen3.6:35b-a3b"
#model_name = "qwen3.5:9b"
# Load your CSV
df = pd.read_csv(input_file)

# Set up blank columns if they don't exist
if "Example" not in df.columns:
    df["Example"] = ""
if "Example_Meaning" not in df.columns:
    df["Example_Meaning"] = ""

def get_local_llm_example(vocab, pinyin, meaning):
    # prompt = f"""
    # You are a Chinese language teacher. Look at this vocabulary word:
    # Word: {vocab}
    # Pinyin: {pinyin}
    # Definition: {meaning}
    
    # Create exactly one practical, natural example sentence in Chinese using this word correctly based on its definition. Then provide its English translation.
    # """
    prompt = f"""
    Act as a Chinese teacher. 
    Word: {vocab} | Pinyin: {pinyin} | Definition: {meaning}
    
    Task: Create ONE short, simple, conversational Chinese example sentence using this word. Provide its English translation.
    
    Rules: Short (under 12 chars). No complex grammar. No Pinyin inside the Chinese sentence.
    
    Output JSON format only:
    {{"example": "Chinese sentence", "meaning": "English translation"}}
    """
    try:
        # Requesting structured output from Ollama
        response = chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.3},
            format=TranslationExample.model_json_schema()
        )
        
        # Parse the verified JSON structure
        result = TranslationExample.model_validate_json(response.message.content)
        return result.example, result.meaning
    except Exception as e:
        print(f"\nError processing word '{vocab}': {e}")
        return "", ""

print(f"Processing 3,000 words locally using {model_name} on your RTX 3090...")

# Iterate through the dataframe with a progress bar
for index, row in tqdm(df.iterrows(), total=len(df)):
    # Skip rows that are already completed (allows resuming if stopped)
    if pd.notna(row["Example"]) and row["Example"] != "":
        continue
        
    ex_cn, ex_en = get_local_llm_example(row["Vocab"], row["Pinyin"], row["Meaning"])
    
    print(f"\nWord: {row['Vocab']}, Pinyin: {row['Pinyin']}, Meaning: {row['Meaning']}, Example: {ex_cn}, Translation: {ex_en}")
    df.at[index, "Example"] = ex_cn
    df.at[index, "Example_Meaning"] = ex_en
    
    # Save progress to disk every 50 rows
    if index % 10 == 0:
        df.to_csv(output_file, index=False)

# Final save
df.to_csv(output_file, index=False)
print(f"\nTask Complete! Output successfully saved to: {output_file}")