# 🗺️ Phayathai Campus Trash & Bin Finder Map
### คณะวิทยาศาสตร์ มหาวิทยาลัยมหิดล (พญาไท)

เว็บแอปพลิเคชันสำหรับค้นหาจุดทิ้งขยะและถังขยะคัดแยกใน 17 อาคารของคณะวิทยาศาสตร์ มหาวิทยาลัยมหิดล พญาไท พัฒนาด้วยภาษา Python ล้วนด้วยเฟรมเวิร์ก **Plotly Dash** (ไม่ใช้ JavaScript) และจัดการ Environment ด้วย **uv**

---

## 🛠️ 1. เทคโนโลยีที่ใช้ (Tech Stack)
- **Python**: 3.12+ (จัดการสภาพแวดล้อมและแพ็กเกจด้วย `uv`)
- **Web Framework**: Plotly Dash (`dash`, `dash.dcc`, `dash.html`, `dash.Input`, `dash.Output`, `dash.State`)
- **Map & Data Visualization**: `plotly.graph_objects`
- **Data Manipulation**: `pandas`

---

## 🏢 2. รายชื่อ 17 อาคารที่รองรับ
1. Lecture Building (L) - อาคารบรรยายรวม
2. Chemistry Building (C) - อาคารเคมี
3. Computer Building - อาคารคอมพิวเตอร์
4. Biology Building (B) - อาคารชีววิทยา
5. New Biology Building (N) - อาคารชีววิทยาใหม่
6. Research Building (R) - อาคารวิจัย
7. Physics Building (P) - อาคารฟิสิกส์
8. Preclinic Building (Pr) - อาคารพรีคลินิก
9. Anatomy Building 1 (AN1) - อาคารกายวิภาคศาสตร์ 1
10. Anatomy Building 2 (AN2) - อาคารกายวิภาคศาสตร์ 2
11. Multidisciplinary Building (M) - อาคารสหวิทยาการ
12. Biotechnology Building (BT) - อาคารเทคโนโลยีชีวภาพ
13. Chalermphrakiet Building (K) - อาคารเฉลิมพระเกียรติ
14. Laboratory Animal Facility Building (AF) - อาคารศูนย์สัตว์ทดลอง
15. Stang Mongkolsuk Building (ST) - อาคารสตางค์ มงคลสุข
16. Venture Club@MUSC Building (V) - อาคาร Venture Club
17. National Doping Control Centre (NDCC) - ศูนย์ตรวจสารต้องห้ามในนักกีฬา

---

## 🚀 3. วิธีติดตั้งและรันโปรเจกต์ด้วย `uv`

### 1) ติดตั้งโปรเจกต์และ dependencies
```bash
# ติดตั้ง uv (หากยังไม่มีในเครื่อง)
# Windows PowerShell:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# เดินทางไปยังโฟลเดอร์โปรเจกต์
cd musc-bin-finder

# ติดตั้งไลบรารีที่จำเป็น
uv add dash plotly pandas
```

### 2) เริ่มต้นรันเซิร์ฟเวอร์
```bash
uv run app.py
```

จากนั้นเปิดเว็บเบราว์เซอร์ไปที่: **`http://127.0.0.1:8050`**

---

## 📌 4. วิธีนำข้อมูลตำแหน่งถังขยะจริงมาใส่ในอนาคต

เมื่อคุณได้ข้อมูลตำแหน่งจริงของถังขยะ สามารถนำมาใส่ได้ 2 วิธี:

### วิธีที่ 1: แก้ไขในตัวแปร `MOCK_BINS` ภายในไฟล์ `app.py`
คุณสามารถเพิ่มหรือแทนที่รายการพจนานุกรมในตัวแปร `MOCK_BINS` โดยกำหนดฟิลด์ดังนี้:
```python
{
    "bin_id": "BIN-L-101",                     # รหัสถังขยะ
    "building_id": "L",                        # รหัสอาคาร (ตรงกับ BUILDINGS)
    "building_name": "Lecture Building (L)",   # ชื่ออาคาร
    "floor": 1,                                # ชั้น (ตัวเลข เช่น 1, 2, 3)
    "bin_type": "recycle",                     # 'recycle' | 'general' | 'organic' | 'hazardous' | 'e-waste'
    "x": 25.5,                                 # พิกัดแนวนอน สเกล 0 ถึง 100
    "y": 40.0,                                 # พิกัดแนวตั้ง สเกล 0 ถึง 100
    "location_desc": "ใกล้ทางเข้าฝั่งทิศเหนือ",   # คำอธิบายจุดสังเกต
    "accepted_items": "ขวดพลาสติก PET, กระป๋อง", # สิ่งของที่ทิ้งได้
    "prohibited_items": "เศษอาหาร, สารเคมี",     # สิ่งของที่ห้ามทิ้ง
    "status": "พร้อมใช้งาน"                     # สถานะ
}
```

### วิธีที่ 2: โหลดข้อมูลจากไฟล์ CSV หรือ Excel
สร้างไฟล์ `bins_data.csv` แล้วแทนที่บรรทัด `df_bins = pd.DataFrame(MOCK_BINS)` ใน `app.py` ด้วย:
```python
df_bins = pd.read_csv("bins_data.csv")
```

---

## 🖼️ 5. วิธีนำรูปภาพผังอาคารจริงมาใส่ (Floor Plan Image)
ระบบได้ออกแบบให้รองรับรูปภาพผังจริงทันที โดยตั้งชื่อไฟล์เป็น:
`assets/floorplans/{building_id}_{floor}.png`
ตัวอย่างเช่น:
- `assets/floorplans/L_1.png` (อาคาร L ชั้น 1)
- `assets/floorplans/C_1.png` (อาคาร C ชั้น 1)
- `assets/floorplans/K_2.png` (อาคาร K ชั้น 2)

*หากยังไม่มีไฟล์รูป ระบบจะแสดง Blueprint ผังอาคารจำลองคุณภาพสูงพร้อมเส้นตารางกริดและสเกล 0-100 ให้อัตโนมัติ*

---

## 💡 6. เครื่องมือช่วยอ่านพิกัด (Coordinate Tool)
ในตัวเว็บแอปพลิเคชัน มีฟังก์ชัน **Coordinate Tool** เมื่อคลิกบนผังอาคาร ระบบจะแสดงค่า `X: 0 - 100` และ `Y: 0 - 100` ให้ทันที เพื่อให้คุณสามารถจดพิกัดไปกรอกในฐานข้อมูลได้อย่างแม่นยำ
