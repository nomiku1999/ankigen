import json
import os
import pandas as pd

JSON_INPUT_FILE = "complete.json"
CSV_OUTPUT_FILE = "chinese_words.csv"


def convert_json_to_csv(json_path, csv_path):
    if not os.path.exists(json_path):
        print(
            f"✗ Không tìm thấy file {json_path}. Vui lòng kiểm tra lại đường dẫn!"
        )
        return

    with open(json_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"✗ Lỗi định dạng file JSON: {e}")
            return

    # Nếu JSON gốc là một object đơn lẻ, bọc nó lại thành list để xử lý thống nhất
    if isinstance(data, dict):
        data = [data]

    parsed_records = []

    # 2. Duyệt qua từng từ trong file JSON
    for item in data:
        # Lọc điều kiện: Chỉ chọn từ có frequency < 3000
        frequency = item.get("frequency", 0)
        if frequency >= 4000:
            continue

        vocab = item.get("simplified", "").strip()
        forms = item.get("forms", [])

        # Kiểm tra nếu từ có chứa thông tin trong danh sách forms
        if forms and len(forms) > 0:
            # Yêu cầu: Chỉ lấy form đầu tiên
            first_form = forms[0]

            # Lấy pinyin từ cấu trúc transcriptions
            transcriptions = first_form.get("transcriptions", {})
            pinyin = transcriptions.get("pinyin", "").strip()

            # Lấy danh sách meanings và gộp lại thành 1 chuỗi tiếng Anh
            meanings_list = first_form.get("meanings", [])
            # Gộp các nghĩa lại bằng dấu chấm phẩy "; "
            meaning_en = "; ".join(meanings_list)

            # Lưu vào danh sách kết quả
            parsed_records.append(
                {"Vocab": vocab, "Pinyin": pinyin, "Meaning": meaning_en}
            )

    # 3. Tạo DataFrame và xuất ra file CSV
    df = pd.DataFrame(parsed_records)

    # Đảm bảo không ghi đè nếu kết quả rỗng
    if not df.empty:
        df.to_csv(csv_path, index=False, encoding="utf-8")
        print(f"✓ Thành công! Đã lọc và xuất {len(df)} từ ra file: {csv_path}")
    else:
        print("⚠ Không có từ nào thỏa mãn điều kiện tần suất (frequency < 3000).")


if __name__ == "__main__":
    convert_json_to_csv(JSON_INPUT_FILE, CSV_OUTPUT_FILE)