"""
เว็บแอปพลิเคชัน: Phayathai Campus Trash & Bin Finder Map 
คณะวิทยาศาสตร์ มหาวิทยาลัยมหิดล (พญาไท) 
พัฒนาด้วย: Python + Plotly Dash (Pure Python, No JavaScript) 
เวอร์ชัน: ผสานโลโก้ MUSC_BIN + SEO Meta Tags เข้ากับระบบค้นหา 300 รายการและข้อมูลล่าสุด
"""
import os
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State, ALL, ctx, no_update

# =============================================================================
# 1. โหลดฐานข้อมูลรายการสิ่งของ 300 รายการจาก waste_classification_300_items.csv
# =============================================================================
def load_waste_catalog(csv_filename="waste_classification_300_items.csv"):
    base_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "."
    csv_path = os.path.join(base_dir, csv_filename)
    if not os.path.exists(csv_path):
        csv_path = csv_filename
    if not os.path.exists(csv_path):
        print(f"⚠️ ไม่พบไฟล์ {csv_filename} ระบบจะค้นหาจากข้อมูลถังขยะในอาคารแทน")
        return []

    df = pd.read_csv(csv_path)
    catalog = []
    for _, row in df.iterrows():
        w_en = str(row.get("waste_type_en", "")).strip()
        sub = str(row.get("หมวดหมู่ย่อย", "")).strip()
        name = str(row.get("รายการสิ่งของ", "")).strip()
        type_th = str(row.get("ประเภทขยะ", "")).strip()

        if w_en == "General Waste":
            bin_type = "general"
        elif w_en == "Recycle Waste":
            bin_type = "recycle"
        elif w_en == "Hazardous Waste":
            if sub in ["แบตเตอรี่และแหล่งจ่ายไฟ", "ขยะอิเล็กทรอนิกส์ขนาดเล็ก (E-Waste)"]:
                bin_type = "e-waste"
            else:
                bin_type = "hazardous"
        else:
            bin_type = "general"

        catalog.append({
            "name": name,
            "sub": sub,
            "type_th": type_th,
            "bin_type": bin_type
        })
    return catalog

WASTE_ITEMS_CATALOG = load_waste_catalog()

def search_waste_catalog(search_query):
    """ค้นหาสิ่งของจากฐานข้อมูล 300 รายการ และคืนค่ารายการที่พบพร้อมประเภทถังขยะ"""
    q = (search_query or "").strip().lower()
    if not q or not WASTE_ITEMS_CATALOG:
        return [], set()

    matched_items = []
    matched_types = set()
    for item in WASTE_ITEMS_CATALOG:
        if q in item["name"].lower() or q in item["sub"].lower():
            matched_items.append(item)
            matched_types.add(item["bin_type"])
    return matched_items, matched_types


# =============================================================================
# 2. ฐานข้อมูลจุดทิ้งขยะและอาคาร
# =============================================================================
BUILDINGS_DATA = [
    {
        "num": 1, "id": "L", "name_en": "Lecture Building (L)", "name_th": "อาคาร 1 (ตึกกลม)",
        "x_pct": 56.43, "y_pct": 38.19,
        "zone": "โซนหน้าแคมปัส ติด GATE 2 และถนนพระราม 6", "floors": [1],
        "description": "อาคารบรรยายรวม (ตึกกลม) ศูนย์กลางกิจกรรมและการเรียนการสอน",
        "gates": ["GATE 2"],
        "bins": [
            {
                "id": "BIN-1-101", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป / ขยะฝังกลบ",
                "loc": " ", "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขยะรีไซเคิล, สารเคมี, ขยะมีพิษ", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-1-102", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": " ", "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "บรรจุภัณฑ์เปื้อนเศษอาหาร, ถุงแกง", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-1-103", "floor": 1, "type": "organic", "type_th": "ขยะอินทรีย์ / เศษอาหาร",
                "loc": "ใต้ต้นไม้ ตรงข้ามร้านค้า", "items": "เศษอาหาร, เปลือกผลไม้, น้ำแกง",
                "prohibited": "ถุงแกง, บรรจุภัณฑ์ที่มีเศษอาหาร", "status": "พร้อมใช้งาน"
            }
        ]
    },
    {
        "num": 2, "id": "C", "name_en": "Chemistry Building (C)", "name_th": "อาคาร 2 (อาคารเคมี)",
        "x_pct": 45.96, "y_pct": 24.79,
        "zone": "โซนหน้าฝั่งซ้าย ถัดจากตึกกลม เชื่อมต่อตึกวิจัย", "floors": [1, 4],
        "description": "ภาควิชาเคมี และห้องปฏิบัติการวิทยาศาสตร์",
        "gates": ["GATE 1", "GATE 2"],
        "bins": [
            # ชั้น 1
            {
                "id": "BIN-2-101", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป / ขยะฝังกลบ",
                "loc": "ชั้น 1 หน้าห้องน้ำ", "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขยะรีไซเคิล, ขยะอันตราย", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-2-102", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล (ขวดแก้ว, กระป๋อง)",
                "loc": "ชั้น 1 หน้าห้องน้ำ", "items": "ขวดแก้ว, กระป๋องอลูมิเนียม ที่สะอาด",
                "prohibited": "ขวดแก้วที่เปื้อนน้ำหวาน", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-2-103", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล (ขวดน้ำแห้งสะอาด)",
                "loc": "ชั้น 1 หน้าห้องน้ำ", "items": "ขวดน้ำดื่มพลาสติกใส แห้งและสะอาด",
                "prohibited": "ขวดที่มีน้ำหวานหรือเศษอาหารตกค้าง", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-2-104", "floor": 1, "type": "e-waste", "type_th": "ขยะอิเล็กทรอนิกส์",
                "loc": "ชั้น 1 หน้าห้องน้ำ", "items": "แบตเตอรี่, ถ่านไฟฉาย, หลอดไส้",
                "prohibited": "ขยะทั่วไป, ขยะเปียก", "status": "พร้อมใช้งาน"
            },
            # ชั้น 4
            {
                "id": "BIN-2-401", "floor": 4, "type": "general", "type_th": "ขยะทั่วไป",
                "loc": "ชั้น 4 ทางเดินหน้าห้องปฏิบัติการ", "items": "พลาสติกห่ออาหาร, ถุงแกง, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขยะรีไซเคิลสะอาด", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-2-402", "floor": 4, "type": "organic", "type_th": "ขยะย่อยสลายได้",
                "loc": "ชั้น 4 ทางเดินหน้าห้องปฏิบัติการ", "items": "เศษผัก ผลไม้, เศษอาหาร, เศษเนื้อสัตว์",
                "prohibited": "ถุงพลาสติก, บรรจุภัณฑ์", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-2-403", "floor": 4, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "ชั้น 4 ทางเดินหน้าห้องปฏิบัติการ", "items": "แก้วพลาสติก, เศษกระดาษ, ถุงพลาสติกหูหิ้ว (*Note ต้องเป็นขยะที่สะอาด ไม่เปื้อนเศษอาหาร*)",
                "prohibited": "ขยะเปื้อนคราบมันและเศษอาหาร", "status": "พร้อมใช้งาน"
            }
        ]
    },
    {
        "num": 5, "id": "N", "name_en": "New Biology Building (N)", "name_th": "อาคาร 5 (อาคารชีววิทยาใหม่)",
        "x_pct": 36.22, "y_pct": 14.17,
        "zone": "โซนหลังฝั่งซ้าย ใกล้อาคารสตางค์ มงคลสุข", "floors": [],
        "description": "อาคารเรียนและวิจัยขั้นสูงด้านชีววิทยา",
        "gates": ["GATE 1"],
        "bins": []  # Not available ตามเอกสาร
    },
    {
        "num": 7, "id": "P", "name_en": "Physics Building (P)", "name_th": "อาคาร 7 (อาคารฟิสิกส์)",
        "x_pct": 64.66, "y_pct": 20.51,
        "zone": "โซนกลางฝั่งขวา เชื่อมต่ออาคารวิจัยและอาคารเฉลิมพระเกียรติ", "floors": [1, 4, 5, 6],
        "description": "ภาควิชาฟิสิกส์ และห้องปฏิบัติการฟิสิกส์",
        "gates": ["GATE 2", "GATE 3"],
        "bins": [
            # ชั้น 1
            {
                "id": "BIN-7-101", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป / ขยะฝังกลบ",
                "loc": "ใต้ตึกฟิสิกส์", "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขยะรีไซเคิล, สารเคมี", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-7-102", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "ใต้ตึกฟิสิกส์", "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "บรรจุภัณฑ์เปื้อนเศษอาหาร", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-7-103", "floor": 1, "type": "e-waste", "type_th": "ขยะอิเล็กทรอนิกส์",
                "loc": "ใต้ตึกฟิสิกส์", "items": "แบตเตอรี่, ถ่านไฟฉาย, แผงวงจร",
                "prohibited": "ขยะทั่วไป", "status": "พร้อมใช้งาน"
            },
            # ชั้น 4
            {
                "id": "BIN-7-401", "floor": 4, "type": "general", "type_th": "ขยะทั่วไป / ขยะฝังกลบ",
                "loc": "ชั้น 4 โถงทางเดิน", "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขยะรีไซเคิล", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-7-402", "floor": 4, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "ชั้น 4 โถงทางเดิน", "items": "ขวดน้ำพลาสติก",
                "prohibited": "บรรจุภัณฑ์เปื้อนเศษอาหาร, ถุงแกง", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-7-403", "floor": 4, "type": "organic", "type_th": "ขยะอินทรีย์",
                "loc": "ชั้น 4 โถงทางเดิน", "items": "เศษอาหาร, เปลือกผลไม้",
                "prohibited": "ถุงพลาสติก, โฟม", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-7-404", "floor": 4, "type": "recycle", "type_th": "ถังแยกเศษกระดาษ",
                "loc": "ชั้น 4 โถงทางเดิน", "items": "เศษกระดาษที่ไม่ได้ใช้แล้ว, ลังกระดาษ",
                "prohibited": "กระดาษเปื้อนคราบอาหาร, ทิชชู่ใช้แล้ว", "status": "พร้อมใช้งาน"
            },
            # ชั้น 5
            {
                "id": "BIN-7-501", "floor": 5, "type": "general", "type_th": "ขยะทั่วไป / ขยะฝังกลบ",
                "loc": "ชั้น 5 โถงกลาง", "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร, เทปกาว",
                "prohibited": "ขยะรีไซเคิล", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-7-502", "floor": 5, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "ชั้น 5 โถงกลาง", "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, ขวดแก้ว",
                "prohibited": "บรรจุภัณฑ์เปื้อนเศษอาหาร", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-7-503", "floor": 5, "type": "recycle", "type_th": "ตะกร้าสำหรับแยกบรรจุภัณฑ์",
                "loc": "ชั้น 5 จุดแยกขยะพิเศษ", "items": "แก้วพลาสติก, ถ้วยมาม่า, กล่องอาหาร (*Note ต้องเทเศษอาหารออก และล้างให้สะอาดก่อน*)",
                "prohibited": "บรรจุภัณฑ์ที่มีเศษอาหารตกค้าง", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-7-504", "floor": 5, "type": "general", "type_th": "ตะกร้าสำหรับแยกตะเกียบและไม้เสียบลูกชิ้น",
                "loc": "ชั้น 5 จุดแยกขยะพิเศษ", "items": "ตะเกียบไม้, ตะเกียบพลาสติก, ไม้เสียบลูกชิ้น",
                "prohibited": "ขยะมีคมอื่นๆ", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-7-505", "floor": 5, "type": "recycle", "type_th": "ตะกร้าสำหรับแยกหลอดพลาสติก",
                "loc": "ชั้น 5 จุดแยกขยะพิเศษ", "items": "หลอดพลาสติกทุกชนิด",
                "prohibited": "ขยะทั่วไป", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-7-506", "floor": 5, "type": "recycle", "type_th": "ตะกร้าสำหรับแยกฝาขวดน้ำ",
                "loc": "ชั้น 5 จุดแยกขยะพิเศษ", "items": "ฝาขวดน้ำพลาสติกทุกขนาด",
                "prohibited": "ฝาโลหะมีคม", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-7-507", "floor": 5, "type": "recycle", "type_th": "ตะกร้าสำหรับแยกกล่องนม / กล่องน้ำผลไม้",
                "loc": "ชั้น 5 จุดแยกขยะพิเศษ", "items": "กล่องนม, กล่องน้ำผลไม้ (*Note ต้องล้างให้สะอาดก่อน*)",
                "prohibited": "กล่องที่มีน้ำบูดหรือเศษอาหารตกค้าง", "status": "พร้อมใช้งาน"
            },
            # ชั้น 6
            {
                "id": "BIN-7-601", "floor": 6, "type": "recycle", "type_th": "ถังแยกเศษกระดาษ",
                "loc": "ชั้น 6 ทางเดินชั้น 6", "items": "เศษกระดาษที่ไม่ได้ใช้แล้ว, ลังกระดาษ",
                "prohibited": "กระดาษเปื้อนอาหาร", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-7-602", "floor": 6, "type": "general", "type_th": "ขยะทั่วไป / ขยะฝังกลบ",
                "loc": "ชั้น 6 ทางเดินชั้น 6", "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขยะรีไซเคิล", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-7-603", "floor": 6, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "ชั้น 6 ทางเดินชั้น 6", "items": "ขวดพลาสติก",
                "prohibited": "ขยะทั่วไป", "status": "พร้อมใช้งาน"
            }
        ]
    },
    {
        "num": 11, "id": "M", "name_en": "Multidisciplinary Building (M)", "name_th": "อาคาร 11 (อาคารอเนกประสงค์ / สหวิทยาการ)",
        "x_pct": 52.02, "y_pct": 8.77,
        "zone": "โซนหลังตรงกลาง ใกล้ GATE 6", "floors": [1, 2, 3],
        "description": "ศูนย์ประชุมสัมมนา ลานกิจกรรมอเนกประสงค์ และสำนักงานหลักสูตร",
        "gates": ["GATE 6"],
        "bins": [
            # ชั้น 1
            {
                "id": "BIN-11-101", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป / ขยะฝังกลบ",
                "loc": "ชั้น 1 โรงอาหาร", "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขยะรีไซเคิล", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-11-102", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "ชั้น 1 โรงอาหาร", "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "บรรจุภัณฑ์เปื้อนเศษอาหาร, ถุงแกง", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-11-103", "floor": 1, "type": "organic", "type_th": "ถังทิ้งเศษอาหารของโรงอาหาร",
                "loc": "ชั้น 1 บริเวณโรงอาหาร", "items": "ทิ้งเศษอาหารปริมาณมากได้, เปลือกผลไม้, เศษผัก",
                "prohibited": "ถุงพลาสติก, ภาชนะใส่อาหาร, ช้อนส้อมพลาสติก", "status": "พร้อมใช้งาน"
            },
            # ชั้น 2
            {
                "id": "BIN-11-201", "floor": 2, "type": "general", "type_th": "ขยะทั่วไป / ขยะฝังกลบ",
                "loc": "ชั้น 2 ระเบียงทางเดิน", "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขยะรีไซเคิล", "status": "พร้อมใช้งาน"
            },
            # ชั้น 3
            {
                "id": "BIN-11-301", "floor": 3, "type": "general", "type_th": "ขยะทั่วไป / ขยะฝังกลบ",
                "loc": "ชั้น 3 ระเบียงทางเดิน", "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขยะรีไซเคิล", "status": "พร้อมใช้งาน"
            }
        ]
    },
    {
        "num": 13, "id": "K", "name_en": "Chalermphrakiet Building (K)", "name_th": "อาคาร 13 (อาคารเฉลิมพระเกียรติ - บริเวณหลังลิฟต์)",
        "x_pct": 74.37, "y_pct": 32.82,
        "zone": "โซนหน้าฝั่งขวา ติดถนนพระราม 6 และ GATE 3", "floors": [1, 4, 5],
        "description": "ศูนย์รวมห้องวิจัยขั้นสูง และสำนักงานคณบดี คณะวิทยาศาสตร์",
        "gates": ["GATE 3", "GATE 4"],
        "bins": [
            # ชั้น 1
            {
                "id": "BIN-13-101", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป / ขยะฝังกลบ",
                "loc": "ชั้น 1 บริเวณหลังลิฟต์", "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขยะรีไซเคิล", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-13-102", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "ชั้น 1 บริเวณหลังลิฟต์", "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "บรรจุภัณฑ์เปื้อนเศษอาหาร", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-13-103", "floor": 1, "type": "e-waste", "type_th": "ขยะอิเล็กทรอนิกส์",
                "loc": "ชั้น 1 บริเวณหลังลิฟต์", "items": "แบตเตอรี่, ถ่านไฟฉาย, แผงวงจร",
                "prohibited": "ขยะทั่วไป", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-13-104", "floor": 1, "type": "recycle", "type_th": "Drop Box",
                "loc": "ชั้น 1 บริเวณหลังลิฟต์", "items": "สำหรับแยกถุงพลาสติกที่สะอาด ที่สามารถนำมาใช้ซ้ำได้",
                "prohibited": "ถุงพลาสติกเปื้อนอาหารหรือเปียกชื้น", "status": "พร้อมใช้งาน"
            },
            # ชั้น 4
            {
                "id": "BIN-13-401", "floor": 4, "type": "general", "type_th": "ขยะทั่วไป / ขยะฝังกลบ",
                "loc": "ชั้น 4 บริเวณหลังลิฟต์", "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขยะรีไซเคิล", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-13-402", "floor": 4, "type": "recycle", "type_th": "ขยะรีไซเคิล (ขวดแก้ว, กระป๋อง)",
                "loc": "ชั้น 4 บริเวณหลังลิฟต์", "items": "ขวดแก้ว, กระป๋องอลูมิเนียม ที่สะอาด",
                "prohibited": "ขวดแก้วที่เปื้อนน้ำหวาน", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-13-403", "floor": 4, "type": "recycle", "type_th": "ขยะรีไซเคิล (ขวดน้ำแห้งสะอาด)",
                "loc": "ชั้น 4 บริเวณหลังลิฟต์", "items": "ขวดน้ำพลาสติกใส แห้งสะอาด",
                "prohibited": "ขวดน้ำที่มีเศษอาหารหรือน้ำหวานค้างอยู่", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-13-404", "floor": 4, "type": "organic", "type_th": "ขยะอินทรีย์",
                "loc": "ชั้น 4 บริเวณหลังลิฟต์", "items": "เปลือกผลไม้, เศษผัก, เศษอาหารปริมาณไม่มาก",
                "prohibited": "ถุงแกง, บรรจุภัณฑ์พลาสติก", "status": "พร้อมใช้งาน"
            },
            # ชั้น 5
            {
                "id": "BIN-13-501", "floor": 5, "type": "general", "type_th": "ขยะทั่วไป / ขยะฝังกลบ",
                "loc": "ชั้น 5 บริเวณหลังลิฟต์", "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขยะรีไซเคิล", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-13-502", "floor": 5, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "ชั้น 5 บริเวณหลังลิฟต์", "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "บรรจุภัณฑ์เปื้อนอาหาร", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-13-503", "floor": 5, "type": "recycle", "type_th": "ขยะรีไซเคิล (ขวดแก้ว, กระป๋อง)",
                "loc": "ชั้น 5 บริเวณหลังลิฟต์", "items": "ขวดแก้ว, กระป๋องอลูมิเนียม ที่สะอาด",
                "prohibited": "ขวดแก้วที่เปื้อนน้ำหวาน", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-13-504", "floor": 5, "type": "recycle", "type_th": "ขยะรีไซเคิล (ขวดน้ำแห้งสะอาด)",
                "loc": "ชั้น 5 บริเวณหลังลิฟต์", "items": "ขวดน้ำพลาสติกใส แห้งสะอาด",
                "prohibited": "ขวดน้ำหวานเปื้อนคราบ", "status": "พร้อมใช้งาน"
            }
        ]
    },
    {
        "num": 15, "id": "ST", "name_en": "Stang Mongkolsuk Building (ST)", "name_th": "อาคาร 15 (อาคารสตางค์ มงคลสุข)",
        "x_pct": 29.73, "y_pct": 16.38,
        "zone": "โซนซ้าย ติดสนามฟุตบอลและลานจอดรถ GATE 1", "floors": [1],
        "description": "ห้องสมุดสตางค์ มงคลสุข แหล่งเรียนรู้และค้นคว้าวิจัย",
        "gates": ["GATE 1"],
        "bins": [
            {
                "id": "BIN-15-101", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป / ขยะฝังกลบ",
                "loc": "ชั้น 1 โถงทางเข้าห้องสมุด", "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขยะรีไซเคิล, ขยะอันตราย", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-15-102", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "ชั้น 1 โถงทางเข้าห้องสมุด", "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "บรรจุภัณฑ์เปื้อนอาหาร", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-15-103", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล (ขวดแก้ว, กระป๋อง)",
                "loc": "ชั้น 1 โถงทางเข้าห้องสมุด", "items": "ขวดแก้ว, กระป๋องอลูมิเนียม ที่สะอาด",
                "prohibited": "ขวดแก้วที่เปื้อนน้ำหวาน", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-15-104", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล (ขวดน้ำแห้งสะอาด)",
                "loc": "ชั้น 1 โถงทางเข้าห้องสมุด", "items": "ขวดน้ำพลาสติกใส แห้งสะอาด",
                "prohibited": "ขวดน้ำที่มีน้ำแข็งหรือเศษอาหารค้างอยู่", "status": "พร้อมใช้งาน"
            }
        ]
    },
    {
        "num": 18, "id": "P-MUSES", "name_en": "Walkway between P & MUSES Building", "name_th": "เบอร์ 18: ทางเดินระหว่างตึก P กับตึก MUSES",
        "x_pct": 58.5, "y_pct": 22.5,
        "zone": "ทางเดินเชื่อมระหว่างอาคารฟิสิกส์ (ตึก 7) และอาคาร MUSES (ตึก 3)", "floors": [1],
        "description": "จุดทิ้งขยะกลางแจ้งบริเวณทางเดินเชื่อมระหว่างตึก P และตึก MUSES",
        "gates": ["GATE 2", "GATE 3"],
        "bins": [
            {
                "id": "BIN-18-01", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป",
                "loc": "บริเวณทางเดินเชื่อมตึก P และ MUSES", "items": "ซองขนม, ซองกาแฟ, ถุงแกง, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขยะรีไซเคิล, ขยะอันตราย", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-18-02", "floor": 1, "type": "organic", "type_th": "ขยะอินทรีย์",
                "loc": "บริเวณทางเดินเชื่อมตึก P และ MUSES", "items": "เปลือกผลไม้, เศษผัก, เศษอาหารปริมาณไม่มาก",
                "prohibited": "ถุงแกง, บรรจุภัณฑ์พลาสติก", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-18-03", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "บริเวณทางเดินเชื่อมตึก P และ MUSES", "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "บรรจุภัณฑ์เปื้อนเศษอาหาร", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-18-04", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล (ขวดแก้ว, กระป๋อง)",
                "loc": "บริเวณทางเดินเชื่อมตึก P และ MUSES", "items": "ขวดแก้ว, กระป๋องอลูมิเนียม ที่สะอาด",
                "prohibited": "ขวดแก้วที่เปื้อนน้ำหวานหรือคราบสกปรก", "status": "พร้อมใช้งาน"
            }
        ]
    },
    {
        "num": 19, "id": "7-11", "name_en": "Opposite 7-Eleven", "name_th": "เบอร์ 19: ตรงข้าม 7-Eleven",
        "x_pct": 51.5, "y_pct": 29.5,
        "zone": "บริเวณทางเดินหน้าโรงอาหารและร้านค้า ตรงข้ามเซเว่น อีเลฟเว่น", "floors": [1],
        "description": "จุดคัดแยกขยะหน้าร้านค้าและโรงอาหาร บริเวณตรงข้าม 7-11",
        "gates": ["GATE 2"],
        "bins": [
            {
                "id": "BIN-19-01", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป",
                "loc": "ตรงข้าม 7-11", "items": "ซองขนม, ซองกาแฟ, ถุงแกง, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขยะรีไซเคิลสะอาด", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-19-02", "floor": 1, "type": "organic", "type_th": "ขยะอินทรีย์",
                "loc": "ตรงข้าม 7-11", "items": "เปลือกผลไม้, เศษผัก, เศษอาหารปริมาณไม่มาก",
                "prohibited": "ถุงแกง, บรรจุภัณฑ์พลาสติก", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-19-03", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล (ขวดแก้ว, กระป๋อง)",
                "loc": "ตรงข้าม 7-11", "items": "ขวดแก้ว, กระป๋องอลูมิเนียม ที่สะอาด",
                "prohibited": "ขวดแก้วที่เปื้อนน้ำหวาน", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-19-04", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล (ขวดน้ำแห้งสะอาด)",
                "loc": "ตรงข้าม 7-11", "items": "ขวดน้ำพลาสติกใส แห้งสะอาด",
                "prohibited": "ขวดน้ำที่มีของเหลวตกค้าง", "status": "พร้อมใช้งาน"
            }
        ]
    }
]

BIN_TYPE_COLORS = {
    "recycle": "#E67E22",
    "general": "#2980B9",
    "organic": "#27AE60",
    "hazardous": "#C0392B",
    "e-waste": "#8E44AD"
}

BIN_TYPE_LABELS_TH = {
    "recycle": "🟡 ขยะรีไซเคิล (Recycle Waste)",
    "general": "🔵 ขยะทั่วไป / ขยะฝังกลบ (General Waste)",
    "organic": "🟢 ขยะอินทรีย์ / เศษอาหาร (Organic Waste)",
    "hazardous": "🔴 ขยะอันตราย (Hazardous Waste)",
    "e-waste": "🟣 ขยะอิเล็กทรอนิกส์ (E-Waste)"
}

BUILDING_BY_NUM = {b["num"]: b for b in BUILDINGS_DATA}

# =============================================================================
# 3. การสร้าง Layout Dash App
# =============================================================================
app = Dash(
    __name__,
    title="Phayathai Campus Trash & Bin Finder Map | คณะวิทยาศาสตร์ ม.มหิดล",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {
            "name": "description",
            "content": "แผนผังอาคารและจุดทิ้งขยะ คณะวิทยาศาสตร์ มหาวิทยาลัยมหิดล พญาไท"
        },
        {
            "name": "keywords",
            "content": "จุดทิ้งขยะ มหิดล พญาไท, แผนที่ คณะวิทย์ มหิดล, MUSC_BIN"
        }
    ]
)
server = app.server

def generate_building_pins():
    pins = []
    for b in BUILDINGS_DATA:
        pin = html.Button(
            id={"type": "building-pin", "index": b["num"]},
            className="building-pin-btn",
            style={
                "left": f"{b['x_pct']}%",
                "top": f"{b['y_pct']}%"
            },
            n_clicks=0,
            children=[
                str(b["num"]),
                html.Span(
                    f"{b['num']}. {b['name_th']}",
                    className="pin-tooltip-text"
                )
            ]
        )
        pins.append(pin)
    return pins

app.layout = html.Div(
    children=[
        dcc.Store(id="selected-building-store", data=1),
        dcc.Store(id="modal-open-store", data=False),
        dcc.Store(id="filter-type-store", data="all"),

        # ส่วนเนื้อหาหลัก จัดกึ่งกลางหน้าจอ
        html.Main(
            style={"maxWidth": "1050px", "margin": "15px auto", "padding": "0 15px"},
            children=[
                # ส่วนหัวแสดงโลโก้ MUSC_BIN
                html.Header(
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "14px",
                        "marginBottom": "16px",
                        "padding": "12px 18px",
                        "backgroundColor": "#ffffff",
                        "borderRadius": "12px",
                        "boxShadow": "0 2px 8px rgba(0,0,0,0.06)"
                    },
                    children=[
                        html.Img(
                            src="/assets/logo.png",
                            alt="MUSC_BIN Logo",
                            style={"height": "54px", "width": "auto", "objectFit": "contain"}
                        ),
                        html.Div([
                            html.H1(
                                "MUSC_BIN",
                                style={"margin": 0, "fontSize": "1.35rem", "color": "#0F172A", "fontWeight": "700"}
                            ),
                            html.P(
                                "ระบบค้นหาจุดทิ้งขยะ คณะวิทยาศาสตร์ มหาวิทยาลัยมหิดล (พญาไท)",
                                style={"margin": 0, "fontSize": "0.85rem", "color": "#64748B"}
                            )
                        ])
                    ]
                ),

                # แถบค้นหาและฟิลเตอร์
                html.Div(
                    className="filter-card",
                    style={"marginBottom": "15px"},
                    children=[
                        html.Div(
                            className="search-input-box",
                            children=[
                                dcc.Input(
                                    id="campus-search-input",
                                    type="text",
                                    placeholder="🔍 พิมพ์ชื่อสิ่งของที่ต้องการทิ้ง เช่น กล่องโฟม, ขวดน้ำ, ถ่านไฟฉาย, สายชาร์จ, ปากกา...",
                                    style={
                                        "width": "100%", "padding": "10px 14px",
                                        "borderRadius": "8px", "border": "1.5px solid #CBD5E1",
                                        "fontSize": "0.95rem"
                                    },
                                    debounce=True
                                )
                            ]
                        ),
                        # แถบแสดงผลการจำแนกประเภทขยะจากฐานข้อมูล 300 รายการ
                        html.Div(
                            id="search-classification-banner",
                            style={"marginTop": "10px"}
                        ),
                        html.Div(
                            className="waste-filter-pills",
                            style={"marginTop": "10px"},
                            children=[
                                html.Button("ทั้งหมด (All)", id={"type": "filter-btn", "index": "all"}, className="filter-pill-btn active", n_clicks=0),
                                html.Button("🟡 รีไซเคิล", id={"type": "filter-btn", "index": "recycle"}, className="filter-pill-btn", n_clicks=0),
                                html.Button("🔵 ทั่วไป", id={"type": "filter-btn", "index": "general"}, className="filter-pill-btn", n_clicks=0),
                                html.Button("🟢 เศษอาหาร/อินทรีย์", id={"type": "filter-btn", "index": "organic"}, className="filter-pill-btn", n_clicks=0),
                                html.Button("🔴 อันตราย", id={"type": "filter-btn", "index": "hazardous"}, className="filter-pill-btn", n_clicks=0),
                                html.Button("🟣 อิเล็กทรอนิกส์", id={"type": "filter-btn", "index": "e-waste"}, className="filter-pill-btn", n_clicks=0),
                            ]
                        )
                    ]
                ),

                # แผนที่แคมปัส
                html.Div(
                    className="campus-map-card",
                    children=[
                        html.Div(
                            className="map-card-header",
                            children=[
                                html.H2(["🗺️ แผนผังจุดทิ้งขยะ คณะวิทยาศาสตร์ พญาไท (Phayathai Campus Map)"]),
                                html.Span("👉 คลิกที่หมุดตัวเลขบนแผนที่ เพื่อดูประเภทและจุดคัดแยกขยะในแต่ละตำแหน่ง", className="map-hint-text")
                            ]
                        ),
                        html.Div(
                            id="campus-map-container",
                            className="map-canvas-container",
                            style={"position": "relative"},
                            children=[
                                html.Img(
                                    src="/assets/campus_map.png",
                                    className="campus-base-image",
                                    alt="แผนผังคณะวิทยาศาสตร์ มหาวิทยาลัยมหิดล พญาไท",
                                    style={"width": "100%", "display": "block"}
                                ),
                                html.Div(
                                    id="pins-overlay-container",
                                    children=generate_building_pins()
                                )
                            ]
                        )
                    ]
                )
            ]
        ),

        # =====================================================================
        # 4. Pop-up Modal แสดงรายละเอียดจุดทิ้งขยะ
        # =====================================================================
        html.Div(
            id="building-modal-container",
            style={"display": "none"},
            children=[
                # พื้นหลัง Backdrop
                html.Div(
                    id="modal-backdrop",
                    style={
                        "position": "fixed",
                        "top": 0, "left": 0, "width": "100vw", "height": "100vh",
                        "backgroundColor": "rgba(15, 23, 42, 0.65)",
                        "backdropFilter": "blur(4px)",
                        "zIndex": 9998
                    }
                ),
                # ตัวกล่อง Modal
                html.Div(
                    style={
                        "position": "fixed",
                        "top": "50%", "left": "50%",
                        "transform": "translate(-50%, -50%)",
                        "backgroundColor": "#ffffff",
                        "borderRadius": "18px",
                        "boxShadow": "0 25px 50px -12px rgba(0, 0, 0, 0.35)",
                        "width": "92%",
                        "maxWidth": "650px",
                        "maxHeight": "88vh",
                        "zIndex": 9999,
                        "display": "flex",
                        "flexDirection": "column",
                        "overflow": "hidden"
                    },
                    children=[
                        # Header
                        html.Div(
                            style={
                                "display": "flex",
                                "justifyContent": "space-between",
                                "alignItems": "center",
                                "padding": "16px 20px",
                                "borderBottom": "1px solid #E2E8F0",
                                "backgroundColor": "#F8FAFC"
                            },
                            children=[
                                html.Div(
                                    id="modal-header-title",
                                    style={"display": "flex", "alignItems": "center", "gap": "10px"}
                                ),
                                html.Button(
                                    "✕",
                                    id="close-modal-btn",
                                    n_clicks=0,
                                    style={
                                        "background": "#E2E8F0",
                                        "border": "none",
                                        "borderRadius": "50%",
                                        "width": "34px",
                                        "height": "34px",
                                        "fontSize": "16px",
                                        "cursor": "pointer",
                                        "fontWeight": "bold",
                                        "color": "#475569",
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center"
                                    }
                                )
                            ]
                        ),
                        # Body
                        html.Div(
                            id="modal-body-content",
                            style={"padding": "20px", "overflowY": "auto", "maxHeight": "calc(88vh - 75px)"}
                        )
                    ]
                )
            ]
        )
    ]
)

# =============================================================================
# 5. Callbacks การคลิก การค้นหา และเปิด/ปิด Pop-up Modal
# =============================================================================
@app.callback(
    Output("selected-building-store", "data"),
    Output("modal-open-store", "data"),
    Input({"type": "building-pin", "index": ALL}, "n_clicks"),
    Input("close-modal-btn", "n_clicks"),
    Input("modal-backdrop", "n_clicks"),
    State("selected-building-store", "data"),
    State("modal-open-store", "data"),
    prevent_initial_call=True
)
def manage_building_selection_and_modal(pin_clicks, close_clicks, backdrop_clicks, current_bldg, is_open):
    if not ctx.triggered_id:
        return current_bldg, is_open

    trig_id = ctx.triggered_id

    if trig_id == "close-modal-btn" or trig_id == "modal-backdrop":
        return current_bldg, False

    if isinstance(trig_id, dict):
        clicked_num = trig_id.get("index")
        if clicked_num:
            return clicked_num, True

    return current_bldg, is_open

@app.callback(
    Output("building-modal-container", "style"),
    Input("modal-open-store", "data")
)
def toggle_modal_visibility(is_open):
    if is_open:
        return {"display": "block"}
    return {"display": "none"}

@app.callback(
    Output("filter-type-store", "data"),
    Output({"type": "filter-btn", "index": ALL}, "className"),
    Input({"type": "filter-btn", "index": ALL}, "n_clicks"),
    State("filter-type-store", "data"),
    prevent_initial_call=True
)
def handle_filter_click(n_clicks_list, current_filter):
    if not ctx.triggered_id:
        return current_filter, no_update
    new_filter = ctx.triggered_id.get("index", "all")
    filter_keys = ["all", "recycle", "general", "organic", "hazardous", "e-waste"]
    class_names = [
        "filter-pill-btn active" if k == new_filter else "filter-pill-btn"
        for k in filter_keys
    ]
    return new_filter, class_names

# แสดงผลการจำแนกประเภทขยะเมื่อค้นหาสิ่งของจากรายการ 300 รายการ
@app.callback(
    Output("search-classification-banner", "children"),
    Input("campus-search-input", "value")
)
def update_search_classification_banner(search_query):
    search_q = (search_query or "").strip()
    if not search_q:
        return None

    matched_items, matched_types = search_waste_catalog(search_q)
    if not matched_items:
        return html.Div(
            f"🔎 ค้นหาคำว่า '{search_q}' ในรายการสิ่งของมาตรฐานไม่พบ (กำลังค้นหาจากรายละเอียดจุดทิ้งขยะในอาคารโดยตรง)",
            style={
                "padding": "8px 12px",
                "backgroundColor": "#F8FAFC",
                "border": "1px dashed #CBD5E1",
                "borderRadius": "8px",
                "fontSize": "0.84rem",
                "color": "#64748B"
            }
        )

    badges = []
    for b_type in ["general", "recycle", "organic", "hazardous", "e-waste"]:
        if b_type in matched_types:
            color = BIN_TYPE_COLORS.get(b_type, "#475569")
            label = BIN_TYPE_LABELS_TH.get(b_type, b_type)
            badges.append(
                html.Span(
                    label,
                    style={{
                        "backgroundColor": color,
                        "color": "#FFFFFF",
                        "padding": "3px 10px",
                        "borderRadius": "999px",
                        "fontSize": "0.8rem",
                        "fontWeight": "bold",
                        "marginRight": "6px",
                        "display": "inline-block"
                    }}
                )
            )

    sample_names = [item["name"] for item in matched_items[:5]]
    more_count = len(matched_items) - len(sample_names)
    sample_text = ", ".join(sample_names) + (f" และอีก {more_count} รายการ" if more_count > 0 else "")

    return html.Div(
        style={
            "padding": "10px 14px",
            "backgroundColor": "#F0F9FF",
            "border": "1px solid #BAE6FD",
            "borderRadius": "10px",
            "fontSize": "0.85rem"
        },
        children=[
            html.Div([
                html.Strong(f"✅ พบสิ่งของที่ตรงกับ '{search_q}' ({len(matched_items)} รายการ) → กรุณาทิ้งในถัง: ", style={"color": "#0369A1"}),
                *badges
            ], style={"marginBottom": "4px"}),
            html.Div([
                html.Span("รายการที่พบ: ", style={"fontWeight": "bold", "color": "#475569", "fontSize": "0.8rem"}),
                html.Span(sample_text, style={"color": "#334155", "fontSize": "0.8rem"})
            ])
        ]
    )

@app.callback(
    Output({"type": "building-pin", "index": ALL}, "className"),
    Input("filter-type-store", "data"),
    Input("campus-search-input", "value")
)
def update_pin_styles(filter_type, search_query):
    search_q = (search_query or "").strip().lower()
    _, catalog_matched_types = search_waste_catalog(search_q)
    classes = []

    for b in BUILDINGS_DATA:
        has_filtered_type = True
        if filter_type and filter_type != "all":
            has_filtered_type = any(bin_item["type"] == filter_type for bin_item in b["bins"])

        matches_search = True
        if search_q:
            matches_search = False
            for bin_item in b["bins"]:
                # ตรงกับประเภทถังขยะที่ค้นเจอจาก 300 รายการ หรือตรงกับข้อความในจุดทิ้งขยะโดยตรง
                if (bin_item["type"] in catalog_matched_types or
                    search_q in bin_item["items"].lower() or
                    search_q in bin_item["type_th"].lower() or
                    search_q in bin_item["loc"].lower() or
                    search_q in b["name_th"].lower() or
                    search_q in b["name_en"].lower()):
                    matches_search = True
                    break

        cls = "building-pin-btn"
        if matches_search and has_filtered_type and (filter_type != "all" or search_q):
            cls += " is-highlighted"
        elif not matches_search or not has_filtered_type:
            cls += " is-dimmed"

        classes.append(cls)
    return classes

@app.callback(
    Output("modal-header-title", "children"),
    Output("modal-body-content", "children"),
    Input("selected-building-store", "data"),
    Input("filter-type-store", "data"),
    Input("campus-search-input", "value")
)
def update_modal_content(selected_num, filter_type, search_query):
    b = BUILDING_BY_NUM.get(selected_num, BUILDINGS_DATA[0])
    search_q = (search_query or "").strip().lower()
    _, catalog_matched_types = search_waste_catalog(search_q)

    # กรองรายการถังขยะตามประเภทและคำค้นหา (รวมรายการ 300 ชิ้น)
    displayed_bins = []
    for bin_item in b["bins"]:
        if filter_type != "all" and bin_item["type"] != filter_type:
            continue
        if search_q:
            matches_catalog_type = bin_item["type"] in catalog_matched_types
            matches_direct_text = (
                search_q in bin_item["items"].lower() or
                search_q in bin_item["type_th"].lower() or
                search_q in bin_item["loc"].lower()
            )
            if not (matches_catalog_type or matches_direct_text):
                continue
        displayed_bins.append(bin_item)

    # จัดกลุ่มถังขยะตามชั้น (Floor Grouping)
    bins_by_floor = {}
    for item in displayed_bins:
        f = item.get("floor", 1)
        if f not in bins_by_floor:
            bins_by_floor[f] = []
        bins_by_floor[f].append(item)

    floor_sections = []
    sorted_floors = sorted(bins_by_floor.keys())

    for idx, f in enumerate(sorted_floors):
        floor_bins = bins_by_floor[f]
        bin_cards = []
        for item in floor_bins:
            color = BIN_TYPE_COLORS.get(item["type"], "#64748B")
            card = html.Div(
                className="bin-item-card",
                style={
                    "borderLeft": f"4px solid {color}",
                    "marginBottom": "10px",
                    "padding": "10px 14px",
                    "backgroundColor": "#FFFFFF",
                    "borderRadius": "8px",
                    "border": "1px solid #E2E8F0",
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.04)"
                },
                children=[
                    html.Div([
                        html.Span(
                            item["type_th"],
                            className="bin-type-badge",
                            style={
                                "backgroundColor": color, "color": "#FFF",
                                "padding": "3px 8px", "borderRadius": "4px",
                                "fontSize": "0.78rem", "fontWeight": "bold"
                            }
                        )
                    ]),
                    html.P([html.Strong("📍 ตำแหน่ง: "), html.Span(item["loc"])], style={"fontSize": "0.85rem", "margin": "6px 0 4px 0"}),
                    html.Div([
                        html.Strong("✅ ขยะที่ทิ้งได้: ", style={"color": "#166534", "fontSize": "0.82rem"}),
                        html.Span(item["items"], style={"fontSize": "0.82rem", "color": "#334155"})
                    ]),
                    html.Div([
                        html.Strong("❌ สิ่งที่ห้ามทิ้ง: ", style={"color": "#991B1B", "fontSize": "0.8rem"}),
                        html.Span(item["prohibited"], style={"fontSize": "0.8rem", "color": "#64748B"})
                    ], style={"marginTop": "3px"})
                ]
            )
            bin_cards.append(card)

        # แถบแสดงชั้น (Floor Accordion)
        floor_title = f"🏢 ชั้น {f}" if b["floors"] else "📍 บริเวณพื้นที่ให้บริการ"
        accordion_item = html.Details(
            open=True if idx == 0 else False,
            style={
                "marginBottom": "12px",
                "borderRadius": "8px",
                "backgroundColor": "#F8FAFC",
                "border": "1px solid #CBD5E1",
                "overflow": "hidden"
            },
            children=[
                html.Summary(
                    f"{floor_title} ({len(floor_bins)} จุด)",
                    style={
                        "padding": "10px 14px",
                        "fontWeight": "bold",
                        "cursor": "pointer",
                        "backgroundColor": "#F1F5F9",
                        "color": "#1E293B",
                        "fontSize": "0.9rem"
                    }
                ),
                html.Div(bin_cards, style={"padding": "12px 14px 4px 14px"})
            ]
        )
        floor_sections.append(accordion_item)

    # กรณีอาคารไม่มีข้อมูล (เช่น อาคาร 5 ที่ระบุ Not Available)
    if not b["bins"]:
        content_bins = [
            html.Div([
                html.Div("⚠️", style={"fontSize": "2rem", "marginBottom": "6px"}),
                html.Strong("Not Available", style={"fontSize": "1rem", "color": "#991B1B"}),
                html.P("ขณะนี้ยังไม่มีข้อมูลจุดทิ้งขยะในบริเวณนี้ หรือยังไม่เปิดให้บริการคัดแยกขยะ", style={"fontSize": "0.85rem", "color": "#64748B", "margin": "6px 0 0 0"})
            ], style={"padding": "24px", "background": "#FEF2F2", "borderRadius": "10px", "textAlign": "center", "border": "1px dashed #F87171"})
        ]
    elif not floor_sections:
        content_bins = [
            html.Div(
                "ไม่พบจุดทิ้งขยะที่ตรงกับเงื่อนไขการค้นหาในตำแหน่งนี้",
                style={"padding": "16px", "background": "#FEF2F2", "color": "#991B1B", "borderRadius": "8px", "fontSize": "0.86rem", "textAlign": "center"}
            )
        ]
    else:
        content_bins = floor_sections

    # ส่วนหัว Pop-up (นำโลโก้/ไอคอนประจำอาคารออกแล้ว)
    header_content = [
        html.Div(
            str(b["num"]),
            style={
                "width": "32px", "height": "32px", "borderRadius": "50%",
                "backgroundColor": "#D9A74A", "color": "#111",
                "display": "flex", "alignItems": "center", "justifyContent": "center",
                "fontWeight": "bold", "fontSize": "0.95rem"
            }
        ),
        html.Div([
            html.H3(b["name_th"], style={"margin": 0, "fontSize": "1.05rem", "color": "#0F172A", "fontWeight": "700"}),
            html.P(b["name_en"], style={"margin": 0, "fontSize": "0.8rem", "color": "#64748B"})
        ])
    ]

    body_content = [
        html.H4(
            f"🗑️ จุดคัดแยกขยะในตำแหน่งนี้ ({len(displayed_bins) if b['bins'] else 0} รายการ):",
            style={"margin": "0 0 12px 0", "fontSize": "0.92rem", "color": "#002D62"}
        ),
        html.Div(content_bins)
    ]

    return header_content, body_content

# =============================================================================
# 6. การรันระบบ
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print(f"🚀 Phayathai Campus Trash & Bin Finder Map ({len(WASTE_ITEMS_CATALOG)} Items Loaded)")
    print("🌐 เข้าใช้งานได้ที่: http://127.0.0.1:8050")
    print("=" * 70)
    app.run(debug=True, host="127.0.0.1", port=8050, use_reloader=False)

    