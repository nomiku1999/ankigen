import genanki
import os

MODEL_ID = 1984739201
DECK_ID = 2026061701

# [Giữ nguyên phần định nghĩa Model và Deck giống như bài trước]
chinese_model = genanki.Model(
    MODEL_ID,
    'Chinese Common 3000 Words Model',
    fields=[
        {'name': 'Vocab'}, {'name': 'Pinyin'}, {'name': 'Meaning'},
        {'name': 'Image'}, {'name': 'Audio'},
    ],
    templates=[{
        'name': 'Card 1',
        'qfmt': '<div class="image-container">{{Image}}</div><div class="audio-container">{{Audio}}</div><div class="vocab-text">{{Vocab}}</div><div class="pinyin-text">{{Pinyin}}</div>',
        'afmt': '{{FrontSide}}<hr id="answer"><div class="meaning-text">{{Meaning}}</div>',
    }],
    css='.card { text-align: center; font-family: sans-serif; } .image-container img { max-width: 250px; }' # Viết gọn lại minh họa
)

my_deck = genanki.Deck(DECK_ID, '3000 Từ Trung Common (Phân tách Folder)')

# Database mẫu: Chỉ lưu tên file, không lưu tên folder gốc
words_database = [
    {"vocab": "我", "pinyin": "wǒ", "meaning": "I; me", "img": "wo.jpg", "audio": "wo.mp3"},
    {"vocab": "你", "pinyin": "nǐ", "meaning": "you (singular)", "img": "ni.jpg", "audio": "ni.mp3"},
]

# Đây là nơi chứa đường dẫn thực tế để Python quét ổ đĩa khi đóng gói
actual_media_paths = []

for item in words_database:
    # 1. Định dạng trên thẻ Anki: KHÔNG ĐƯỢC chứa tên folder 'img/' hay 'mp3/'
    img_tag = f'<img src="{item["img"]}">' if item["img"] else ''
    audio_tag = f'[sound:{item["audio"]}]' if item["audio"] else ''
    
    note = genanki.Note(
        model=chinese_model,
        fields=[item["vocab"], item["pinyin"], item["meaning"], img_tag, audio_tag]
    )
    my_deck.add_note(note)
    
    # 2. Đường dẫn thực tế để Python tìm file nén: Phải nối thêm tên folder tương ứng
    if item["img"]:
        actual_path = os.path.join("img", item["img"])  # Kết quả: "img/wo.jpg"
        actual_media_paths.append(actual_path)
        
    if item["audio"]:
        actual_path = os.path.join("mp3", item["audio"])  # Kết quả: "mp3/wo.mp3"
        actual_media_paths.append(actual_path)

# 3. Tiến hành đóng gói file .apkg
my_package = genanki.Package(my_deck)

# Nạp danh sách đường dẫn thực tế (ví dụ: ['img/wo.jpg', 'mp3/wo.mp3'])
my_package.media_files = list(set(actual_media_paths)) 

output_file = 'Chinese_Common_Separated_Folders.apkg'
my_package.write_to_file(output_file)

print(f"Đã xuất bộ thẻ thành công từ các thư mục riêng lẻ: {output_file}")