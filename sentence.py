import pandas as pd
from tqdm import tqdm
import requests
import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator
import time

# Load your CSV
input_file = CSV_FILE = r"C:\Users\Miku\Desktop\Anki_generate\word\chinese_words.csv"
output_file = r"C:\Users\Miku\Desktop\Anki_generate\word\chinese_words_free_examples.csv"

df = pd.read_csv(input_file)

if "Example" not in df.columns:
    df["Example"] = ""
if "Example_Meaning" not in df.columns:
    df["Example_Meaning"] = ""

def get_free_sentence(word):
    """Fetches a real Chinese example sentence using a free public dictionary API"""
    try:
        # Using a public free API endpoint that returns example sentences in XML
        url = f"http://dict.youdao.com/search?q={word}&doctype=xml"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            # Find the first example sentence block
            for example in root.findall('.//example'):
                cn_sentence = example.find('cn')
                en_sentence = example.find('en')
                
                if cn_sentence is not None and en_sentence is not None:
                    # Clean up any leftover whitespace or newlines
                    cn = cn_sentence.text.strip().replace('\n', '')
                    en = en_sentence.text.strip().replace('\n', '')
                    return cn, en
    except Exception as e:
        pass
    
    # Fallback Method: If the dictionary API misses, we look up a sentence or use translation
    return None, None

def fallback_translation(word):
    """Fallback if no example is found: make a simple sentence and translate it"""
    try:
        # Create a super basic sentence: "This is [word]." (这是[word]。)
        simple_sentence = f"这是{word}。"
        # Translate it for free
        translated = GoogleTranslator(source='zh-CN', target='en').translate(simple_sentence)
        return simple_sentence, translated
    except:
        return "", ""

# Process the 3,000 rows
print("Starting free generation process...")
for index, row in tqdm(df.iterrows(), total=len(df)):
    # Skip already processed rows
    if pd.notna(row["Example"]) and row["Example"] != "":
        continue
        
    word = row["Vocab"]
    cn_ex, en_ex = get_free_sentence(word)
    
    # If the dictionary didn't have an exact sentence, use the fallback
    if not cn_ex:
        cn_ex, en_ex = fallback_translation(word)
        
    df.at[index, "Example"] = cn_ex
    df.at[index, "Example_Meaning"] = en_ex
    
    # Pause for a split second so the free servers don't block you
    time.sleep(0.3)
    
    # Auto-save every 100 rows
    if index % 100 == 0:
        df.to_csv(output_file, index=False)

# Save final results
df.to_csv(output_file, index=False)
print(f"\nSuccess! All 3,000 words processed for $0. File saved to: {output_file}")