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


def extract_line_value(text, labels):
    for label in labels:
        pattern = rf"(?i){label}\s*[:\-]?\s*([^\n\r]+)"
        match = re.search(pattern, text)

        if match:
            return clean_text(match.group(1))

    return None


def extract_number(text, labels):
    for label in labels:
        pattern = rf"(?i){label}\s*[:\-]?\s*([\d,]+)"
        match = re.search(pattern, text)

        if match:
            value = match.group(1).replace(",", "")
            return int(value)

    return None


def extract_container_count(text):
    labels = [
        r"Total Containers",
        r"No\. of Containers or Packages",
        r"No\. of Containers",
        r"Container Count",
        r"Containers",
    ]

    for label in labels:
        pattern = rf"(?i){label}\s*[:\-]?\s*(\d+)"
        match = re.search(pattern, text)

        if match:
            return int(match.group(1))

    return None


def extract_fields(text):
    fields = {
        "shipper": None,
        "consignee": None,
        "notify_party": None,
        "port_of_loading": None,
        "port_of_discharge": None,
        "container_count": None,
        "gross_weight_kg": None,
    }

    fields["shipper"] = extract_line_value(
        text,
        [
            r"Shipper \(Principal or Seller\)",
            r"Shipper/Exporter",
            r"Shipper\b",
        ],
    )

    fields["consignee"] = extract_line_value(
        text,
        [
            r"Consignee(?:\s*\([^)]*\))?",
            r"To the Order of",
        ],
    )

    fields["notify_party"] = extract_line_value(
        text,
        [
            r"Notify Party",
            r"Notify",
        ],
    )

    fields["port_of_loading"] = extract_line_value(
        text,
        [
            r"Port of Loading(?:\s*\(POL\))?",
            r"Load Port",
            r"POL",
        ],
    )

    fields["port_of_discharge"] = extract_line_value(
        text,
        [
            r"Port of Discharge",
            r"Discharge Port",
            r"POD",
        ],
    )

    fields["container_count"] = extract_container_count(text)

    fields["gross_weight_kg"] = extract_number(
        text,
        [
            r"Gross Weight毛重\(KGS\)",
            r"Gross Weight \(KG\)",
            r"Gross Weight \(KGS\)",
            r"Gross Wt \(kgs\)",
            r"Gross Wt \(kg\)",
            r"Gross Weight",
            r"Gross Wt",
            r"GROSS WEIGHT",
        ],
    )

    return fields


def find_missing_fields(fields):
    return [
        field
        for field in FIELDS
        if fields.get(field) is None
    ]


if __name__ == "__main__":
    test_text = """
SHIPPING INSTRUCTION
========================================

Shipper: APRIL FAR EAST (M) SDN BHD
Consignee (Non-Negotiable): EAST BRIGHT FZ-LLC
Notify: EAST BRIGHT FZ-LLC
Port of Loading (POL): NANTONG, CHINA (CNNTG)
POD: KARACHI, PAKISTAN (PKKHI)
Total Containers: 6 x 40'HC
Gross Wt (kgs): 131,058 KG
"""

    result = extract_fields(test_text)

    print("Extracted fields:")
    print()

    for field, value in result.items():
        print(f"{field}: {value}")

    print()
    print("Missing fields:")

    missing = find_missing_fields(result)

    if missing:
        for field in missing:
            print(f"- {field}")
    else:
        print("None")