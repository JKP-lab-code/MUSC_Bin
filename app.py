"""
เว็บแอปพลิเคชัน: Phayathai Campus Trash & Bin Finder Map 
คณะวิทยาศาสตร์ มหาวิทยาลัยมหิดล (พญาไท) 
พัฒนาด้วย: Python + Plotly Dash (Pure Python, No JavaScript) 
เวอร์ชัน: อัปเดตฐานข้อมูลถังขยะตามเอกสารจริง + เพิ่มหมุดอาคาร 5, 15, 17
"""
import os
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State, ALL, ctx, no_update

# =============================================================================
# 1. ข้อมูลแนะนำประเภทขยะเบื้องต้น (Waste Information Data)
# =============================================================================
WASTE_TYPE_INFO = {
    "recycle": {
        "title": "🟡 ขยะรีไซเคิล (Recycle Waste)",
        "color": "#D97706",
        "bg_color": "#FFFBEB",
        "border_color": "#FDE68A",
        "characteristic": "บรรจุภัณฑ์หรือวัสดุเหลือใช้ที่สะอาด แห้ง ไม่เปื้อนเศษอาหาร สามารถนำกลับเข้ากระบวนการแปรรูปเป็นวัตถุดิบใหม่ได้",
        "decomposition": "❌ ย่อยสลายยากมาก หรือไม่ย่อยสลาย (พลาสติก PET ใช้เวลา 450 ปี, กระป๋องอลูมิเนียม 200–500 ปี)",
        "acceptable_items": "ขวดน้ำพลาสติกใส, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด, กล่องกระดาษ",
        "handling_tip": "เทของเหลวทิ้งให้หมด บ้วนน้ำล้างคราบสกปรก และบีบให้แบนเพื่อประหยัดพื้นที่ก่อนทิ้ง"
    },
    "general": {
        "title": "🔵 ขยะทั่วไป (ขยะฝังกลบ) (General / Landfill Waste)",
        "color": "#2563EB",
        "bg_color": "#EFF6FF",
        "border_color": "#BFDBFE",
        "characteristic": "ขยะที่ย่อยสลายยาก มีการปนเปื้อน หรือไม่คุ้มค่าทางเศรษฐกิจในการนำกลับไปรีไซเคิล ต้องนำไปเข้าสู่กระบวนการฝังกลบหรือกำจัดตามระบบ",
        "decomposition": "❌ ย่อยสลายยากมาก (ส่วนใหญ่ใช้เวลา 50–500 ปี หรือแตกตัวเป็นไมโครพลาสติกตกค้าง)",
        "acceptable_items": "ซองขนม, ซองกาแฟ, ทิชชู่ใช้แล้ว, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร, ถุงพลาสติกเปื้อนแกง",
        "handling_tip": "มัดปากถุงให้มิดชิด อย่าทิ้งปนกับขยะรีไซเคิลสะอาด และห้ามนำขยะอันตรายหรือสารเคมีมาทิ้งรวม"
    },
    "organic": {
        "title": "🟢 ขยะอินทรีย์ / เศษอาหาร (Organic Waste)",
        "color": "#16A34A",
        "bg_color": "#F0FDF4",
        "border_color": "#BBF7D0",
        "characteristic": "สารอินทรีย์ที่เน่าเสียและย่อยสลายได้ มีความชื้นสูง ส่งกลิ่นได้ง่าย นำไปหมักทำปุ๋ยชีวภาพหรือผลิตก๊าซชีวภาพได้",
        "decomposition": "✅ ย่อยสลายได้ง่ายและรวดเร็วตามธรรมชาติ (ใช้เวลาประมาณ 1 สัปดาห์ ถึง 2 เดือน)",
        "acceptable_items": "เศษอาหาร, ข้าวเหลือ, เศษผัก, เปลือกผลไม้, น้ำแกง",
        "handling_tip": "แยกน้ำแกงออกให้เหลือน้อยที่สุด ห้ามทิ้งถุงพลาสติก ช้อนส้อมพลาสติก หรือไม้เสียบลูกชิ้นปนลงไป"
    },
    "hazardous": {
        "title": "🔴 ขยะอันตราย / สารเคมี (Hazardous / Chemical Waste)",
        "color": "#DC2626",
        "bg_color": "#FEF2F2",
        "border_color": "#FECACA",
        "characteristic": "วัสดุปนเปื้อนสารเคมี วัตถุไวไฟ สารกัดกร่อน หรือแบตเตอรี่ หากทิ้งปะปนจะแพร่กระจายสารพิษสู่สิ่งแวดล้อม",
        "decomposition": "❌ ไม่ย่อยสลายตามธรรมชาติ และสร้างมลพิษตกค้างยาวนานในดินและน้ำ",
        "acceptable_items": "แบตเตอรี่, ถ่านไฟฉาย, หลอดไส้, หลอดฟลูออเรสเซนต์, กระป๋องสเปรย์, ภาชนะบรรจุสารเคมี",
        "handling_tip": "บรรจุในถุงหรือภาชนะที่ปิดมิดชิด ป้องกันการรั่วซึมหรือแตกหักก่อนนำมาทิ้ง"
    },
    "e-waste": {
        "title": "🟣 ขยะอิเล็กทรอนิกส์ (E-Waste)",
        "color": "#7C3AED",
        "bg_color": "#FAF5FF",
        "border_color": "#E9D5FF",
        "characteristic": "อุปกรณ์เครื่องใช้ไฟฟ้าและชิ้นส่วนวงจรอิเล็กทรอนิกส์ที่ชำรุด มีส่วนประกอบของโลหะมีค่าแต่มีโลหะหนักเป็นพิษ",
        "decomposition": "❌ ไม่สามารถย่อยสลายได้ตามธรรมชาติ ต้องเข้าโรงงานสกัดแยกโลหะหนักอย่างถูกวิธี",
        "acceptable_items": "แบตเตอรี่, ถ่านไฟฉาย, แผงวงจร, สายชาร์จ, แฟลชไดรฟ์, หูฟัง, โทรศัพท์เก่า",
        "handling_tip": "ห้ามทุบ ดัด หรือแกะแบตเตอรี่เพราะอาจเกิดประกายไฟหรือสารเคมีรั่วไหลได้"
    }
}

# =============================================================================
# 2. ข้อมูลอาคารและจุดทิ้งขยะ (อ้างอิงจาก Data_bin_location.docx)
# =============================================================================
BUILDINGS_DATA = [
    {
        "num": 1, "id": "L", "name_en": "Lecture Building (L)", "name_th": "อาคารปาฐกถา / อาคารบรรยายรวม (ตึกกลม)",
        "x_pct": 56.43, "y_pct": 38.19, "icon": "🏛️",
        "zone": "โซนหน้าแคมปัส ติด GATE 2 และถนนพระราม 6 (RAMA VI Rd.)", "floors": [1],
        "description": "อาคารทรงกลมเอกลักษณ์ประจำคณะวิทยาศาสตร์ ม.มหิดล เป็นศูนย์กลางห้องบรรยายรวมและกิจกรรมนักศึกษา",
        "gates": ["GATE 2"],
        "bins": [
            {
                "id": "BIN-1-101", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป (ขยะฝังกลบ)",
                "loc": "โถงทางเข้าชั้น 1 ใกล้ลิฟต์และบันได",
                "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขวดแก้ว, ขยะอันตราย, ขยะอิเล็กทรอนิกส์", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-1-102", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "โถงทางเข้าชั้น 1 ตั้งคู่กับถังขยะทั่วไป",
                "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "บรรจุภัณฑ์เปื้อนเศษอาหาร, ถุงแกง", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-1-103", "floor": 1, "type": "organic", "type_th": "ขยะอินทรีย์/เศษอาหาร",
                "loc": "บริเวณโถงใกล้มุมร้านค้า/อาหารว่าง ชั้น 1",
                "items": "เศษอาหาร, เปลือกผลไม้, น้ำแกง",
                "prohibited": "ถุงแกง, บรรจุภัณฑ์ที่มีเศษอาหาร, พลาสติก", "status": "พร้อมใช้งาน"
            }
        ]
    },
    {
        "num": 2, "id": "C", "name_en": "Chemistry Building (C)", "name_th": "อาคารเคมี",
        "x_pct": 45.96, "y_pct": 24.79, "icon": "🧪",
        "zone": "โซนหน้าฝั่งซ้าย ถัดจากตึกกลม เชื่อมต่อตึกวิจัยและตึกคอมพิวเตอร์", "floors": [1],
        "description": "ภาควิชาเคมี ศูนย์รวมห้องปฏิบัติการวิจัยเคมีและห้องเรียนปฏิบัติการ",
        "gates": ["GATE 1", "GATE 2"],
        "bins": [
            {
                "id": "BIN-2-101", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป (ขยะฝังกลบ)",
                "loc": "โถงทางเดินกลาง ชั้น 1",
                "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "สารเคมี, ขยะมีพิษ, ขวดแก้ว", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-2-102", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "โถงทางเดินกลาง ชั้น 1 เชื่อมทางออกอาคาร",
                "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "บรรจุภัณฑ์เปื้อนเศษอาหาร, ถุงแกง", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-2-103", "floor": 1, "type": "hazardous", "type_th": "ขยะอันตราย",
                "loc": "จุดคัดแยกวัสดุอันตราย ชั้น 1 หน้าห้องปฏิบัติการ",
                "items": "แบตเตอรี่, ถ่านไฟฉาย, หลอดไส้, หลอดไฟ",
                "prohibited": "ขยะทั่วไป, เศษอาหาร", "status": "พร้อมใช้งาน"
            }
        ]
    },
    {
        "num": 5, "id": "N", "name_en": "New Biology Building (N)", "name_th": "อาคารชีววิทยาใหม่",
        "x_pct": 36.22, "y_pct": 14.17, "icon": "🔬",
        "zone": "โซนหลังฝั่งซ้าย ใกล้อาคารสตางค์ มงคลสุข และอาคารวิจัย", "floors": [2, 3],
        "description": "อาคารเรียนและวิจัยขั้นสูงด้านชีววิทยาและเทคโนโลยีชีวภาพโมเลกุล",
        "gates": ["GATE 1", "GATE 6"],
        "bins": [
            {
                "id": "BIN-5-201", "floor": 2, "type": "general", "type_th": "ขยะทั่วไป (ขยะฝังกลบ)",
                "loc": "โถงทางเดินหน้าห้องปฏิบัติการ ชั้น 2",
                "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "สารเคมี, สารติดเชื้อ, ขวดแก้ว", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-5-202", "floor": 2, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "โถงบันได ชั้น 2",
                "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "บรรจุภัณฑ์เปื้อนเศษอาหาร, ถุงแกง", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-5-301", "floor": 3, "type": "general", "type_th": "ขยะทั่วไป (ขยะฝังกลบ)",
                "loc": "โถงทางเดิน ชั้น 3",
                "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "สารเคมี, สารติดเชื้อ", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-5-302", "floor": 3, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "โถงบันได ชั้น 3",
                "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "บรรจุภัณฑ์เปื้อนเศษอาหาร, ถุงแกง", "status": "พร้อมใช้งาน"
            }
        ]
    },
    {
        "num": 7, "id": "P", "name_en": "Physics Building (P)", "name_th": "อาคารฟิสิกส์",
        "x_pct": 64.66, "y_pct": 20.51, "icon": "⚛️",
        "zone": "โซนกลางฝั่งขวา เชื่อมต่ออาคารวิจัยและอาคารปรีคลินิก", "floors": [1, 4, 5, 6],
        "description": "ภาควิชาฟิสิกส์ ห้องปฏิบัติการฟิสิกส์เชิงคำนวณ เลเซอร์ และวัสดุศาสตร์นาโน",
        "gates": ["GATE 2", "GATE 3"],
        "bins": [
            # ชั้น 1
            {
                "id": "BIN-7-101", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป (ขยะฝังกลบ)",
                "loc": "โถงทางเดินชั้น 1 ทางเข้าอาคาร",
                "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "สายไฟ, อุปกรณ์อิเล็กทรอนิกส์", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-7-102", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "โถงบันไดกลาง ชั้น 1",
                "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "เศษอาหาร, บรรจุภัณฑ์เปื้อน", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-7-103", "floor": 1, "type": "e-waste", "type_th": "ขยะอิเล็กทรอนิกส์",
                "loc": "หน้าห้องปฏิบัติการอิเล็กทรอนิกส์ ชั้น 1",
                "items": "แบตเตอรี่, ถ่านไฟฉาย, แผงวงจร",
                "prohibited": "ขยะทั่วไป, ขยะเปียก", "status": "พร้อมใช้งาน"
            },
            # ชั้น 4
            {
                "id": "BIN-7-401", "floor": 4, "type": "general", "type_th": "ขยะทั่วไป (ขยะฝังกลบ)",
                "loc": "โถงทางเดิน ชั้น 4",
                "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขวดแก้ว, ขยะอิเล็กทรอนิกส์", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-7-402", "floor": 4, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "หน้าห้องพักอาจารย์/ห้องเรียน ชั้น 4",
                "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "บรรจุภัณฑ์เปื้อนเศษอาหาร, ถุงแกง", "status": "พร้อมใช้งาน"
            },
            # ชั้น 5
            {
                "id": "BIN-7-501", "floor": 5, "type": "general", "type_th": "ขยะทั่วไป (ขยะฝังกลบ)",
                "loc": "โถงกลาง ชั้น 5",
                "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขยะรีไซเคิล", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-7-502", "floor": 5, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "จุดคัดแยกขยะ ชั้น 5",
                "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "เศษอาหาร", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-7-503", "floor": 5, "type": "recycle", "type_th": "ขยะรีไซเคิล (ตะกร้าแยกเฉพาะ)",
                "loc": "จุดแยกพิเศษ ชั้น 5",
                "items": "ตะกร้าสำหรับแยกบรรจุภัณฑ์, ตะกร้าสำหรับแยกตะเกียบและไม้เสียบลูกชิ้น, ตะกร้าสำหรับแยกหลอดพลาสติก",
                "prohibited": "ขยะเปียก, น้ำแกง", "status": "พร้อมใช้งาน"
            },
            # ชั้น 6
            {
                "id": "BIN-7-601", "floor": 6, "type": "general", "type_th": "ขยะทั่วไป (ขยะฝังกลบ)",
                "loc": "โถงทางเดิน ชั้น 6",
                "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขวดแก้ว", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-7-602", "floor": 6, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "โถงบันได ชั้น 6",
                "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "บรรจุภัณฑ์เปื้อนเศษอาหาร", "status": "พร้อมใช้งาน"
            }
        ]
    },
    {
        "num": 11, "id": "M", "name_en": "Multidisciplinary Building (M)", "name_th": "อาคารอเนกประสงค์ / สหวิทยาการ",
        "x_pct": 52.02, "y_pct": 8.77, "icon": "🏢",
        "zone": "โซนหลังตรงกลาง ใกล้หอถังเก็บน้ำและ GATE 6", "floors": [1, 2, 3],
        "description": "ศูนย์ประชุมสัมมนา ลานกิจกรรมอเนกประสงค์ และสำนักงานหลักสูตรสหวิทยาการ",
        "gates": ["GATE 6"],
        "bins": [
            # ชั้น 1
            {
                "id": "BIN-11-101", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป (ขยะฝังกลบ)",
                "loc": "โถงลานกิจกรรมอเนกประสงค์ ชั้น 1",
                "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขวดแก้ว, ของมีคม", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-11-102", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "ทางเข้าโถงประชุมใหญ่ ชั้น 1",
                "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "บรรจุภัณฑ์เปื้อนเศษอาหาร, ถุงแกง", "status": "พร้อมใช้งาน"
            },
            # ชั้น 2
            {
                "id": "BIN-11-201", "floor": 2, "type": "general", "type_th": "ขยะทั่วไป (ขยะฝังกลบ)",
                "loc": "โถงทางเดิน ชั้น 2",
                "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "สารเคมี, ขยะมีพิษ", "status": "พร้อมใช้งาน"
            },
            # ชั้น 3
            {
                "id": "BIN-11-301", "floor": 3, "type": "general", "type_th": "ขยะทั่วไป (ขยะฝังกลบ)",
                "loc": "โถงทางเดิน ชั้น 3",
                "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "สารเคมี", "status": "พร้อมใช้งาน"
            }
        ]
    },
    {
        "num": 13, "id": "K", "name_en": "Chalermphrakiet Building (K)", "name_th": "อาคารเฉลิมพระเกียรติ",
        "x_pct": 74.37, "y_pct": 32.82, "icon": "🎖️",
        "zone": "โซนหน้าฝั่งขวา ติดถนนพระราม 6, GATE 3 และ GATE 4", "floors": [1],
        "description": "อาคารสูงทันสมัย ศูนย์รวมห้องวิจัยขั้นสูง ห้องประชุมนานาชาติ และสำนักงานคณบดี คณะวิทยาศาสตร์",
        "gates": ["GATE 3", "GATE 4"],
        "bins": [
            {
                "id": "BIN-13-101", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "โถงลิฟต์หลักชั้น 1 ทางเข้าอาคาร",
                "items": "ขวดพลาสติก PET, กระป๋องเครื่องดื่ม, ซองเอกสาร",
                "prohibited": "เศษอาหาร, ของเหลว", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-13-102", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป (ขยะฝังกลบ)",
                "loc": "โถงลิฟต์หลักชั้น 1 คู่กับถังรีไซเคิล",
                "items": "ซองขนม, กล่องโฟม, ถุงพลาสติก, ทิชชู่",
                "prohibited": "สารเคมี, ขยะมีพิษ", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-13-103", "floor": 1, "type": "hazardous", "type_th": "ขยะอันตราย",
                "loc": "ทางเดินฝั่งห้องวิจัยขั้นสูง เชื่อมออกลานจอดรถ",
                "items": "หน้ากากอนามัย, ถุงมือการแพทย์, หลอดไฟ, สเปรย์",
                "prohibited": "ขยะทั่วไป", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-13-104", "floor": 1, "type": "e-waste", "type_th": "ขยะอิเล็กทรอนิกส์",
                "loc": "จุดคัดแยกขยะอิเล็กทรอนิกส์ สำนักงานคณบดี",
                "items": "ถ่านไฟฉาย, แบตเตอรี่, สายชาร์จ, แฟลชไดรฟ์เสีย",
                "prohibited": "ขยะทั่วไป", "status": "พร้อมใช้งาน"
            }
        ]
    },
    {
        "num": 15, "id": "ST", "name_en": "Stang Mongkolsuk Building (ST)", "name_th": "อาคารสตางค์ มงคลสุข",
        "x_pct": 29.73, "y_pct": 16.38, "icon": "📚",
        "zone": "โซนซ้าย ติดสนามฟุตบอลและลานจอดรถ GATE 1", "floors": [1],
        "description": "ห้องสมุดสตางค์ มงคลสุข (Stang Library) แหล่งค้นคว้าวิจัย และ Co-working Space",
        "gates": ["GATE 1"],
        "bins": [
            {
                "id": "BIN-15-101", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป (ขยะฝังกลบ)",
                "loc": "โถงทางเข้าชั้น 1 หน้าห้องสมุด",
                "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "ขยะอิเล็กทรอนิกส์, แก้วน้ำมีน้ำแข็ง", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-15-102", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "โถงทางเข้าชั้น 1 หน้าห้องสมุด",
                "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "บรรจุภัณฑ์เปื้อนเศษอาหาร", "status": "พร้อมใช้งาน"
            }
        ]
    },
    {
        "num": 17, "id": "NDCC", "name_en": "National Doping Control Centre (NDCC)", "name_th": "ศูนย์ตรวจสารต้องห้ามในนักกีฬา",
        "x_pct": 30.78, "y_pct": 11.34, "icon": "🏅",
        "zone": "โซนซ้ายบน หลังอาคารสตางค์ มงคลสุข ติดอาคารสัตว์ทดลอง", "floors": [1, 3, 4],
        "description": "สถาบันวิทยาศาสตร์การวิเคราะห์และตรวจสารในการกีฬา มาตรฐานสากล WADA",
        "gates": ["GATE 1"],
        "bins": [
            # ชั้น 1
            {
                "id": "BIN-17-101", "floor": 1, "type": "general", "type_th": "ขยะทั่วไป (ขยะฝังกลบ)",
                "loc": "โถงทางเข้าหลัก ชั้น 1",
                "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "สารเคมีตรวจวิเคราะห์", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-17-102", "floor": 1, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "โถงรับรอง ชั้น 1",
                "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "ขยะเปียก", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-17-103", "floor": 1, "type": "e-waste", "type_th": "ขยะอิเล็กทรอนิกส์",
                "loc": "จุดคัดแยกขยะอิเล็กทรอนิกส์ ชั้น 1",
                "items": "แบตเตอรี่, ถ่านไฟฉาย, แผงวงจร",
                "prohibited": "ขยะทั่วไป", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-17-104", "floor": 1, "type": "e-waste", "type_th": "ขยะอิเล็กทรอนิกส์ (Drop Box)",
                "loc": "กล่อง Drop Box ชั้น 1",
                "items": "แบตเตอรี่, ถ่านไฟฉาย, แผงวงจร",
                "prohibited": "ขยะทั่วไป, ขยะเปียก", "status": "พร้อมใช้งาน"
            },
            # ชั้น 3
            {
                "id": "BIN-17-301", "floor": 3, "type": "general", "type_th": "ขยะทั่วไป (ขยะฝังกลบ)",
                "loc": "โถงทางเดิน ชั้น 3",
                "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "สารเคมี", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-17-302", "floor": 3, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "โถงบันได ชั้น 3",
                "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "บรรจุภัณฑ์เปื้อนเศษอาหาร", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-17-303", "floor": 3, "type": "recycle", "type_th": "ขยะรีไซเคิล (ถังแยกเอกสาร)",
                "loc": "หน้าห้องสำนักงาน ชั้น 3",
                "items": "ถังแยกเอกสารใช้แล้ว, กระดาษ A4, ชีทรายงาน",
                "prohibited": "กระดาษเปื้อนคราบอาหาร", "status": "พร้อมใช้งาน"
            },
            # ชั้น 4
            {
                "id": "BIN-17-401", "floor": 4, "type": "general", "type_th": "ขยะทั่วไป (ขยะฝังกลบ)",
                "loc": "โถงทางเดิน ชั้น 4",
                "items": "ซองขนม, ซองกาแฟ, ทิชชู่, บรรจุภัณฑ์ที่เปื้อนเศษอาหาร",
                "prohibited": "สารเคมี", "status": "พร้อมใช้งาน"
            },
            {
                "id": "BIN-17-402", "floor": 4, "type": "recycle", "type_th": "ขยะรีไซเคิล",
                "loc": "โถงบันได ชั้น 4",
                "items": "ขวดน้ำพลาสติก, กระป๋องอลูมิเนียม, แก้วพลาสติกแข็ง, กล่องพลาสติกที่สะอาด",
                "prohibited": "บรรจุภัณฑ์เปื้อนเศษอาหาร", "status": "พร้อมใช้งาน"
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

BUILDING_BY_NUM = {b["num"]: b for b in BUILDINGS_DATA}

# กำหนดหมุดอาคารที่แสดงบนแผนที่ (เปิด 1, 2, 5, 7, 11, 13, 15, 17)
ACTIVE_BUILDING_NUMS = [1, 2, 5, 7, 11, 13, 15, 17]
ACTIVE_BUILDINGS = [b for b in BUILDINGS_DATA if b["num"] in ACTIVE_BUILDING_NUMS]

# =============================================================================
# 3. การสร้าง Layout Dash App
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
                # กล่องตัวกรองและช่องค้นหา
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
                        # ปุ่มฟิลเตอร์ประเภทขยะ
                        html.Div(
                            className="waste-filter-pills",
                            children=[
                                html.Button("ทั้งหมด (All)", id={"type": "filter-btn", "index": "all"}, className="filter-pill-btn active", n_clicks=0),
                                html.Button("🟡 รีไซเคิล", id={"type": "filter-btn", "index": "recycle"}, className="filter-pill-btn", n_clicks=0),
                                html.Button("🔵 ทั่วไป (ขยะฝังกลบ)", id={"type": "filter-btn", "index": "general"}, className="filter-pill-btn", n_clicks=0),
                                html.Button("🟢 เศษอาหาร", id={"type": "filter-btn", "index": "organic"}, className="filter-pill-btn", n_clicks=0),
                                html.Button("🔴 อันตราย/เคมี", id={"type": "filter-btn", "index": "hazardous"}, className="filter-pill-btn", n_clicks=0),
                                html.Button("🟣 อิเล็กทรอนิกส์", id={"type": "filter-btn", "index": "e-waste"}, className="filter-pill-btn", n_clicks=0),
                            ]
                        ),
                        # กล่อง Information แสดงความรู้ประเภทขยะ
                        html.Div(
                            id="waste-type-info-container",
                            style={"marginTop": "12px"}
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
                                html.Span("👉 คลิกที่หมุดตัวเลขบนอาคารเพื่อเปิดดูจุดทิ้งขยะแยกตามชั้น", className="map-hint-text")
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

        # Pop-up Modal
        html.Div(
            id="building-modal-container",
            style={"display": "none"},
            children=[
                # Backdrop
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
                # Modal Box
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
                        # Header ของ Modal
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
                        # Body ของ Modal (Accordion แยกตามชั้น)
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
# 4. Callbacks
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

# Callback แสดง Information ขยะเบื้องต้นเมื่อคลิกแต่ละประเภท
@app.callback(
    Output("waste-type-info-container", "children"),
    Input("filter-type-store", "data")
)
def render_waste_type_information(filter_type):
    if not filter_type or filter_type == "all":
        return html.Div(
            "💡 คำแนะนำ: คลิกที่ประเภทขยะด้านบนเพื่อดูข้อมูลลักษณะขยะ การย่อยสลาย และสิ่งที่สามารถทิ้งได้",
            style={
                "padding": "10px 14px",
                "backgroundColor": "#F8FAFC",
                "borderRadius": "8px",
                "fontSize": "0.82rem",
                "color": "#64748B",
                "border": "1px dashed #CBD5E1"
            }
        )

    info = WASTE_TYPE_INFO.get(filter_type)
    if not info:
        return html.Div()

    return html.Div(
        style={
            "backgroundColor": info["bg_color"],
            "border": f"1.5px solid {info['border_color']}",
            "borderRadius": "10px",
            "padding": "14px 16px",
            "boxShadow": "0 2px 6px rgba(0,0,0,0.03)"
        },
        children=[
            html.Div(
                info["title"],
                style={"fontWeight": "bold", "color": info["color"], "fontSize": "0.95rem", "marginBottom": "8px"}
            ),
            html.Div([
                html.Span("📋 ลักษณะขยะ: ", style={"fontWeight": "bold", "color": "#1E293B", "fontSize": "0.84rem"}),
                html.Span(info["characteristic"], style={"fontSize": "0.84rem", "color": "#334155"})
            ], style={"marginBottom": "5px"}),
            html.Div([
                html.Span("⏳ การย่อยสลาย: ", style={"fontWeight": "bold", "color": "#1E293B", "fontSize": "0.84rem"}),
                html.Span(info["decomposition"], style={"fontSize": "0.84rem", "color": "#334155"})
            ], style={"marginBottom": "5px"}),
            html.Div([
                html.Span("✅ ขยะที่ทิ้งได้: ", style={"fontWeight": "bold", "color": "#15803D", "fontSize": "0.84rem"}),
                html.Span(info["acceptable_items"], style={"fontSize": "0.84rem", "color": "#334155"})
            ], style={"marginBottom": "5px"}),
            html.Div([
                html.Span("💡 ข้อแนะนำการทิ้ง: ", style={"fontWeight": "bold", "color": "#B45309", "fontSize": "0.82rem"}),
                html.Span(info["handling_tip"], style={"fontSize": "0.82rem", "color": "#475569", "fontStyle": "italic"})
            ])
        ]
    )

# อัปเดตสไตล์ของหมุดบนแผนที่
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

# อัปเดตเนื้อหาใน Pop-up Modal โดยแบ่งจุดทิ้งขยะเป็นแถบตามชั้น (Floor Accordion)
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

    # จัดกลุ่มถังขยะตามชั้นของอาคาร
    bins_by_floor = {}
    for item in displayed_bins:
        floor_num = item.get("floor", 1)
        if floor_num not in bins_by_floor:
            bins_by_floor[floor_num] = []
        bins_by_floor[floor_num].append(item)

    sorted_floors = sorted(bins_by_floor.keys())

    floor_accordions = []
    for idx, f_num in enumerate(sorted_floors):
        floor_items = bins_by_floor[f_num]
        
        cards = []
        for item in floor_items:
            color = BIN_TYPE_COLORS.get(item["type"], "#64748B")
            card = html.Div(
                className="bin-item-card",
                style={
                    "borderLeft": f"4px solid {color}",
                    "marginBottom": "10px",
                    "backgroundColor": "#FFFFFF",
                    "borderRadius": "8px",
                    "padding": "12px 14px",
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.05)",
                    "border": "1px solid #E2E8F0",
                    "borderLeft": f"4px solid {color}"
                },
                children=[
                    html.Div([
                        html.Span(
                            item["type_th"],
                            className="bin-type-badge",
                            style={"backgroundColor": color, "color": "#FFFFFF", "padding": "3px 10px", "borderRadius": "12px", "fontSize": "0.78rem", "fontWeight": "bold"}
                        ),
                        html.Span(f" (ชั้น {item['floor']})", style={"fontSize": "0.82rem", "color": "#475569", "fontWeight": "bold", "marginLeft": "6px"}),
                        html.Span(f"• {item['id']}", style={"fontSize": "0.76rem", "color": "#94A3B8", "float": "right"})
                    ]),
                    html.P([html.Strong("📍 ตำแหน่ง: "), html.Span(item["loc"])], style={"fontSize": "0.85rem", "margin": "8px 0 4px 0", "color": "#1E293B"}),
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
            cards.append(card)

        floor_accordion = html.Details(
            open=(idx == 0),
            style={
                "marginBottom": "12px",
                "border": "1.5px solid #CBD5E1",
                "borderRadius": "10px",
                "overflow": "hidden",
                "backgroundColor": "#F8FAFC"
            },
            children=[
                html.Summary(
                    style={
                        "padding": "12px 16px",
                        "cursor": "pointer",
                        "backgroundColor": "#EEF2F6",
                        "fontWeight": "bold",
                        "fontSize": "0.93rem",
                        "color": "#0F172A",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "space-between",
                        "userSelect": "none"
                    },
                    children=[
                        html.Div([
                            html.Span("🏢 ", style={"fontSize": "1.1rem"}),
                            html.Span(f"ชั้น {f_num}", style={"fontWeight": "700"}),
                            html.Span(f" ({len(floor_items)} จุดทิ้งขยะ)", style={"fontSize": "0.82rem", "color": "#64748B", "marginLeft": "6px", "fontWeight": "normal"})
                        ]),
                        html.Span("▾", style={"fontSize": "1.1rem", "color": "#64748B"})
                    ]
                ),
                html.Div(
                    cards,
                    style={"padding": "12px 12px 2px 12px", "backgroundColor": "#F8FAFC"}
                )
            ]
        )
        floor_accordions.append(floor_accordion)

    if not floor_accordions:
        floor_accordions = [
            html.Div(
                "ไม่พบจุดทิ้งขยะที่ตรงกับเงื่อนไขการค้นหาในอาคารนี้",
                style={"padding": "16px", "background": "#FEF2F2", "color": "#991B1B", "borderRadius": "8px", "fontSize": "0.86rem", "textAlign": "center"}
            )
        ]

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
        html.Div(floor_accordions)
    ]

    return header_content, body_content

# =============================================================================
# 5. การรันระบบ
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Phayathai Campus Trash & Bin Finder Map (Updated with Document Data)")
    print("🌐 เข้าใช้งานได้ที่: http://127.0.0.1:8050")
    print("=" * 70)
    app.run(debug=True, host="127.0.0.1", port=8050, use_reloader=False)

    