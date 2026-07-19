import genanki
import os
import pandas as pd

MODEL_ID = 1984739201
DECK_ID = 2026061701

CSV_FILE = "/home/miku/Code/AnkiGenerater/ankigen/word/chinese_HSK.csv"
IMG_FOLDER = "/home/miku/Code/AnkiGenerater/ankigen/HSK_images"
VOCAB_AUDIO_FOLDER = "/home/miku/Code/AnkiGenerater/ankigen/voice/chinese"
SENTENCE_AUDIO_FOLDER = "/home/miku/Code/AnkiGenerater/ankigen/voice/chinese_sentences"

chinese_model = genanki.Model(
    MODEL_ID,
    'Chinese Common 4000 Words Model',
    fields=[
        {'name': 'Vocab'}, 
        {'name': 'Pinyin'}, 
        {'name': 'Meaning'},
        {'name': 'Image'},
        {'name': 'Audio'},
        {'name': 'Example'},       
        {'name': 'SentenceAudio'}, 
        {'name': 'ExampleMeaning'}
    ],
    templates=[{
        'name': 'Card 1',
        'qfmt': '''
            <div class="image-container">{{Image}}</div>
            <div class="audio-container">{{Audio}}</div>
            <div class="vocab-text">{{Vocab}}</div>
            <div class="pinyin-text">{{Pinyin}}</div>
        ''',
        'afmt': '''
            {{FrontSide}}
            <hr id="answer">
            <div class="meaning-text">{{Meaning}}</div>
            
            {{#Example}}
            <div class="example-container">
                <div class="example-box">
                    <div class="example-header">💡 Context Sentence</div>
                    <div class="example-text">{{Example}}</div>
                    
                    {{#ExampleMeaning}}
                    <div class="example-meaning">{{ExampleMeaning}}</div>
                    {{/ExampleMeaning}}
                    
                    {{#SentenceAudio}}
                    <div class="example-audio-wrapper">
                        <span class="audio-label">Pronunciation:</span> {{SentenceAudio}}
                    </div>
                    {{/SentenceAudio}}
                </div>
            </div>
            {{/Example}}
        ''',
    }],
    css='''
        /* Base Card Structure */
        .card { 
            text-align: center; 
            font-family: system-ui, -apple-system, sans-serif; 
            background-color: #fcfcfc; 
            color: #333;
            padding: 20px;
        } 
        
        .vocab-text { font-size: 34px; font-weight: bold; color: #111; margin-top: 10px; }
        .pinyin-text { font-size: 18px; color: #666; margin-bottom: 10px; }
        .meaning-text { font-size: 22px; color: #0077cc; font-weight: 600; margin: 15px 0; }
        
        /* Modernized Layout Wrapper */
        .example-container {
            display: flex;
            justify-content: center;
            width: 100%;
            margin-top: 20px;
        }

        .example-box { 
            background: #f4f7f9; 
            border: 1px solid #e2e8f0;
            border-radius: 12px; 
            padding: 18px; 
            width: 85%;
            max-width: 500px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
            text-align: left; /* Left-align text inside the card container for reading comfort */
        }
        
        .example-header {
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #888;
            margin-bottom: 8px;
            font-weight: bold;
        }

        .example-text { font-size: 22px; color: #1a1a1a; font-weight: 500; line-height: 1.4; }
        .example-meaning { font-size: 16px; color: #555; margin-top: 6px; font-style: italic; line-height: 1.4; }
        
        /* Clean Alignment row for the native audio action */
        .example-audio-wrapper {
            margin-top: 14px;
            padding-top: 12px;
            border-top: 1px dashed #cbd5e1;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .audio-label {
            font-size: 14px;
            color: #666;
            font-weight: 500;
        }

        /* --- STUNNING NATIVE AUDIO BUTTON STYLING --- */
        .card .replay-button, .card .soundLink {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-decoration: none !important;
            background-color: #0077cc !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 6px 14px !important;
            font-size: 13px !important;
            font-weight: bold !important;
            border: none !important;
            box-shadow: 0 2px 4px rgba(0,119,204,0.2) !important;
            transition: background 0.2s;
        }
        
        .card .replay-button:hover, .card .soundLink:hover {
            background-color: #005599 !important;
        }

        /* Adjusts native SVG icon to white to look perfect inside the blue pill */
        .card .replay-button svg {
            width: 14px !important;
            height: 14px !important;
            fill: white !important;
        }
    '''
)

my_deck = genanki.Deck(DECK_ID, '4000 Common Chinese Words with Sentences')
actual_media_paths = []

df = pd.read_csv(CSV_FILE)

for index, row in df.iterrows():
    vocab = str(row.get("Vocab", "")).strip()
    pinyin = str(row.get("Pinyin", "")).strip()
    meaning = str(row.get("Meaning", "")).strip()
    example = str(row.get("Example", "")).strip()
    example_meaning = str(row.get("Example_Meaning", row.get("ExampleMeaning", ""))).strip()
    if not example_meaning or example_meaning == 'nan':
        example_meaning = str(row.get("Translation", "")).strip()
    
    if not vocab or vocab == 'nan':
        continue

    if (not pinyin or pinyin == 'nan'
        # or not meaning or meaning == 'nan'
        or not example or example == 'nan'
        or not example_meaning or example_meaning == 'nan'):
        print(f"⚠️ Skipping row {index} due to missing essential data: Vocab='{vocab}', Pinyin='{pinyin}', Meaning='{meaning}', Example='{example}', ExampleMeaning='{example_meaning}'")
        continue

    img_file = f"{vocab}.jpg"
    vocab_audio_file = f"{vocab}.mp3"
    sentence_audio_file = f"{vocab}_sentence.mp3"
    
    # if ";" in meaning:
    #     meaning = meaning.split(";")[0].strip()

    field_example = example if example != 'nan' and example != '' else ''
    field_example_meaning = example_meaning if example_meaning != 'nan' and example_meaning != '' else ''

    img_tag = f'<img src="{img_file}">' if os.path.exists(os.path.join(IMG_FOLDER, img_file)) else ''
    audio_tag = f'[sound:{vocab_audio_file}]' if os.path.exists(os.path.join(VOCAB_AUDIO_FOLDER, vocab_audio_file)) else ''
    sentence_audio_tag = f'[sound:{sentence_audio_file}]' if os.path.exists(os.path.join(SENTENCE_AUDIO_FOLDER, sentence_audio_file)) else ''
    
    note = genanki.Note(
        model=chinese_model,
        fields=[
            vocab, 
            pinyin, 
            meaning, 
            img_tag, 
            audio_tag,
            field_example,
            sentence_audio_tag,
            field_example_meaning
        ]
    )
    my_deck.add_note(note)
    
    if img_tag:
        actual_media_paths.append(os.path.join(IMG_FOLDER, img_file))
    if audio_tag:
        actual_media_paths.append(os.path.join(VOCAB_AUDIO_FOLDER, vocab_audio_file))
    if sentence_audio_tag and os.path.exists(os.path.join(SENTENCE_AUDIO_FOLDER, sentence_audio_file)):
        actual_media_paths.append(os.path.join(SENTENCE_AUDIO_FOLDER, sentence_audio_file))

my_package = genanki.Package(my_deck)
my_package.media_files = list(set(actual_media_paths)) 
my_package.write_to_file('Chinese_Vocabulary_and_Sentences.apkg')
print("Successfully generated deck with beautiful, adaptive layouts!")