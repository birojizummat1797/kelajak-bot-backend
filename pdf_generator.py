import os
from fpdf import FPDF
from datetime import datetime

def clean_text(text):
    """AI dan kelgan matndagi PDF tushunmaydigan belgilarni tozalaydi"""
    if not text: return ""
    # Uzun chiziqlar va jingalak belgilarni standartiga almashtirish
    return str(text).replace("–", "-").replace("—", "-").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("`", "'")

class PremiumPDF(FPDF):
    def header(self):
        # Yuqori qism (Header) dizayni
        self.set_fill_color(0, 0, 0) # Qora fonga
        self.rect(0, 0, 210, 30, 'F')
        
        self.set_font("helvetica", "B", 18)
        self.set_text_color(0, 200, 83) # Yashil matn
        self.cell(0, 10, "KARYERA YO'L XARITASI", border=0, ln=1, align="C")
        
        self.set_font("helvetica", "I", 10)
        self.set_text_color(192, 192, 192) # Kumush matn
        self.cell(0, 5, "DeepTech Premium Diagnostika Xulosasi", border=0, ln=1, align="C")
        self.ln(10)

    def footer(self):
        # Pastki qism (Footer) dizayni
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Sahifa {self.page_no()} | Avtomatik generatsiya qilindi", align="C")

def create_personal_roadmap(chat_id: int, user_name: str, ai_data: dict) -> str:
    """
    AI ma'lumotlari asosida 3 sahifalik Premium PDF xaritani yaratadi va fayl manzilini qaytaradi.
    """
    pdf = PremiumPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    career_info = ai_data.get("top_career", {})
    
    # MATNLARNI TOZALASH (FILTRDAN O'TKAZISH)
    title = clean_text(career_info.get("title", "Noma'lum"))
    reason = clean_text(career_info.get("reason", "Tahlil natijasi mavjud emas."))
    time_to_learn = clean_text(career_info.get("time_to_learn", "-"))
    salary = clean_text(career_info.get("salary_expectation", "-"))
    risk = clean_text(career_info.get("biggest_risk", "Ma'lumot yo'q"))
    
    # 1-SAHIFA: Xulosa va Natija
    pdf.set_font("helvetica", "B", 22)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 15, clean_text(f"Assalomu alaykum, {user_name}!"), ln=1, align="L")
    
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(0, 8, clean_text("Sizning psixologik profilingiz, yashirin qobiliyatlaringiz va hozirgi sharoitlaringiz 100+ kasblar bazasi bilan solishtirildi. Eng kuchli moslik topildi:"))
    pdf.ln(5)
    
    # Kasb bloki
    pdf.set_fill_color(240, 255, 240) # Och yashil
    pdf.set_draw_color(0, 200, 83) # Yashil ramka
    pdf.cell(0, 20, f" KASB: {title}", border=1, ln=1, align="C", fill=True)
    pdf.ln(5)
    
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, clean_text("Nima uchun aynan shu kasb?"), ln=1)
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(0, 8, reason)
    pdf.ln(10)
    
    # 2-SAHIFA: Reja va Texnologiyalar
    pdf.add_page()
    pdf.set_font("helvetica", "B", 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, clean_text("O'rganilishi kerak bo'lgan texnologiyalar"), ln=1)
    pdf.ln(5)
    
    pdf.set_font("helvetica", "", 12)
    for tech in career_info.get("technologies", []):
        pdf.cell(10, 8, "-", ln=0)
        pdf.cell(0, 8, clean_text(str(tech)), ln=1)
        
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, clean_text("Kutilayotgan Natijalar:"), ln=1)
    
    pdf.set_font("helvetica", "", 12)
    pdf.cell(50, 10, clean_text("O'rganish vaqti:"), border=1)
    pdf.cell(0, 10, f" {time_to_learn}", border=1, ln=1)
    
    pdf.cell(50, 10, clean_text("Daromad:"), border=1)
    pdf.cell(0, 10, f" {salary}", border=1, ln=1)
    
    pdf.ln(15)
    pdf.set_fill_color(255, 240, 240) # Och qizil (Xavf uchun)
    pdf.set_draw_color(255, 0, 0)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, clean_text("Sohadagi Eng Katta Xavf:"), border=1, ln=1, fill=True)
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(0, 8, risk, border=1, fill=True)

    # Papka mavjudligini tekshirish
    os.makedirs("generated_pdfs", exist_ok=True)
    
    # Faylni saqlash
    file_path = f"generated_pdfs/Yol_Xaritasi_{chat_id}.pdf"
    pdf.output(file_path)
    
    return file_path