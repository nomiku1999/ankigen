import csv

import requests
import json
import argostranslate.package
import argostranslate.translate
from pypinyin import pinyin, Style
import os
from bs4 import BeautifulSoup

# The default address for AnkiConnect
URL = 'http://localhost:8765'

argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()
package_to_install = next(
    filter(lambda x: x.from_code == "en" and x.to_code == "zh", available_packages)
)
argostranslate.package.install_from_path(package_to_install.download())

# Will store fields for each note in the deck then save to a CSV file for later use
deck = []

def get_pinyin(text):
    """
    Converts Chinese text to Pinyin. 
    Style.TONE uses tone marks (e.g., zhōngwén).
    """
    result = pinyin(text, style=Style.TONE)
    # Flatten the list of lists into a single string
    return " ".join([item[0] for item in result])

def translate_text(text):
    """
    Translates text using the locally installed Argos Translate model.
    """
    translated_text = argostranslate.translate.translate(text, "en", "zh")
    return translated_text

def extract_first_example(html):
    if not html:
        return None, None
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find the first row that contains an example (mh_T_cv_id)
    example_row = soup.find('tr', id='mh_T_cv_id')
    
    # Find the next immediate sibling row that contains the translation (mh_n_T_cv_id)
    if example_row:
        translation_row = example_row.find_next_sibling('tr', id='mh_n_T_cv_id')
    
    if example_row and translation_row:
        # Extract text and strip whitespace/HTML tags
        example = example_row.find('font').get_text(strip=True)
        translation = translation_row.find('font').get_text(strip=True)
        return example, translation
    
    return None, None

def update_anki_card_to_chinese(note_id):
    # 1. Fetch current note data
    note_data = requests.post('http://localhost:8765', json={
        "action": "notesInfo",
        "version": 6,
        "params": {"notes": [note_id]}
    }).json()['result'][0]

    # fields = note_data['fields']

    fields = note_data.get('fields', {})
    print("-" * 20)
    # for field_name, field_data in fields.items():
    #     print(f"{field_name}: {field_data['value']}")
    # print(f"Current fields for note {note_id}: {fields}")

    field = [fields.get('Mặt trước', {}).get('value', '')]
    field.append(fields.get('Tiếng Việt', {}).get('value', ''))
    field.append(fields.get('Phiên âm', {}).get('value', ''))
    
    dic = fields.get('Từ Điển', {}).get('value', '')

    if not dic:
        print(f"No dictionary content found for note ID {note_id}.")
        field.append('')
        field.append('')
    else:
        print(f"Dictionary content for note ID {note_id}: {dic[:100]}...")  # Print first 100 characters for debugging
        example, translation = extract_first_example(dic)
        field.append(example if example else '')
        field.append(translation if translation else '')
    deck.append(field)


    return

    # 2. Translate fields
    new_fields = {
        "Word": translate_text(fields['Word']['value']),
        "Example": translate_text(fields['Example']['value']),
        "IPA": get_pinyin(fields['Word']['value']),
    }

    # 3. Update the note in Anki
    requests.post('http://localhost:8765', json={
        "action": "updateNoteFields",
        "version": 6,
        "params": {
            "note": {
                "id": note_id,
                "fields": new_fields
            }
        }
    })
    print(f"Note {note_id} updated successfully.")

def invoke(action, params=None):
    request_payload = {
        "action": action,
        "version": 6,
        "params": params or {}
    }
    response = requests.post(URL, json=request_payload)
    return response.json().get('result')

def save_card_image(note_id, output_folder="HSK_images"):
    # 1. Get the note data to find the filename
    note_data = requests.post('http://localhost:8765', json={
        "action": "notesInfo",
        "version": 6,
        "params": {"notes": [note_id]}
    }).json()['result'][0]

    # Get the word for the filename and the image tag
    word = note_data['fields']['Mặt trước']['value']
    image_html = note_data['fields']['Hình ảnh']['value']
    
    if not image_html:
        print(f"No image found for note ID {note_id}.")
        return
    # 2. Extract filename from HTML (e.g., <img src="30_3600.jpg" />)
    # This simple split finds the filename inside the src attribute
    filename = image_html.split('src="')[1].split('"')[0]

    # 3. Retrieve the binary file from Anki
    response = requests.post('http://localhost:8765', json={
        "action": "retrieveMediaFile",
        "version": 6,
        "params": {"filename": filename}
    }).json()
    
    # Anki returns a base64 encoded string
    import base64
    binary_data = base64.b64decode(response['result'])

    # 4. Save the file
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    # Get file extension from original filename
    ext = os.path.splitext(filename)[1]
    save_path = os.path.join(output_folder, f"{word}{ext}")
    
    with open(save_path, "wb") as f:
        f.write(binary_data)
        
    print(f"Image saved to: {save_path}")

# 1. Get all deck names
decks = invoke("deckNames")
print(f"Available Decks: {decks}")

# 2. Browse a specific deck
# We use the search syntax 'deck:"Your Deck Name"'
target_deck = "HSK" 
query = f'deck:"{target_deck}"'

# Get IDs of notes in the deck
note_ids = invoke("findNotes", {"query": query})

# Fetch the actual content for those IDs
processed_notes = note_ids  # Limit to first 10 notes for demonstration
if processed_notes:
    notes_info = invoke("notesInfo", {"notes": processed_notes})
    
    print(f"\nFound {len(notes_info)} notes in '{target_deck}':")
    for note in notes_info:

        note_id = note.get('noteId')
        if note_id:
            update_anki_card_to_chinese(note_id)
            print(f"Updated note ID {note_id} to Chinese.")
        else:
            print("No note ID found for this note.")

        if note_id:
            save_card_image(note_id)
else:
    print(f"No notes found in deck '{target_deck}'.")

# save the deck to a CSV file for later use
with open("deck_data.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Word", "Example", "IPA", "Translation"])
    writer.writerows(deck)

"""
--------------------
Word: whereabouts
Image: <img src="30_3600.jpg" />
Sound: [sound:30_3600.mp3]
Sound_Meaning: [sound:30_3600_meaning.mp3]
Sound_Example: [sound:30_3600_example.mp3]
Meaning: The <i>whereabouts</i> of someone or something is the place where they are.
Example: The police looked for the lost dog, but its <b>whereabouts</b> were still unknown.
IPA: ˈwerəbaʊts
"""