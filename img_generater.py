import os
import torch
import pandas as pd
from diffusers import FluxPipeline

# 1. Cấu hình đường dẫn
CSV_FILE = "chinese_words.csv"
OUTPUT_FOLDER = "img"
MEANING_COLUMN = "Meaning"
VOCAB_COLUMN = "Vocab"

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# 2. Khởi tạo mô hình FLUX.1-schnell tối ưu cho RTX 3090
print("Đang tải model Flux vào RTX 3090...")
pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-schnell", 
    torch_dtype=torch.bfloat16
)
# Đẩy model lên GPU
pipe.to("cuda") 

def generate_local_image(prompt, filename):
    path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(path):
        return # Bỏ qua nếu ảnh đã tồn tại
        
    try:
        # Thêm phong cách vào prompt để ảnh đồng bộ và trực quan (VD: dạng minh họa cho trẻ em, sạch sẽ)
        enhanced_prompt = f"A clean, minimalist vector illustration of {prompt}, white background, educational flashcard style"
        
        # Sinh ảnh (Flux-schnell chỉ cần 4 steps là rất đẹp)
        image = pipe(
            prompt=enhanced_prompt,
            guidance_scale=0.0,
            num_inference_steps=4,
            max_sequence_length=256
        ).images[0]
        
        # Resize về kích thước vừa phải để tối ưu dung lượng bộ thẻ Anki
        image = image.resize((512, 512))
        image.save(path)
        print(f"✓ Đã sinh ảnh cho: {filename}")
    except Exception as e:
        print(f"✗ Lỗi khi sinh ảnh '{prompt}': {e}")

def main():
    df = pd.read_csv(CSV_FILE)
    print(f"Bắt đầu sinh {len(df)} hình ảnh...")
    
    for index, row in df.iterrows():
        vocab = str(row[VOCAB_COLUMN]).strip()
        meaning = str(row[MEANING_COLUMN]).strip()
        
        if not vocab or vocab == 'nan':
            continue
            
        filename = f"{vocab}.jpg"
        generate_local_image(meaning, filename)

if __name__ == "__main__":
    main()