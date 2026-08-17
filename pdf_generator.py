import os
from fpdf import FPDF

def clean_text(text):
    """PDF qulamangligi uchun matnlarni filtrdan o'tkazamiz"""
    if not text: return ""
    return str(text).replace("–", "-").replace("—", "-").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("`", "'").replace("\n", " ")

class PremiumPDF(FPDF):
    def header(self):
        # Qora fon
        self.set_fill_color(0, 0, 0)
        self.rect(0, 0, 210, 30, 'F')
        
        # Yashil asosiy sarlavha
        self.set_font("helvetica", "B", 18)
        self.set_text_color(0, 200, 83)
        self.cell(0, 10, "KARYERA YO'L XARITASI", border=0, ln=1, align="C")
        
        # Kumush rangli ost-sarlavha
        self.set_font("helvetica", "I", 10)
        self.set_text_color(192, 192, 192)
        self.cell(0, 5, "DeepTech Premium Diagnostika Xulosasi", border=0, ln=1, align="C")
        self.ln(10)

    def footer(self):
        # Kumush rangli alt-kolontitul
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(192, 192, 192)
        self.cell(0, 10, f"Sahifa {self.page_no()} | Maxsus generatsiya qilindi", align="C")

def create_personal_roadmap(chat_id: int, user_name: str, ai_data: dict) -> str:
    pdf = PremiumPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # YANGI AI QOLIPIDAGI KALITLARNI O'QISH
    psycho = ai_data.get("psychological_profile", {})
    careers = ai_data.get("careers", {})
    top_match = careers.get("top_match", {})
    roadmap = ai_data.get("roadmap", [])
    finance = ai_data.get("financial_forecast", {})
    tips = ai_data.get("pro_tips", [])
    
    # --- 1. KIRISH VA PSIXOLOGIK PORTRET ---
    pdf.set_font("helvetica", "B", 20)
    pdf.set_text_color(0, 0, 0) # Qora matn
    pdf.cell(0, 15, clean_text(f"Hurmatli {user_name},"), ln=1)
    
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(0, 8, clean_text("Sizning javoblaringiz asosida chuqur psixologik va professional tahlil o'tkazildi. Sizning yashirin qobiliyatlaringiz: \n"))
    
    # Psixologik blok (Och kumush fon)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, clean_text("1. PSIXOLOGIK PROFILINGIZ"), ln=1, fill=True)
    
    pdf.set_font("helvetica", "", 12)
    pdf.cell(40, 8, clean_text("Arxetipingiz:"), border=0)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, clean_text(psycho.get("archetype", "Noma'lum")), ln=1)
    
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(0, 8, clean_text(f"Super Kuchingiz: {psycho.get('super_power', 'Ma\'lumot yo\'q')}"))
    pdf.multi_cell(0, 8, clean_text(f"Rivojlantirish kerak: {psycho.get('growth_area', 'Ma\'lumot yo\'q')}"))
    pdf.ln(5)

    # --- 2. ASOSIY KASB (Yashil fon, Oq matn bilan ajratilgan) ---
    pdf.set_fill_color(0, 200, 83) 
    pdf.set_text_color(255, 255, 255) 
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, clean_text("2. SIZ UCHUN ENG MOS KASB"), ln=1, fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 12, clean_text(f" {top_match.get('title', 'Noma\'lum kasb')} ({top_match.get('match_score', 0)}% moslik)"), ln=1)
    
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(0, 8, clean_text(f"Nega aynan bu kasb? {top_match.get('why_this', '')}"))
    pdf.ln(3)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, clean_text("Asosiy ko'nikmalar:"), ln=1)
    pdf.set_font("helvetica", "", 12)
    for skill in top_match.get("core_skills", []):
        pdf.cell(10, 6, "-", ln=0, align="R")
        pdf.cell(0, 6, clean_text(skill), ln=1)
    pdf.ln(5)

    # --- 3. YO'L XARITASI ---
    pdf.add_page()
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, clean_text("3. 6 OYLIK QADAM-BAQADAM REJA"), ln=1, fill=True)
    pdf.ln(5)
    
    for step in roadmap:
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(0, 200, 83) # Yashil qadamlar
        pdf.cell(0, 8, clean_text(f"{step.get('phase', '')}: {step.get('focus', '')}"), ln=1)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("helvetica", "", 12)
        pdf.multi_cell(0, 8, clean_text(step.get('action', '')))
        pdf.ln(3)
        
    # --- 4. MOLIYA VA TAVSIYALAR (Qora fon, Oq matn) ---
    pdf.set_fill_color(0, 0, 0)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, clean_text("4. MOLIYAVIY KUTILMALAR VA TAVSIYALAR"), ln=1, fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    pdf.set_font("helvetica", "", 12)
    
    pdf.cell(60, 8, clean_text("Boshlang'ich daromad:"), border=1)
    pdf.cell(0, 8, clean_text(finance.get("starting_income", "-")), border=1, ln=1)
    
    pdf.cell(60, 8, clean_text("1 yildan keyingi potensial:"), border=1)
    pdf.cell(0, 8, clean_text(finance.get("potential_1_year", "-")), border=1, ln=1)
    pdf.ln(5)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, clean_text("Maxsus Tavsiyalar:"), ln=1)
    pdf.set_font("helvetica", "", 12)
    for tip in tips:
        pdf.cell(10, 8, "*", ln=0, align="R")
        pdf.multi_cell(0, 8, clean_text(tip))

    os.makedirs("generated_pdfs", exist_ok=True)
    file_path = f"generated_pdfs/Premium_Yol_Xaritasi_{chat_id}.pdf"
    pdf.output(file_path)
    
    return file_path