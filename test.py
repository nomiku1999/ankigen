# read file /home/miku/Code/AnkiGenerater/ankigen/word/chinese_words_with_meanings.csv

import csv
import re
import pandas as pd
import os

file = '/home/miku/Code/AnkiGenerater/ankigen/word/chinese_words_with_meanings.csv'
df = pd.read_csv(file)
# Vocab,Pinyin,Meaning,Example,Example_Meaning

img_files = os.listdir('/home/miku/Code/AnkiGenerater/ankigen/extracted_images')
# remove file extension and create a set of image names
img_names = set(os.path.splitext(f)[0] for f in img_files)

# loop each row of df
sorted_img_names = sorted(list(img_names), key=len, reverse=True)

# We use a set to keep track of images we have already assigned to a word
used_images = set()

# add a new column to the DataFrame for the image
df['Image'] = ''

cnt = 0
for index, row in df.iterrows():
    vocab = row['Vocab']
    meaning = row['Meaning']
    
    # Check if we have already found an image for this row (optional)
    found_for_this_row = False
    
    for img_name in sorted_img_names:
        # Only use the image if it hasn't been used yet
        if img_name not in used_images:
            # Using a boundary check is safer: 
            # This ensures 'prod' doesn't match 'produce'
            # by checking if it exists as a distinct word in the meaning string
            if re.search(rf'\b{re.escape(img_name)}\b', meaning, re.IGNORECASE):
                print(f"Match Found! {vocab}: {meaning} -> {img_name}")
                
                # Mark as used so it isn't matched again
                used_images.add(img_name)
                cnt += 1
                found_for_this_row = True

                # Add the image to the row in the DataFrame
                df.at[index, 'Image'] = f'<img src="{img_name}.jpg" />'
                break # Move to the next vocab row once a match is found
print(f"Total matches found: {cnt}")
# save the updated DataFrame to a new CSV file
output_file = '/home/miku/Code/AnkiGenerater/ankigen/word/chinese_words_with_meanings_and_images.csv'
df.to_csv(output_file, index=False)
    