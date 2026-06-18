import os
import asyncio
import pandas as pd
import edge_tts

# 1. Cấu hình đường dẫn
CSV_FILE = "chinese_words.csv"  # Thay bằng tên file CSV của bạn
OUTPUT_FOLDER = "mp3"          # Thư mục sẽ chứa các file MP3
VOCAB_COLUMN = "Vocab"         # Tên cột chứa chữ Hán trong file CSV của bạn

# Chọn giọng đọc tiếng Trung Phổ Thông (Mandarin)
# Một số giọng hay: 
# - 'zh-CN-XiaoxiaoNeural' (Giọng nữ, rất tự nhiên, khuyên dùng)
# - 'zh-CN-YunyangNeural' (Giọng nam, ấm áp, phù hợp đọc từ vựng)
VOICE = 'zh-CN-XiaoxiaoNeural' 

# Tạo thư mục đầu ra nếu chưa tồn tại
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

async def download_audio(text, filename):
    """Hàm bất đồng bộ để tải âm thanh từ Edge TTS"""
    path = os.path.join(OUTPUT_FOLDER, filename)
    
    # Bỏ qua nếu file đã tồn tại (để tránh tải lại nếu script bị ngắt quãng giữa chừng)
    if os.path.exists(path):
        return
        
    try:
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(path)
        print(f"✓ Đã tải: {filename}")
    except Exception as e:
        print(f"✗ Lỗi khi tải từ '{text}': {e}")

async def main():
    # 2. Đọc file CSV bằng pandas
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print(f"Không tìm thấy file {CSV_FILE}. Vui lòng kiểm tra lại đường dẫn!")
        return

    print(f"Tìm thấy {len(df)} từ vựng trong file CSV. Bắt đầu tải âm thanh...")

    # 3. Duyệt qua từng hàng để tải file
    for index, row in df.iterrows():
        vocab = str(row[VOCAB_COLUMN]).strip()
        
        # Bỏ qua nếu ô dữ liệu bị trống
        if not vocab or vocab == 'nan':
            continue
            
        # Đặt tên file (Ví dụ: "老师.mp3")
        # Lưu ý: Nếu từ vựng có ký tự đặc biệt không hợp lệ làm tên file, bạn có thể thay bằng id hoặc pinyin
        filename = f"{vocab}.mp3" 
        
        # Gọi hàm tải âm thanh
        await download_audio(vocab, filename)
        
        # Thêm một khoảng nghỉ nhỏ (0.1 giây) để tránh gửi request quá dồn dập lên server
        await asyncio.sleep(0.1)

    print("\n🎉 Hoàn thành! Tất cả các file MP3 đã được lưu trong thư mục:", OUTPUT_FOLDER)

# Chạy chương trình
if __name__ == "__main__":
    asyncio.run(main())