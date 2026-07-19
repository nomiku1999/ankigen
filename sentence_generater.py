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
input_file = "/home/miku/Code/AnkiGenerater/ankigen/deck_data.csv"
output_file = "/home/miku/Code/AnkiGenerater/ankigen/word/chinese_HSK.csv"
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
    
    Task: Create ONE short, simple, conversational Chinese example sentence using this word. Provide its Vietnamese translation.
    
    Rules: 
    1. Short (under 12 chars). 
    2. No complex grammar. 
    3. No Pinyin inside the Chinese sentence.
    4. CRITICAL: The example sentence MUST contextually demonstrate the specific definition provided above. 
    
    Output JSON format only:
    {{"example": "Chinese sentence", "meaning": "Vietnamese translation"}}
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

    # print(f"\nProcessing row {index + 1}/{len(df)}: Word: {row['Word']}, Pinyin: {row['Pinyin']}, Meaning: {row['Meaning']}")
    print(row)  
    ex_cn, ex_en = get_local_llm_example(row["Word"], row["Pinyin"], row["Meaning"])
    
    print(f"\nWord: {row['Word']}, Pinyin: {row['Pinyin']}, Meaning: {row['Meaning']}, Example: {ex_cn}, Translation: {ex_en}")
    df.at[index, "Example"] = ex_cn
    df.at[index, "Example_Meaning"] = ex_en
    
    # Save progress to disk every 50 rows
    if index % 10 == 0:
        df.to_csv(output_file, index=False)

# Final save
df.to_csv(output_file, index=False)
print(f"\nTask Complete! Output successfully saved to: {output_file}")