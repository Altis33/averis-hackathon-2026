import re

def normalize_string(text):
    if not text:
        return ""
    # Convert to upper case
    text = text.upper()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_port(port):
    if not port:
        return ""
    port = normalize_string(port)
    # Remove country names or port codes commonly found in parentheses
    # E.g. "NANTONG CHINA CNNTG" -> we already removed punctuation, so it's "NANTONG CHINA CNNTG"
    # Actually, let's keep it simple first
    return port

def normalize_company(company):
    if not company:
        return ""
    company = normalize_string(company)
    # Remove common suffixes
    suffixes = ["LTD", "LLC", "INC", "CO", "PTE", "SDN", "BHD", "FZE", "FZLLC", "GMBH"]
    words = company.split()
    words = [w for w in words if w not in suffixes]
    return " ".join(words)

def compare_fields(si_fields, bl_fields):
    """
    Compares SI and BL fields.
    Returns (status, has_defect, defect_fields, review_reason)
    status: OK, MISMATCH, NEEDS_REVIEW
    """
    defect_fields = []
    
    missing_count_si = sum(1 for f in si_fields if si_fields[f] is None)
    missing_count_bl = sum(1 for f in bl_fields if bl_fields[f] is None)
    if missing_count_si >= 4 or missing_count_bl >= 4:
        return "NEEDS_REVIEW", False, [], "wrong_doc_type"
        
    for field in si_fields:
        if si_fields[field] is None and bl_fields[field] is None:
            return "NEEDS_REVIEW", False, [], "missing_value"
        elif si_fields[field] is None or bl_fields[field] is None:
            defect_fields.append(field)

    # Compare each field
    # 1. Shipper
    s_sh = normalize_company(si_fields['shipper'])
    b_sh = normalize_company(bl_fields['shipper'])
    if s_sh not in b_sh and b_sh not in s_sh:
        defect_fields.append('shipper')
        
    # 2. Consignee
    s_co = normalize_company(si_fields['consignee'])
    b_co = normalize_company(bl_fields['consignee'])
    if s_co not in b_co and b_co not in s_co:
        defect_fields.append('consignee')
        
    # 3. Notify Party
    s_np = normalize_company(si_fields['notify_party'])
    b_np = normalize_company(bl_fields['notify_party'])
    if s_np not in b_np and b_np not in s_np:
        defect_fields.append('notify_party')
        
    # 4. Port of Loading
    s_pl = normalize_port(si_fields['port_of_loading'])
    b_pl = normalize_port(bl_fields['port_of_loading'])
    if s_pl not in b_pl and b_pl not in s_pl:
        defect_fields.append('port_of_loading')
        
    # 5. Port of Discharge
    s_pd = normalize_port(si_fields['port_of_discharge'])
    b_pd = normalize_port(bl_fields['port_of_discharge'])
    if s_pd not in b_pd and b_pd not in s_pd:
        defect_fields.append('port_of_discharge')
        
    # 6. Container Count
    if si_fields['container_count'] != bl_fields['container_count']:
        defect_fields.append('container_count')
        
    # 7. Gross Weight
    # Sometimes there's a small tolerance, but let's do exact match for now
    if si_fields['gross_weight_kg'] != bl_fields['gross_weight_kg']:
        defect_fields.append('gross_weight_kg')
        
    if defect_fields:
        return "MISMATCH", True, defect_fields, None
    else:
        return "OK", False, [], None
