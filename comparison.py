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
    
    # Check for missing values first (NEEDS_REVIEW)
    for field in si_fields:
        if si_fields[field] is None or bl_fields[field] is None:
            return "NEEDS_REVIEW", False, [], "missing_value"

    # Compare each field
    # 1. Shipper
    if normalize_company(si_fields['shipper']) != normalize_company(bl_fields['shipper']):
        defect_fields.append('shipper')
        
    # 2. Consignee
    if normalize_company(si_fields['consignee']) != normalize_company(bl_fields['consignee']):
        defect_fields.append('consignee')
        
    # 3. Notify Party
    if normalize_company(si_fields['notify_party']) != normalize_company(bl_fields['notify_party']):
        defect_fields.append('notify_party')
        
    # 4. Port of Loading
    if normalize_port(si_fields['port_of_loading']) != normalize_port(bl_fields['port_of_loading']):
        defect_fields.append('port_of_loading')
        
    # 5. Port of Discharge
    if normalize_port(si_fields['port_of_discharge']) != normalize_port(bl_fields['port_of_discharge']):
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
