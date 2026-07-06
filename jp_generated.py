import os
import asyncio
import pandas as pd
import torch
from diffusers import FluxPipeline
import edge_tts
import genanki

# ==================== 1. CẤU HÌNH HỆ THỐNG ====================
CSV_FILE = "japanese_words.csv"  # Thay bằng tên file CSV thực tế của bạn
VOCAB_COL = "expression"         # Tên cột chữ Hán (hoặc từ gốc)
READING_COL = "reading"         # Tên cột cách đọc Kana
MEANING_COL = "meaning"         # Tên cột nghĩa tiếng Anh

IMG_FOLDER = "img"
MP3_FOLDER = "mp3"
OUTPUT_APKG = "Bo_The_Tieng_Nhat_Nghe_Noi.apkg"

# Cấu hình ID ngẫu nhiên cho Anki (Giữ cố định để tránh trùng lặp khi import)
MODEL_ID = 2026061801
DECK_ID = 2026061802

# Tạo các thư mục chứa media
os.makedirs(IMG_FOLDER, exist_ok=True)
os.makedirs(MP3_FOLDER, exist_ok=True)

# ==================== 2. KHỞI TẠO AI GENERATION (RTX 3090) ====================
print("Đang tải mô hình Flux.1-Schnell vào RTX 3090...")
try:
    pipe = FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-schnell", torch_dtype=torch.bfloat16)
    pipe.to("cuda")
    print("✓ Đã nạp Model lên GPU thành công!")
except Exception as e:
    print(f"✗ Không thể nạp Model lên GPU. Kiểm tra lại cài đặt CUDA: {e}")
    exit()

# ==================== 3. ĐỊNH NGHĨA CẤU TRÚC THẺ ANKI ====================
# Mặt trước CHỈ CÓ Ảnh + Âm thanh để luyện phản xạ Nghe-Hiểu
# Mặt sau hiển thị nghĩa tiếng Anh, cách đọc và chữ Kanji
japanese_model = genanki.Model(
    MODEL_ID,
    'Luyện Phản Xạ Nghe Nói Tiếng Nhật',
    fields=[
        {'name': 'Vocab'},       # Chữ Kanji (Mặt sau)
        {'name': 'Reading'},     # Chữ Kana (Mặt sau)
        {'name': 'Meaning'},     # Nghĩa tiếng Anh (Mặt sau)
        {'name': 'Image'},       # Thẻ chứa ảnh (Mặt trước)
        {'name': 'Audio'},       # Thẻ chứa âm thanh (Mặt trước)
    ],
    templates=[
        {
            'name': 'Thẻ Phản Xạ 1',
            # MẶT TRƯỚC: Hình ảnh hiện lên đồng thời kích hoạt Âm thanh phát ra
            'qfmt': '''
                <div class="image-container">{{Image}}</div>
                <div class="audio-container">{{Audio}}</div>
            ''',
            # MẶT SAU: Giữ nguyên ảnh + Hiện thêm nghĩa, cách đọc Kana và mặt chữ Kanji
            'afmt': '''
                {{FrontSide}}
                <hr id="answer">
                <div class="meaning-text">{{Meaning}}</div>
                <div class="reading-text">読み方: {{Reading}}</div>
                <div class="vocab-text">漢字: {{Vocab}}</div>
            ''',
        },
    ],
    css='''
        .card { font-family: Arial, sans-serif; text-align: center; color: #2c3e50; background-color: #fcfcfc; padding: 25px; }
        .image-container img { max-width: 280px; max-height: 280px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 15px; }
        .meaning-text { font-size: 30px; color: #2980b9; font-weight: bold; margin-top: 15px; }
        .reading-text { font-size: 22px; color: #e67e22; margin-top: 10px; font-weight: 500; }
        .vocab-text { font-size: 18px; color: #7f8c8d; margin-top: 8px; }
        hr#answer { border: 0; height: 1px; background-image: linear-gradient(to right, rgba(0,0,0,0), rgba(0,0,0,0.2), rgba(0,0,0,0)); margin: 20px 0; }
    '''
)

my_deck = genanki.Deck(DECK_ID, '3000 Từ Tiếng Nhật Cơ Bản (Nghe - Nói Ưu Tiên)')

# ==================== 4. CÁC HÀM XỬ LÝ TỰ ĐỘNG ====================

async def download_audio(text, filename):
    """Tự động tải phát âm chuẩn từ Edge-TTS"""
    path = os.path.join(MP3_FOLDER, filename)
    if os.path.exists(path):
        return True
    try:
        # Sử dụng giọng nữ Nhật Bản 'ja-JP-NanamiNeural' rất trong và chuẩn
        communicate = edge_tts.Communicate(text, 'ja-JP-NanamiNeural')
        await communicate.save(path)
        return True
    except Exception as e:
        print(f"  ✗ Lỗi tải âm thanh '{text}': {e}")
        return False

def generate_image(prompt, filename):
    """Tự động sinh ảnh minh họa bằng RTX 3090"""
    path = os.path.join(IMG_FOLDER, filename)
    if os.path.exists(path):
        return True
    try:
        # Thiết kế prompt dạng Flashcard giáo dục sạch sẽ, tối giản để tránh sinh ảnh rác
        clean_prompt = f"A clean, professional minimalist vector illustration of {prompt}, white background, educational flashcard style, clear object"
        
        image = pipe(
            prompt=clean_prompt,
            guidance_scale=0.0,
            num_inference_steps=4,  # Flux-schnell chỉ cần 4 bước để ra ảnh đẹp xuất sắc
            max_sequence_length=256
        ).images[0]
        
        # Resize ảnh về 512x512 để tối ưu bộ nhớ Anki
        image = image.resize((512, 512))
        image.save(path)
        return True
    except Exception as e:
        print(f"  ✗ Lỗi sinh ảnh '{prompt}': {e}")
        return False

# ==================== 5. TIẾN TRÌNH CHẠY CHÍNH ====================

async def main():
    # Đọc file dữ liệu đầu vào
    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        print(f"Không thể mở file CSV: {e}")
        return

    print(f"Tìm thấy {len(df)} từ vựng. Tiến hành xử lý song song...")
    
    media_files_to_pack = []

    for index, row in df.iterrows():
        vocab = str(row[VOCAB_COL]).strip() if pd.notna(row[VOCAB_COL]) else ""
        reading = str(row[READING_COL]).strip()
        meaning = str(row[MEANING_COL]).strip()
        
        # Đặt tên file đồng bộ theo từ vựng để tránh trùng lặp chèn chéo
        file_base_name = reading if not vocab else vocab
        # Loại bỏ các ký tự có thể gây lỗi lưu file hệ thống nếu có
        file_base_name = "".join(c for c in file_base_name if c.isalnum())
        
        img_name = f"{file_base_name}.jpg"
        mp3_name = f"{file_base_name}.mp3"
        
        print(f"[{index + 1}/{len(df)}] Đang xử lý từ: {reading} ({meaning})")
        
        # 1. Gọi TTS tải âm thanh (Dựa vào cột cách đọc Reading để máy phát âm chuẩn)
        audio_success = await download_audio(reading, mp3_name)
        
        # 2. Gọi GPU 3090 sinh hình ảnh (Dựa vào cột Meaning tiếng Anh làm Prompt)
        img_success = generate_image(meaning, img_name)
        
        # 3. Nếu tải và sinh ảnh thành công (hoặc file đã tồn tại), tiến hành tạo Note cho Anki
        if audio_success and img_success:
            img_tag = f'<img src="{img_name}">'
            audio_tag = f'[sound:{mp3_name}]'
            
            note = genanki.Note(
                model=japanese_model,
                fields=[vocab, reading, meaning, img_tag, audio_tag]
            )
            my_deck.add_note(note)
            
            # Đăng ký đường dẫn file thực tế trên ổ đĩa để đóng gói
            media_files_to_pack.append(os.path.join(IMG_FOLDER, img_name))
            media_files_to_pack.append(os.path.join(MP3_FOLDER, mp3_name))
            
        # Nghỉ một chút giữa các request TTS để tránh bị block IP
        await asyncio.sleep(0.05)

    # ==================== 6. ĐÓNG GÓI XUẤT FILE .APKG ====================
    print("\nĐang tiến hành đóng gói toàn bộ dữ liệu và media vào file .apkg...")
    my_package = genanki.Package(my_deck)
    my_package.media_files = media_files_to_pack
    my_package.write_to_file(OUTPUT_APKG)
    
    print(f"\n🎉 QUÁ TRÌNH HOÀN TẤT THÀNH CÔNG!")
    print(f"-> Kết quả xuất ra file: '{OUTPUT_APKG}'")
    print("-> Bạn chỉ cần click đúp vào file này để nạp thẳng bộ thẻ 3000 từ vào ứng dụng Anki.")

if __name__ == "__main__":
    asyncio.run(main())