import pandas as pd
import json

# 1. Đọc dữ liệu đã xuất từ PDF ra Excel
df_nganh = pd.read_csv("danh_muc_tat_ca_nganh.csv") 

# Danh sách các mã ngành độc hại trích từ Thông tư 05/2023 (Bạn cập nhật thêm các mã)
danh_muc_doc_hai = ["5510202", "6510202", "6720301", "5510216", "6510216", "6520123"]

json_output = []

for index, row in df_nganh.iterrows():
    ma_nganh = str(row['ma_nganh'])
    ten_nganh = row['ten_nganh']
    
    # Xác định bậc đào tạo dựa trên số đầu tiên của mã ngành
    if ma_nganh.startswith("5"):
        bac = "Trung cấp"
        co_quan = "Bộ LĐ-TB&XH"
        van_ban = "Thông tư số 26/2020/TT-BLĐTBXH"
    elif ma_nganh.startswith("6"):
        bac = "Cao đẳng"
        co_quan = "Bộ LĐ-TB&XH"
        van_ban = "Thông tư số 26/2020/TT-BLĐTBXH"
    elif ma_nganh.startswith("7"):
        bac = "Đại học"
        co_quan = "Bộ GD&ĐT"
        van_ban = "Thông tư số 09/2022/TT-BGDĐT"
    elif ma_nganh.startswith("8"):
        bac = "Thạc sĩ"
        co_quan = "Bộ GD&ĐT"
        van_ban = "Thông tư số 09/2022/TT-BGDĐT"
    elif ma_nganh.startswith("9"):
        bac = "Tiến sĩ"
        co_quan = "Bộ GD&ĐT"
        van_ban = "Thông tư số 09/2022/TT-BGDĐT"
    else:
        bac = "Khác"
        
    # Mapping tính chất độc hại
    is_doc_hai = True if ma_nganh in danh_muc_doc_hai else False
    ghi_chu_suc_khoe = "Thuộc TT 05/2023/TT-BLĐTBXH" if is_doc_hai else "Bình thường"

    # Đóng gói JSON
    record = {
        "page_content": f"Ngành đào tạo: {ten_nganh}. Hệ đào tạo: {bac}. Mã ngành: {ma_nganh}.",
        "metadata": {
            "ma_nganh": ma_nganh,
            "ten_nganh": ten_nganh,
            "bac_dao_tao": bac,
            "co_quan_quan_ly": co_quan,
            "van_ban_phap_ly": van_ban,
            "hoc_tap_doc_hai_nguy_hiem": is_doc_hai,
            "can_cu_suc_khoe": ghi_chu_suc_khoe
        }
    }
    json_output.append(record)

# Xuất ra file chuẩn để nạp ChromaDB
with open("full_career_knowledge.json", "w", encoding="utf-8") as f:
    json.dump(json_output, f, ensure_ascii=False, indent=4)
    
print("Đã tạo thành công file JSON toàn bộ danh mục ngành nghề!")