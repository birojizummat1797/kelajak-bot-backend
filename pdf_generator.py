import os
import re # <-- Zirhli filtrimiz uchun yadroviy kutubxona
from fpdf import FPDF

def clean_text(text):
    """PDF qulamangligi uchun matnlarni filtrdan o'tkazamiz va kesamiz"""
    if not text: return ""
    text = str(text).replace("–", "-").replace("—", "-").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("`", "'")
    
    # 1-ZIRH: AI yuborishi mumkin bo'lgan o'ta uzun chiziqlarni (---, ===) bitta belgiga qisqartiramiz
    text = re.sub(r'[-_=*~]{4,}', '-', text)
    
    # 2-ZIRH: FPDF ni qulatadigan "bitta probelsiz" o'ta uzun so'zlarni (40 ta harfdan oshsa) majburlab bo'lib yuboramiz
    text = re.sub(r'([^\s]{40})', r'\1 ', text)
    
    return text

class PremiumPDF(FPDF):
    def header(self):
        self.set_fill_color(10, 25, 47)
        self.rect(0, 0, 210, 30, 'F')
        
        self.set_font("helvetica", "B", 18)
        self.set_text_color(100, 255, 218)
        self.cell(0, 10, "KARYERA YO'L XARITASI", border=0, ln=1, align="C")
        
        self.set_font("helvetica", "I", 10)
        self.set_text_color(204, 214, 246)
        self.cell(0, 5, "DeepTech Premium Diagnostika Xulosasi", border=0, ln=1, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(136, 146, 176)
        self.cell(0, 10, f"Sahifa {self.page_no()} | Maxsus generatsiya qilindi", align="C")

def create_personal_roadmap(chat_id: int, user_name: str, ai_data: dict) -> str:
    pdf = PremiumPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # 3-ZIRH: Dinamik sahifa kengligini oldindan hisoblab, FPDF aqlini chalg'itmaymiz
    epw = pdf.epw 
    
    psycho = ai_data.get("psychological_profile", {})
    careers = ai_data.get("careers", {})
    top_match = careers.get("top_match", {})
    roadmap = ai_data.get("roadmap", [])
    finance = ai_data.get("financial_forecast", {})
    tips = ai_data.get("pro_tips", [])
    
    pdf.set_font("helvetica", "B", 20)
    pdf.set_text_color(10, 25, 47) 
    pdf.cell(0, 15, clean_text(f"Hurmatli {user_name},"), ln=1)
    
    pdf.set_font("helvetica", "", 12)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(epw, 8, clean_text("Sizning javoblaringiz asosida chuqur psixologik va professional tahlil o'tkazildi. Sizning yashirin qobiliyatlaringiz: \n"))
    
    pdf.set_fill_color(230, 241, 255)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(10, 25, 47)
    pdf.cell(0, 10, clean_text(" 1. PSIXOLOGIK PROFILINGIZ"), ln=1, fill=True)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(40, 8, clean_text("Arxetipingiz:"), border=0)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 8, clean_text(psycho.get("archetype", "Noma'lum")), ln=1)
    
    pdf.multi_cell(epw, 8, clean_text(f"Super Kuchingiz: {psycho.get('super_power', 'Ma\'lumot yo\'q')}"))
    pdf.multi_cell(epw, 8, clean_text(f"Rivojlantirish kerak: {psycho.get('growth_area', 'Ma\'lumot yo\'q')}"))
    pdf.ln(5)

    pdf.set_fill_color(100, 255, 218) 
    pdf.set_text_color(10, 25, 47) 
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, clean_text(" 2. SIZ UCHUN ENG MOS KASB"), ln=1, fill=True)
    
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 12, clean_text(f" {top_match.get('title', 'Noma\'lum kasb')} ({top_match.get('match_score', 0)}% moslik)"), ln=1)
    
    pdf.set_font("helvetica", "", 12)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(epw, 8, clean_text(f"Nega aynan bu kasb? {top_match.get('why_this', '')}"))
    pdf.ln(3)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, clean_text("Asosiy ko'nikmalar:"), ln=1)
    pdf.set_font("helvetica", "", 12)
    for skill in top_match.get("core_skills", []):
        pdf.set_x(15) # 4-ZIRH: Kursorni majburiy chapga surish
        pdf.multi_cell(epw, 6, clean_text(f"• {skill}"))
    pdf.ln(5)

    pdf.add_page()
    pdf.set_fill_color(230, 241, 255)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(10, 25, 47)
    pdf.cell(0, 10, clean_text(" 3. 6 OYLIK QADAM-BAQADAM REJA"), ln=1, fill=True)
    pdf.ln(5)
    
    for step in roadmap:
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(0, 128, 128) 
        pdf.cell(0, 8, clean_text(f"{step.get('phase', '')}: {step.get('focus', '')}"), ln=1)
        pdf.set_text_color(50, 50, 50)
        pdf.set_font("helvetica", "", 12)
        pdf.set_x(15) # 4-ZIRH qullanildi
        pdf.multi_cell(epw, 8, clean_text(step.get('action', '')))
        pdf.ln(3)
        
    pdf.set_fill_color(10, 25, 47) 
    pdf.set_text_color(255, 255, 255) 
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, clean_text(" 4. MOLIYAVIY KUTILMALAR VA TAVSIYALAR"), ln=1, fill=True)
    
    pdf.set_text_color(50, 50, 50)
    pdf.ln(5)
    pdf.set_font("helvetica", "", 12)
    
    pdf.cell(70, 8, clean_text("Boshlang'ich daromad:"), border=1)
    pdf.cell(0, 8, clean_text(finance.get("starting_income", "-")), border=1, ln=1)
    
    pdf.cell(70, 8, clean_text("1 yildan keyingi potensial:"), border=1)
    pdf.cell(0, 8, clean_text(finance.get("potential_1_year", "-")), border=1, ln=1)
    pdf.ln(5)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, clean_text("Maxsus Tavsiyalar:"), ln=1)
    pdf.set_font("helvetica", "", 12)
    for tip in tips:
        pdf.set_x(15) # 4-ZIRH qullanildi
        pdf.multi_cell(epw, 8, clean_text(f"★ {tip}"))

    os.makedirs("generated_pdfs", exist_ok=True)
    file_path = f"generated_pdfs/Premium_Yol_Xaritasi_{chat_id}.pdf"
    pdf.output(file_path)
    
    return file_path