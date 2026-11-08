"""
เว็บแอปพลิเคชัน: Phayathai Campus Trash & Bin Finder Map 
คณะวิทยาศาสตร์ มหาวิทยาลัยมหิดล (พญาไท) 
พัฒนาด้วย: Python + Plotly Dash (Pure Python, No JavaScript) 
เวอร์ชัน: ปรับแต่งหมุดเฉพาะอาคารหลัก (1, 2, 7, 11, 13) และ Pop-up Modal
"""
import os
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State, ALL, ctx, no_update

# =============================================================================
# 1. ข้อมูลอาคารและจุดทิ้งขยะ
# =============================================================================
BUILDINGS_DATA = [
    {
        "num": 1, "id": "L", "name_en": "Lecture Building (L)", "name_th": "อาคารปาฐกถา / อาคารบรรยายรวม (ตึกกลม)",
        "x_pct": 56.43, "y_pct": 38.19, "icon": "🏛️",
        "zone": "โซนหน้าแคมปัส ติด GATE 2 และถนนพระราม 6 (RAMA VI Rd.)", "floors": [1, 2, 3],
        "description": "อาคารทรงกลมเอกลักษณ์ประจำคณะวิทยาศาสตร์ ม.มหิดล เป็นศูนย์กลางห้องบรรยายรวมขนาดใหญ่และกิจกรรมนักศึกษา",
        "gates": ["GATE 2"],
        "bins": [
            {"id": "BIN-L-101", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล", "loc": "โถงทางเข้าทิศเหนือ ใกล้ลิฟต์โดยสาร", "items": "ขวดน้ำพลาสติกใส (PET), กระป๋องอลูมิเนียม, กล่องนม, แก้วพลาสติกแข็ง", "prohibited": "หลอดดูดเปื้อน, เศษอาหาร, ถุงแกง", "status": "พร้อมใช้งาน"},
            {"id": "BIN-L-102", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป", "loc": "โถงทางเข้าทิศเหนือ ตั้งคู่กับถังรีไซเคิล", "items": "ซองขนม, กล่องข้าวโฟม, ซองกาแฟ, ทิชชู่ใช้แล้ว", "prohibited": "ขวดแก้ว, ขยะอิเล็กทรอนิกส์", "status": "พร้อมใช้งาน"},
            {"id": "BIN-L-103", "floor": 1, "type": "organic", "type_th": "ขยะอินทรีย์/เศษอาหาร", "loc": "บริเวณใต้ต้นไม้ ตรงข้ามร้านค้าข้างตึกกลม", "items": "เศษอาหาร, ข้าวเหลือ, เปลือกผลไม้, น้ำแกง", "prohibited": "ถุงแกง, บรรจุภัณฑ์ที่มีเศษอาหาร", "status": "พร้อมใช้งาน"},
            {"id": "BIN-L-104", "floor": 1, "type": "e-waste", "type_th": "ขยะอิเล็กทรอนิกส์", "loc": "จุดบริการวิชาการ มุมโถงประชาสัมพันธ์", "items": "ถ่านไฟฉาย, แบตเตอรี่มือถือ, พาวเวอร์แบงก์ชำรุด, สายเคเบิล, หูฟัง", "prohibited": "ขยะเปียก, หลอดไฟยาว", "status": "พร้อมใช้งาน"},
            {"id": "BIN-L-105", "floor": 1, "type": "hazardous", "type_th": "ขยะอันตราย", "loc": "หน้าทางเข้าห้องซ่อมบำรุงและห้องพักแม่บ้าน", "items": "หลอดฟลูออเรสเซนต์, กระป๋องสเปรย์, หน้ากากอนามัย, ขวดยาปนเปื้อน", "prohibited": "ขยะทั่วไป, เศษอาหาร", "status": "พร้อมใช้งาน"},
            {"id": "BIN-L-201", "floor": 2, "type": "recycle", "type_th": "ขยะรีไซเคิล", "loc": "หน้าห้องบรรยาย L-201 ทางเดินฝั่งตะวันออก", "items": "ขวดน้ำดื่ม, กระป๋องเครื่องดื่ม, ชีทเรียนและกระดาษ", "prohibited": "เศษอาหาร", "status": "พร้อมใช้งาน"},
            {"id": "BIN-L-202", "floor": 2, "type": "general", "type_th": "ขยะทั่วไป", "loc": "ระเบียงหน้าห้องบรรยาย L-201", "items": "ซองขนม, แก้วกระดาษ, ถุงพลาสติก", "prohibited": "ถ่านไฟฉาย", "status": "พร้อมใช้งาน"}
        ]
    },
    {
        "num": 2, "id": "C", "name_en": "Chemistry Building (C)", "name_th": "อาคารเคมี",
        "x_pct": 45.96, "y_pct": 24.79, "icon": "🧪",
        "zone": "โซนหน้าฝั่งซ้าย ถัดจากตึกกลม เชื่อมต่อตึกวิจัยและตึกคอมพิวเตอร์", "floors": [1, 2, 3, 4],
        "description": "ภาควิชาเคมี ศูนย์รวมห้องปฏิบัติการวิจัยเคมีอินทรีย์ เคมีอนินทรีย์ เคมีฟิสิกัล และเคมีวิเคราะห์",
        "gates": ["GATE 1", "GATE 2"],
        "bins": [
            {"id": "BIN-C-101", "floor": 1, "type": "hazardous", "type_th": "ขยะอันตราย/เคมี", "loc": "หน้าห้องปฏิบัติการเคมีพื้นฐาน Lab C-105", "items": "ขวดแก้วสารเคมีล้างสะอาดแล้ว, ถุงมือยางปนเปื้อน, กระดาษกรองเคมี", "prohibited": "สารเคมีไวไฟเข้มข้น", "status": "พร้อมใช้งาน"},
            {"id": "BIN-C-102", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล", "loc": "ทางเข้าตึกเคมี ฝั่งเชื่อมต่อตึกบรรยาย L", "items": "ขวดน้ำพลาสติก PET, ลังกระดาษบรรจุอุปกรณ์, กระป๋อง", "prohibited": "ขวดสารเคมี", "status": "พร้อมใช้งาน"},
            {"id": "BIN-C-103", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป", "loc": "โถงพักคอยนักศึกษา ชั้น 1", "items": "ซองขนม, ถุงพลาสติก, แก้วกาแฟ", "prohibited": "สารเคมีอันตราย", "status": "พร้อมใช้งาน"}
        ]
    },
    {
        "num": 3, "id": "COM", "name_en": "Computer Building", "name_th": "อาคารคอมพิวเตอร์",
        "x_pct": 56.24, "y_pct": 24.92, "icon": "💻",
        "zone": "โซนกลาง หลังตึกกลม (1) ระหว่างตึกเคมี (2) และตึกฟิสิกส์ (7)", "floors": [1, 2, 3],
        "description": "ศูนย์คอมพิวเตอร์และสารสนเทศ ห้องบริการคอมพิวเตอร์สำหรับนักศึกษา",
        "gates": ["GATE 2"],
        "bins": [
            {"id": "BIN-COM-101", "floor": 1, "type": "e-waste", "type_th": "ขยะอิเล็กทรอนิกส์", "loc": "โถงหน้าศูนย์บริการคอมพิวเตอร์", "items": "เมาส์, สาย LAN, ถ่านไฟฉาย", "prohibited": "ขยะเปียก", "status": "พร้อมใช้งาน"}
        ]
    },
    {
        "num": 4, "id": "B", "name_en": "Biology Building (B)", "name_th": "อาคารชีววิทยา",
        "x_pct": 60.57, "y_pct": 10.82, "icon": "🌿",
        "zone": "โซนหลังฝั่งขวา ถัดจากอาคารวิจัยและอาคารฟิสิกส์", "floors": [1, 2, 3, 4],
        "description": "ภาควิชาชีววิทยา",
        "gates": ["GATE 6"],
        "bins": [
            {"id": "BIN-B-101", "floor": 1, "type": "organic", "type_th": "ขยะอินทรีย์/เศษอาหาร", "loc": "ทางเดินติดสวนหย่อม", "items": "เศษพืช, ใบไม้", "prohibited": "ถุงพลาสติก", "status": "พร้อมใช้งาน"}
        ]
    },
    {
        "num": 5, "id": "N", "name_en": "New Biology Building (N)", "name_th": "อาคารชีววิทยาใหม่",
        "x_pct": 36.22, "y_pct": 14.17, "icon": "🔬",
        "zone": "โซนหลังฝั่งซ้าย ใกล้อาคารสตางค์ มงคลสุข", "floors": [1, 2, 3, 4, 5],
        "description": "อาคารเรียนและวิจัยขั้นสูงด้านชีววิทยา",
        "gates": ["GATE 1"],
        "bins": []
    },
    {
        "num": 6, "id": "R", "name_en": "Research Building (R)", "name_th": "อาคารวิจัย",
        "x_pct": 49.88, "y_pct": 14.48, "icon": "🧬",
        "zone": "ใจกลางแคมปัส อาคารแนวยาว", "floors": [1, 2, 3, 4, 5, 6],
        "description": "ศูนย์กลางห้องปฏิบัติการวิจัยเครื่องมือรวม",
        "gates": ["GATE 2"],
        "bins": []
    },
    {
        "num": 7, "id": "P", "name_en": "Physics Building (P)", "name_th": "อาคารฟิสิกส์",
        "x_pct": 64.66, "y_pct": 20.51, "icon": "⚛️",
        "zone": " ", "floors": [4, 5, 6, 7],
        "description": "ภาควิชาฟิสิกส์ ห้องปฏิบัติการฟิสิกส์เชิงคำนวณ เลเซอร์ และวัสดุศาสตร์นาโน",
        "gates": ["GATE 2", "GATE 3"],
        "bins": [
            {"id": "BIN-P-101", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล", "loc": "โถงหน้าห้องปฏิบัติการฟิสิกส์พื้นฐาน", "items": "ขวดน้ำพลาสติก, กระป๋อง, กระดาษคำนวณ", "prohibited": "ขยะเปียก", "status": "พร้อมใช้งาน"},
            {"id": "BIN-P-102", "floor": 1, "type": "e-waste", "type_th": "ขยะอิเล็กทรอนิกส์", "loc": "หน้าห้องปฏิบัติการอิเล็กทรอนิกส์และวงจร", "items": "แผงวงจรทดลองเสีย, ตัวต้านทาน, ถ่านไฟฉาย, อะแดปเตอร์เก่า", "prohibited": "ขยะอาหาร", "status": "พร้อมใช้งาน"},
            {"id": "BIN-P-103", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป", "loc": "ทางเดินฝั่งทิศใต้ ชั้น 1", "items": "ขยะทั่วไป, ซองบะหมี่, ทิชชู่", "prohibited": "สายไฟ, อุปกรณ์อิเล็กทรอนิกส์", "status": "พร้อมใช้งาน"}
        ]
    },
    {
        "num": 8, "id": "PR", "name_en": "Preclinic Building (Pr)", "name_th": "อาคารปรีคลินิก",
        "x_pct": 74.56, "y_pct": 10.80, "icon": "🩺",
        "zone": "โซนหลังฝั่งขวา", "floors": [1, 2, 3, 4, 5],
        "description": "ห้องปฏิบัติการทางวิทยาศาสตร์การแพทย์",
        "gates": ["GATE 4"],
        "bins": []
    },
    {
        "num": 9, "id": "AN1", "name_en": "Anatomy Building 1 (AN1)", "name_th": "อาคารกายวิภาค 1",
        "x_pct": 68.21, "y_pct": 6.87, "icon": "🩻",
        "zone": "โซนหลังสุด", "floors": [1, 2, 3],
        "description": "ภาควิชากายวิภาคศาสตร์ 1",
        "gates": ["GATE 5"],
        "bins": []
    },
    {
        "num": 10, "id": "AN2", "name_en": "Anatomy Building 2 (AN2)", "name_th": "อาคารกายวิภาค 2",
        "x_pct": 71.43, "y_pct": 2.33, "icon": "🦴",
        "zone": "แนวรั้วหลังสุดของแคมปัส", "floors": [1, 2, 3, 4],
        "description": "ภาควิชากายวิภาคศาสตร์ 2",
        "gates": ["GATE 5"],
        "bins": []
    },
    {
        "num": 11, "id": "M", "name_en": "Multidisciplinary Building (M)", "name_th": "อาคารอเนกประสงค์ / สหวิทยาการ",
        "x_pct": 52.02, "y_pct": 8.77, "icon": "🏢",
        "zone": "โซนหลังตรงกลาง ใกล้หอถังเก็บน้ำและ GATE 6", "floors": [1, 2, 3, 4],
        "description": "ศูนย์ประชุมสัมมนา ลานกิจกรรมอเนกประสงค์ และสำนักงานหลักสูตรสหวิทยาการ",
        "gates": ["GATE 6"],
        "bins": [
            {"id": "BIN-M-101", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล", "loc": "โถงลานกิจกรรมอเนกประสงค์", "items": "ขวดน้ำดื่ม, กล่องกระดาษสัมมนา, กระป๋อง", "prohibited": "เศษอาหาร", "status": "พร้อมใช้งาน"},
            {"id": "BIN-M-102", "floor": 1, "type": "organic", "type_th": "ขยะอินทรีย์/เศษอาหาร", "loc": "จุดบริการอาหารว่างและจัดเลี้ยง", "items": "เศษอาหารจัดเลี้ยง, กากกาแฟ, เปลือกผลไม้", "prohibited": "กล่องโฟม, ช้อนส้อมพลาสติก", "status": "พร้อมใช้งาน"},
            {"id": "BIN-M-103", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป", "loc": "ทางเข้าห้องประชุมใหญ่", "items": "กล่องข้าว, ทิชชู่, ถุงพลาสติก", "prohibited": "ขวดแก้ว", "status": "พร้อมใช้งาน"}
        ]
    },
    {
        "num": 12, "id": "BT", "name_en": "Biotechnology Building (BT)", "name_th": "อาคารเทคโนโลยีชีวภาพ",
        "x_pct": 39.72, "y_pct": 7.36, "icon": "🧫",
        "zone": "โซนหลังซ้าย", "floors": [1, 2, 3, 4, 5],
        "description": "ภาควิชาเทคโนโลยีชีวภาพ",
        "gates": ["GATE 6"],
        "bins": []
    },
    {
        "num": 13, "id": "K", "name_en": "Chalermphrakiet Building (K)", "name_th": "อาคารเฉลิมพระเกียรติ",
        "x_pct": 74.37, "y_pct": 32.82, "icon": "🎖️",
        "zone": "โซนหน้าฝั่งขวา ติดถนนพระราม 6, GATE 3 และ GATE 4", "floors": [1, 2, 3, 4, 5, 6, 7],
        "description": "อาคารสูงทันสมัย ศูนย์รวมห้องวิจัยขั้นสูง ห้องประชุมนานาชาติ และสำนักงานคณบดี คณะวิทยาศาสตร์",
        "gates": ["GATE 3", "GATE 4"],
        "bins": [
            {"id": "BIN-K-101", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล", "loc": "โถงลิฟต์หลักชั้น 1 ทางเข้าอาคาร", "items": "ขวดพลาสติก PET, กระป๋องเครื่องดื่ม, ซองเอกสาร", "prohibited": "เศษอาหาร, ของเหลว", "status": "พร้อมใช้งาน"},
            {"id": "BIN-K-102", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป", "loc": "โถงลิฟต์หลักชั้น 1 คู่กับถังรีไซเคิล", "items": "ซองขนม, กล่องโฟม, ถุงพลาสติก, ทิชชู่", "prohibited": "สารเคมี, ขยะมีพิษ", "status": "พร้อมใช้งาน"},
            {"id": "BIN-K-103", "floor": 1, "type": "hazardous", "type_th": "ขยะอันตราย", "loc": "ทางเดินฝั่งห้องวิจัยขั้นสูง เชื่อมออกลานจอดรถ", "items": "หน้ากากอนามัย, ถุงมือการแพทย์, หลอดไฟ, สเปรย์", "prohibited": "ขยะทั่วไป", "status": "พร้อมใช้งาน"},
            {"id": "BIN-K-104", "floor": 1, "type": "e-waste", "type_th": "ขยะอิเล็กทรอนิกส์", "loc": "จุดคัดแยกขยะอิเล็กทรอนิกส์ สำนักงานคณบดี", "items": "ถ่านไฟฉาย, แบตเตอรี่, สายชาร์จ, แฟลชไดรฟ์เสีย", "prohibited": "ขยะทั่วไป", "status": "พร้อมใช้งาน"}
        ]
    },
    {
        "num": 14, "id": "AF", "name_en": "Laboratory Animal Facility Building (AF)", "name_th": "อาคารสัตว์ทดลอง",
        "x_pct": 32.67, "y_pct": 6.40, "icon": "🐁",
        "zone": "มุมซ้ายบนสุดของแคมปัส", "floors": [1, 2, 3],
        "description": "ศูนย์สัตว์ทดลอง",
        "gates": ["GATE 1"],
        "bins": []
    },
    {
        "num": 15, "id": "ST", "name_en": "Stang Mongkolsuk Building (ST)", "name_th": "อาคารสตางค์ มงคลสุข",
        "x_pct": 29.73, "y_pct": 16.38, "icon": "📚",
        "zone": "โซนซ้าย", "floors": [1, 2, 3],
        "description": "ห้องสมุดสตางค์ มงคลสุข",
        "gates": ["GATE 1"],
        "bins": []
    },
    {
        "num": 16, "id": "V", "name_en": "Venture Club@MUSC Building (V)", "name_th": "อาคารเวนเจอร์คลับ (Venture Club@MUSC)",
        "x_pct": 67.99, "y_pct": 25.93, "icon": "🚀",
        "zone": "ระหว่างอาคารฟิสิกส์และอาคารเฉลิมพระเกียรติ", "floors": [1, 2],
        "description": "ศูนย์บ่มเพาะธุรกิจสตาร์ทอัพ",
        "gates": ["GATE 2"],
        "bins": []
    },
    {
        "num": 17, "id": "NDCC", "name_en": "National Doping Control Centre (NDCC)", "name_th": "ศูนย์ตรวจสารต้องห้ามในนักกีฬา",
        "x_pct": 30.78, "y_pct": 11.34, "icon": "🏅",
        "zone": "โซนซ้ายบน", "floors": [1, 2, 3, 4],
        "description": "ศูนย์ตรวจสารต้องห้าม",
        "gates": ["GATE 1"],
        "bins": []
    }
]

BIN_TYPE_COLORS = {
    "recycle": "#E67E22",
    "general": "#2980B9",
    "organic": "#27AE60",
    "hazardous": "#C0392B",
    "e-waste": "#8E44AD"
}

BUILDING_BY_NUM = {b["num"]: b for b in BUILDINGS_DATA}

# กำหนดเฉพาะ 5 อาคารหลักที่ต้องการให้มีหมุดปุ่มกดบนแผนที่
ACTIVE_BUILDING_NUMS = [1, 2, 7, 11, 13]
ACTIVE_BUILDINGS = [b for b in BUILDINGS_DATA if b["num"] in ACTIVE_BUILDING_NUMS]

# =============================================================================
# 2. การสร้าง Layout Dash App
# =============================================================================
app = Dash(
    __name__,
    title="Phayathai Campus Trash & Bin Finder Map | คณะวิทยาศาสตร์ ม.มหิดล",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)
server = app.server

def generate_building_pins():
    pins = []
    for b in ACTIVE_BUILDINGS:
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
                # ช่องค้นหาและตัวกรองประเภทขยะ
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
                                    placeholder="🔍 พิมพ์ค้นหาขยะ เช่น ขวดน้ำ, ถ่านไฟฉาย, สารเคมี, อาหาร...",
                                    style={"width": "100%", "padding": "10px 14px", "borderRadius": "8px", "border": "1.5px solid #CBD5E1", "fontSize": "0.95rem"},
                                    debounce=True
                                )
                            ]
                        ),
                        html.Div(
                            className="waste-filter-pills",
                            children=[
                                html.Button("ทั้งหมด (All)", id={"type": "filter-btn", "index": "all"}, className="filter-pill-btn active", n_clicks=0),
                                html.Button("🟡 รีไซเคิล", id={"type": "filter-btn", "index": "recycle"}, className="filter-pill-btn", n_clicks=0),
                                html.Button("🔵 ทั่วไป", id={"type": "filter-btn", "index": "general"}, className="filter-pill-btn", n_clicks=0),
                                html.Button("🟢 เศษอาหาร", id={"type": "filter-btn", "index": "organic"}, className="filter-pill-btn", n_clicks=0),
                                html.Button("🔴 อันตราย/เคมี", id={"type": "filter-btn", "index": "hazardous"}, className="filter-pill-btn", n_clicks=0),
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
                                html.H2(["🗺️ แผนผังคณะวิทยาศาสตร์ พญาไท (Phayathai Campus Map)"]),
                                html.Span("👉 คลิกที่หมุดหมายเลข 1, 2, 7, 11 หรือ 13 เพื่อดูข้อมูลจุดทิ้งขยะ", className="map-hint-text")
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
                                # แสดงเฉพาะหมุดหมายเลข 1, 2, 7, 11, 13 (ไม่มี icon รบกวนด้านล่าง)
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

        # Pop-up Modal สำหรับแสดงรายละเอียดเมื่อคลิกอาคาร
        html.Div(
            id="building-modal-container",
            style={"display": "none"},
            children=[
                # พื้นหลังมืด
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
                        "maxWidth": "640px",
                        "maxHeight": "88vh",
                        "zIndex": 9999,
                        "display": "flex",
                        "flexDirection": "column",
                        "overflow": "hidden"
                    },
                    children=[
                        # ส่วนหัว Modal พร้อมปุ่มปิดกากบาท (✕)
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
                        # เนื้อหาจุดทิ้งขยะ
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
# 3. Callbacks
# =============================================================================

# ควบคุมการเลือกอาคารและการเปิด/ปิด Pop-up Modal
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

    # กดปุ่มปิด หรือกดที่พื้นหลังสีดำ -> ปิด Pop-up
    if trig_id == "close-modal-btn" or trig_id == "modal-backdrop":
        return current_bldg, False

    # กดที่หมุดบนแผนที่ -> เปิด Pop-up ของอาคารนั้น
    if isinstance(trig_id, dict):
        clicked_num = trig_id.get("index")
        if clicked_num:
            return clicked_num, True

    return current_bldg, is_open

# ควบคุมการแสดงผล/ซ่อน Pop-up Modal
@app.callback(
    Output("building-modal-container", "style"),
    Input("modal-open-store", "data")
)
def toggle_modal_visibility(is_open):
    if is_open:
        return {"display": "block"}
    return {"display": "none"}

# จัดการปุ่มฟิลเตอร์ประเภทขยะ
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

# อัปเดตสไตล์ของหมุด (เฉพาะ 5 อาคารที่แสดง)
@app.callback(
    Output({"type": "building-pin", "index": ALL}, "className"),
    Input("selected-building-store", "data"),
    Input("filter-type-store", "data"),
    Input("campus-search-input", "value")
)
def update_pin_styles(selected_num, filter_type, search_query):
    search_q = (search_query or "").strip().lower()
    classes = []
    for b in ACTIVE_BUILDINGS:
        b_num = b["num"]
        is_active = (b_num == selected_num)
        
        has_filtered_type = True
        if filter_type and filter_type != "all":
            has_filtered_type = any(bin_item["type"] == filter_type for bin_item in b["bins"])
            
        matches_search = True
        if search_q:
            matches_search = False
            for bin_item in b["bins"]:
                if (search_q in bin_item["items"].lower() or 
                    search_q in bin_item["type_th"].lower() or 
                    search_q in bin_item["loc"].lower() or 
                    search_q in b["name_th"].lower() or
                    search_q in b["name_en"].lower()):
                    matches_search = True
                    break

        cls = "building-pin-btn"
        if is_active:
            cls += " is-active"
        elif matches_search and has_filtered_type and (filter_type != "all" or search_q):
            cls += " is-highlighted"
        elif not matches_search or not has_filtered_type:
            cls += " is-dimmed"

        classes.append(cls)
    return classes

# อัปเดตเนื้อหาใน Pop-up Modal เมื่อเลือกอาคาร
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
    
    displayed_bins = []
    for bin_item in b["bins"]:
        if filter_type != "all" and bin_item["type"] != filter_type:
            continue
        if search_q:
            if not (search_q in bin_item["items"].lower() or 
                    search_q in bin_item["type_th"].lower() or 
                    search_q in bin_item["loc"].lower()):
                continue
        displayed_bins.append(bin_item)

    bin_cards = []
    for item in displayed_bins:
        color = BIN_TYPE_COLORS.get(item["type"], "#64748B")
        card = html.Div(
            className="bin-item-card",
            style={"borderLeft": f"4px solid {color}", "marginBottom": "10px"},
            children=[
                html.Div([
                    html.Span(
                        item["type_th"],
                        className="bin-type-badge",
                        style={"backgroundColor": color}
                    ),
                    html.Span(f" (ชั้น {item['floor']})", style={"fontSize": "0.82rem", "color": "#475569", "fontWeight": "bold", "marginLeft": "6px"}),
                    html.Span(f"• {item['id']}", style={"fontSize": "0.76rem", "color": "#94A3B8", "float": "right"})
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

    if not bin_cards:
        bin_cards = [
            html.Div(
                "ไม่พบจุดทิ้งขยะที่ตรงกับเงื่อนไขการค้นหาในอาคารนี้",
                style={"padding": "16px", "background": "#FEF2F2", "color": "#991B1B", "borderRadius": "8px", "fontSize": "0.86rem", "textAlign": "center"}
            )
        ]

    # ส่วนหัว Pop-up
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
        html.Span(b["icon"], style={"fontSize": "1.4rem"}),
        html.Div([
            html.H3(b["name_th"], style={"margin": 0, "fontSize": "1.05rem", "color": "#0F172A", "fontWeight": "700"}),
            html.P(b["name_en"], style={"margin": 0, "fontSize": "0.8rem", "color": "#64748B"})
        ])
    ]

    # เนื้อหาใน Pop-up
    body_content = [
        html.Div(
            style={"background": "#F8FAFC", "padding": "12px 14px", "borderRadius": "10px", "marginBottom": "16px", "border": "1px solid #E2E8F0"},
            children=[
                html.P([html.Strong("📍 โซนที่ตั้ง: "), html.Span(b["zone"])], style={"margin": "0 0 4px 0", "fontSize": "0.86rem"}),
                html.P([html.Strong("🚪 ประตูทางเข้าใกล้เคียง: "), html.Span(", ".join(b["gates"]))], style={"margin": "0 0 4px 0", "color": "#1D4ED8", "fontSize": "0.86rem"}),
                html.P(b["description"], style={"margin": "6px 0 0 0", "fontSize": "0.82rem", "color": "#475569", "fontStyle": "italic"})
            ]
        ),
        html.H4(f"🗑️ จุดทิ้งขยะในอาคารนี้ ({len(displayed_bins)} จุด):", style={"margin": "0 0 10px 0", "fontSize": "0.92rem", "color": "#002D62"}),
        html.Div(bin_cards)
    ]

    return header_content, body_content

# =============================================================================
# 4. การรันระบบ
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Phayathai Campus Trash & Bin Finder Map")
    print("🌐 เข้าใช้งานได้ที่: http://127.0.0.1:8050")
    print("=" * 70)
    app.run(debug=True, host="127.0.0.1", port=8050, use_reloader=False)

