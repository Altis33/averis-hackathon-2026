import re

def normalize_company(name):
    if not name:
        return ""
    name = name.upper()
    name = re.sub(r"[|;].*$", "", name)
    name = re.sub(r"[^\w\s]", "", name)
    suffixes = ["LTD", "LLC", "INC", "CO", "PTE", "SDN", "BHD", "FZE", "FZLLC", "GMBH", "PTY", "UAB"]
    words = [w for w in name.split() if w not in suffixes]
    return " ".join(words).strip()

def normalize_port(port):
    if not port:
        return ""
    port = port.upper()
    port = re.sub(r"\([A-Z0-9/]+\)", "", port)
    port = re.sub(r"[^\w\s]", "", port)
    return re.sub(r"\s+", " ", port).strip()

def compare_fields(si_fields, bl_fields):
    """
    Compares SI and BL fields.
    Returns (status, has_defect, defect_fields, review_reason)
    """
    defect_fields = []
    
    # 1. Shipper
    s_sh = normalize_company(si_fields.get('shipper'))
    b_sh = normalize_company(bl_fields.get('shipper'))
    if ("MIDDLE EAST" in s_sh) != ("MIDDLE EAST" in b_sh) or ("FAR EAST" in s_sh) != ("FAR EAST" in b_sh):
        defect_fields.append('shipper')
    elif s_sh and b_sh:
        if s_sh not in b_sh and b_sh not in s_sh:
            defect_fields.append('shipper')
    elif s_sh != b_sh:
        defect_fields.append('shipper')
        
    # 2. Consignee
    s_co = normalize_company(si_fields.get('consignee'))
    b_co = normalize_company(bl_fields.get('consignee'))
    if s_co and b_co:
        if s_co not in b_co and b_co not in s_co:
            defect_fields.append('consignee')
    elif s_co != b_co:
        defect_fields.append('consignee')
        
    # 3. Notify Party
    s_np = normalize_company(si_fields.get('notify_party'))
    b_np = normalize_company(bl_fields.get('notify_party'))
    if s_np and b_np:
        if s_np not in b_np and b_np not in s_np:
            defect_fields.append('notify_party')
    elif s_np != b_np:
        defect_fields.append('notify_party')
        
    # 4. Port of Loading
    s_pl = normalize_port(si_fields.get('port_of_loading'))
    b_pl = normalize_port(bl_fields.get('port_of_loading'))
    if s_pl and b_pl:
        if s_pl not in b_pl and b_pl not in s_pl:
            defect_fields.append('port_of_loading')
    elif s_pl != b_pl:
        defect_fields.append('port_of_loading')
        
    # 5. Port of Discharge
    s_pd = normalize_port(si_fields.get('port_of_discharge'))
    b_pd = normalize_port(bl_fields.get('port_of_discharge'))
    if s_pd and b_pd:
        if s_pd not in b_pd and b_pd not in s_pd:
            defect_fields.append('port_of_discharge')
    elif s_pd != b_pd:
        defect_fields.append('port_of_discharge')
        
    # 6. Container Count
    if si_fields.get('container_count') != bl_fields.get('container_count'):
        defect_fields.append('container_count')
        
    # 7. Gross Weight
    if si_fields.get('gross_weight_kg') != bl_fields.get('gross_weight_kg'):
        defect_fields.append('gross_weight_kg')
        
    if defect_fields:
        return "MISMATCH", True, sorted(defect_fields), None
    return "OK", False, [], None
