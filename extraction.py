import re

FIELDS = [
    "shipper",
    "consignee",
    "notify_party",
    "port_of_loading",
    "port_of_discharge",
    "container_count",
    "gross_weight_kg",
]

def clean_text(value):
    if value is None:
        return None
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    return value if value else None

def extract_field_value(text, labels):
    for label in labels:
        # Multi-line match (label on line N, value on line N+1 or same line)
        pattern = rf"(?i)(?:^|\n)\s*{label}(?:\s*\([^)]+\))*\s*[:\-]?\s*(?:\n+|\s+)([^\n\r]+)"
        match = re.search(pattern, text)
        if match:
            val = match.group(1).strip()
            val = re.sub(r"\s*\([A-Z0-9/]+\)\s*$", "", val)
            cleaned = clean_text(val)
            if cleaned:
                return cleaned
                
        # Same-line fallback
        pattern_fallback = rf"(?i){label}(?:\s*\([^)]+\))*\s*[:\-]?\s*([^\n\r]+)"
        match = re.search(pattern_fallback, text)
        if match:
            val = match.group(1).strip()
            val = re.sub(r"\s*\([A-Z0-9/]+\)\s*$", "", val)
            cleaned = clean_text(val)
            if cleaned:
                return cleaned
    return None

def extract_container_count(text):
    labels = [
        r"No\. of Containers or Packages",
        r"No\. of Containers",
        r"Total Containers",
        r"Container Count",
        r"Containers",
    ]
    for label in labels:
        pattern = rf"(?i){label}(?:\s*\([^)]+\))*\s*[:\-]?\s*(?:\n+|\s+)(\d+)"
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    return None

def extract_gross_weight(text):
    # Total gross weight in summary lines or PDF summaries
    m_pdf = re.search(r"(?i)(?:TOTAL\s+)?Weight[^\d\n\r]*[:\-]\s*([\d,]+)", text)
    if m_pdf:
        val = m_pdf.group(1).replace(",", "").strip()
        if val.isdigit():
            return int(val)

    labels = [
        r"Gross Weight毛重\(KGS\)",
        r"Gross Weight \(KG\)",
        r"Gross Weight \(KGS\)",
        r"Gross Wt \(kgs\)",
        r"Gross Wt \(kg\)",
        r"Gross Weight",
        r"Gross Wt",
        r"GROSS WEIGHT",
    ]
    for label in labels:
        pattern = rf"(?i){label}(?:\s*\([^)]+\))*\s*[:\-]?\s*(?:\n+|\s+)([\d,]+)"
        match = re.search(pattern, text)
        if match:
            val = match.group(1).replace(",", "").strip()
            if val.isdigit():
                return int(val)
    return None

def extract_fields(text):
    fields = {f: None for f in FIELDS}

    fields["shipper"] = extract_field_value(text, [
        r"Shipper \(Principal or Seller\)",
        r"Shipper/Exporter",
        r"Shipper\b",
        r"SHIPPER",
    ])

    # Ensure Consignee does NOT match Notify Party/Intermediate Consignee
    fields["consignee"] = extract_field_value(text, [
        r"Consignee \(Non-Negotiable\)",
        r"To the Order of",
        r"(?<!Intermediate\s)(?<!/)\bConsignee\b",
        r"CONSIGNEE",
    ])

    fields["notify_party"] = extract_field_value(text, [
        r"Notify Party/Intermediate Consignee",
        r"Notify Party",
        r"Notify\b",
        r"NOTIFY PARTY",
    ])

    fields["port_of_loading"] = extract_field_value(text, [
        r"Port of Loading \(POL\)",
        r"Port of Loading",
        r"Load Port",
        r"POL\b",
        r"PORT OF LOADING",
    ])

    fields["port_of_discharge"] = extract_field_value(text, [
        r"Port of Discharge \(POD\)",
        r"Port of Discharge",
        r"Discharge Port",
        r"POD\b",
        r"PORT OF DISCHARGE",
    ])

    fields["container_count"] = extract_container_count(text)
    fields["gross_weight_kg"] = extract_gross_weight(text)

    return fields

def find_missing_fields(fields):
    return [field for field in FIELDS if fields.get(field) is None]