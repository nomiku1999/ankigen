import os
import torch
import pandas as pd
from diffusers import SanaPipeline

# watch -n 1 nvidia-smi
CSV_FILE = "/home/miku/Code/AnkiGenerater/ankigen/word/chinese_words.csv"
OUTPUT_FOLDER = "/home/miku/Code/AnkiGenerater/ankigen/img/chinese"
MEANING_COLUMN = "Meaning"
VOCAB_COLUMN = "Vocab"

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# 2. Khởi tạo mô hình SANA (Thế hệ mới siêu tốc độ, tiết kiệm VRAM)
print("Đang tải model SANA thế hệ mới vào RTX 3090...")
pipe = SanaPipeline.from_pretrained(
    "Efficient-Large-Model/Sana_600M_512px_diffusers", 
    # variant="fp16",
    # torch_dtype=torch.float16
    torch_dtype=torch.bfloat16
)
# Đẩy model lên GPU và bật chế độ tối ưu bộ nhớ
pipe.to("cuda")

def generate_local_image(meaning_text, filename):
    path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(path):
        return  # Bỏ qua nếu ảnh đã tồn tại
        
    try:
        # Tối ưu hóa prompt ngắn gọn, tập trung thẳng vào phong cách Flashcard tối giản
        # enhanced_prompt = f"A clean, minimalist vector illustration of {meaning_text}, white background, educational flashcard style, no words, simple shapes."
        enhanced_prompt = f"A clean, minimalist illustration of '{meaning_text}'"
        # Sinh ảnh với SANA (Cực kỳ nhanh và chuẩn xác)
        image = pipe(
            prompt=enhanced_prompt,
            height=512,
            width=512,
            guidance_scale=5.0,       # Giúp mô hình bám sát ý nghĩa của từ hơn
            num_inference_steps=16,   # Bước chạy tối ưu cho chất lượng ảnh sắc nét của SANA
        ).images[0]
        
        image.save(path)
        print(f"✓ Đã sinh ảnh cho: {filename}: '{meaning_text}'")
    except Exception as e:
        print(f"✗ Lỗi khi sinh ảnh cho nghĩa '{meaning_text}': {e}")

def main():
    df = pd.read_csv(CSV_FILE)
    print(f"Bắt đầu sinh {len(df)} hình ảnh...")
    
    test_count = 0
    for index, row in df.iterrows():
        vocab = str(row[VOCAB_COLUMN]).strip()
        meaning = str(row[MEANING_COLUMN]).strip()
        
        if not vocab or vocab == 'nan':
            continue
            
        filename = f"{vocab}.jpg"
        
        if ";" in meaning:
            first_meaning = meaning.split(";")[0].strip()
        else:
            first_meaning = meaning
        # Truyền cột "Meaning" (Tiếng Anh) vào để model hiểu và vẽ chính xác
        generate_local_image(first_meaning, filename)
        
        test_count += 1
        if test_count >= 20:  # Giới hạn thử nghiệm 10 từ đầu
            break

if __name__ == "__main__":
    main()