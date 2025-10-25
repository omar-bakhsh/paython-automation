import re
from collections import defaultdict
from pdfminer.high_level import extract_text

def extract_text_from_pdf(pdf_path):
    """
    يستخرج النص من ملف PDF باستخدام pdfminer.six.
    """
    try:
        text = extract_text(pdf_path)
        return text
    except Exception as e:
        print(f"حدث خطأ أثناء استخراج النص من PDF: {e}")
        return None

def analyze_pdf_text(pdf_text):
    """
    يحلل النص المستخرج من PDF لتجميع المبالغ المطلوبة.
    """
    # 1. تجميع مبالغ المحاليل والفنيين والمواد
    technician_amounts = defaultdict(float)
    material_totals = defaultdict(float)
    solution_totals = defaultdict(float)

    # المواد المطلوبة من المستخدم (التي تجمع بمفردها) - الكلمات المفتاحية في النص المستخرج (معكوسة)
    material_keywords = {
        "اسيديلكو دبليو 4": ["وكليديسا"],
        "سليكون": ["نوكيلس"],
        "خرط هوبات": ["تابوه طرخ"]
    }

    # المحاليل الأخرى المذكورة في المستند (التي تجمع بمفردها) - الكلمات المفتاحية في النص المستخرج (معكوسة)
    solution_keywords = {
        "لمارف تيز": ["لمارف تيز"],
        "ماسو": ["ماسو"],
        "سراف": ["سراف"],
        "ويلبد": ["ويلبد"],
        "للاط دمحا": ["للاط دمحا"],
        "ةلاكو عطق": ["ةلاكو عطق"]
    }

    # قائمة بأسماء الفنيين المحتملين من البيانات (معكوسة)
    technicians_list = [
        "يبرحلا دمحم رباج", "قيدص ميهاربا", "ايركز دمحم", "سنح دجام", "شييبلا ليع", 
        "يرهشلا دمحم", "ييرطملا يراس", "ينميثعلا دلاخ", "ينارهزلا فسوي"
    ]
    
    # دمج جميع الكلمات المفتاحية للمواد والمحاليل
    all_item_keywords = {**material_keywords, **solution_keywords}

    lines = pdf_text.split('\n')
    data_lines = []
    
    # منطق لدمج السطور المتقطعة:
    current_record = []
    in_data_section = False
    
    # الكلمات المفتاحية التي تدل على بداية قسم البيانات (سطر الرأس)
    header_keywords = ["عفدلا ليامجا", "شاك", "ليوحت", "ةكبش", "ليمعلا مسا"]
    
    # الكلمات المفتاحية التي تدل على نهاية قسم البيانات
    end_keywords = ["ليامجا", "TOTAL DAILY INCOME", "فيراصملا"]

    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # تحديد بداية قسم البيانات (سطر الرأس)
        if all(kw in line for kw in header_keywords) and "ليمعلا مسا" in line:
            in_data_section = True
            continue
            
        # تحديد نهاية قسم البيانات
        if any(kw in line for kw in end_keywords):
            if in_data_section and current_record:
                data_lines.append(" ".join(current_record))
            in_data_section = False
            break
            
        if not in_data_section:
            continue
            
        # محاولة تجميع السطور في سجل واحد
        # السجل يبدأ بمبلغ (رقم)
        if re.match(r'^\d+\.?\d*$', line) or re.match(r'^\d+\s', line):
            if current_record:
                data_lines.append(" ".join(current_record))
            current_record = [line]
        elif current_record:
            # إذا كان السطر لا يبدأ برقم، ندمجه مع السجل الحالي
            current_record.append(line)
            
    if current_record:
        data_lines.append(" ".join(current_record))
        
    # معالجة كل سطر بيانات مدمج
    for line in data_lines:
        
        # 1. استخراج اسم الفني وتجميع مبالغ الفنيين
        technician_name = "غير محدد"
        
        # البحث عن اسم الفني
        for tech_name in technicians_list:
            if re.search(r'\b' + re.escape(tech_name) + r'\b', line):
                technician_name = tech_name
                break
                
        # تجميع مبالغ الفنيين
        if technician_name != "غير محدد":
            # المبلغ الخاص بالفني هو الرقم الخامس (عمود "نيفلا غلبملا")
            # نستخدم findall لاستخراج جميع الأرقام من بداية السطر
            numbers = re.findall(r'(\d+\.\d+|\d+)', line.replace(',', ''))
            
            # المبلغ الخامس هو مبلغ الفني (تم التحقق يدوياً من النص الخام)
            if len(numbers) >= 5:
                try:
                    technician_amount = float(numbers[4])
                    technician_amounts[technician_name] += technician_amount
                except (ValueError, IndexError):
                    pass

        # 2. استخراج وتجميع مبالغ المواد والمحاليل المحددة
        
        for item_name, keywords in all_item_keywords.items():
            for keyword in keywords:
                # نبحث عن نمط المبلغ=الكلمة المفتاحية
                # النمط: (مبلغ) = (الكلمة المفتاحية)
                # نستخدم نمطاً أكثر مرونة للتعامل مع المسافات الزائدة
                match_amount = re.search(r'(\d+\.?\d*)\s*=\s*' + re.escape(keyword), line)
                
                if match_amount:
                    amount = float(match_amount.group(1))
                    
                    # تصنيف البند إلى مواد محددة أو محاليل
                    if item_name in material_keywords:
                        material_totals[item_name] += amount
                    else:
                        solution_totals[item_name] += amount

    # 3. حساب الإجماليات
    total_technicians = sum(technician_amounts.values())
    total_materials = sum(material_totals.values())
    total_solutions = sum(solution_totals.values())

    # 4. تجميع كل الإجماليات في ملف نصي
    output_content = "إجماليات مبالغ الفنيين والمحاليل والمواد المحددة:\n\n"

    output_content += "1. إجماليات مبالغ الفنيين:\n"
    for technician, amount in technician_amounts.items():
        # عكس اسم الفني لجعله مقروءاً
        readable_name = " ".join(technician.split()[::-1])
        output_content += f"- {readable_name}: {amount:.2f}\n"
    output_content += f"**المجموع الكلي لمبالغ الفنيين:** {total_technicians:.2f}\n\n"

    output_content += "2. إجماليات مبالغ المواد المحددة (اسيديلكو دبليو 4، سليكون، خرط هوبات):\n"
    for material, amount in material_totals.items():
        output_content += f"- {material}: {amount:.2f}\n"
    output_content += f"**المجموع الكلي لمبالغ المواد المحددة:** {total_materials:.2f}\n\n"

    output_content += "3. إجماليات مبالغ المحاليل الأخرى (حسب النوع):\n"
    for solution, amount in solution_totals.items():
        # عكس اسم المحلول لجعله مقروءاً إذا كان معكوساً
        if solution in ["لمارف تيز", "ماسو", "سراف", "ويلبد", "للاط دمحا", "ةلاكو عطق"]:
             readable_solution = " ".join(solution.split()[::-1])
        else:
            readable_solution = solution
        output_content += f"- {readable_solution}: {amount:.2f}\n"
    output_content += f"**المجموع الكلي لمبالغ المحاليل الأخرى:** {total_solutions:.2f}\n\n"

    # الإجمالي العام
    output_content += f"**الإجمالي العام لكل البنود المجمعة:** {total_technicians + total_materials + total_solutions:.2f}\n"

    # كتابة الملف النصي
    with open("summary_report.txt", "w", encoding="utf-8") as f:
        f.write(output_content)

    return output_content

# المسار إلى ملف PDF المرفق
pdf_file_path = "C:/Users/Amoory/Downloads/Day-22-1.pdf"

# استخراج النص من PDF
extracted_text = extract_text_from_pdf(pdf_file_path)

if extracted_text:
    # تحليل النص وتوليد التقرير
    report = analyze_pdf_text(extracted_text)
    # print("تم إنشاء ملف summary_report.txt بنجاح.")
    # print(report) # لا نطبع التقرير هنا لتجنب تكرار الإخراج
else:
    print("فشل استخراج النص من ملف PDF.")
