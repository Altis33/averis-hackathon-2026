import re


# The seven fields required by the hackathon specification
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
    """Clean spaces and punctuation around an extracted value."""
    if value is None:
        return None

    value = value.strip()
    value = re.sub(r"\s+", " ", value)

    return value if value else None


def extract_line_value(text, labels):
    """
    Find the value after one of the given labels.

    Example:
        Shipper: APRIL FAR EAST (M) SDN BHD

    returns:
        APRIL FAR EAST (M) SDN BHD
    """

    for label in labels:
        pattern = rf"(?im)^\s*{label}\s*:\s*(.+?)\s*$"
        match = re.search(pattern, text)

        if match:
            return clean_text(match.group(1))

    return None


def extract_number(text, labels):
    """
    Extract a numeric value after one of the given labels.

    Handles values such as:
        131,058 KG
        131058 KG
    """

    for label in labels:
        pattern = rf"(?im)^\s*{label}\s*:\s*([\d,]+)"
        match = re.search(pattern, text)

        if match:
            value = match.group(1).replace(",", "")
            return int(value)

    return None


def extract_container_count(text):
    """
    Extract the number of containers.

    Handles examples such as:
        Total Containers: 6 x 40'HC
        Container Count: 6 x 40'HC
        Containers: 6
    """

    labels = [
        r"Total Containers",
        r"Container Count",
        r"Containers",
    ]

    for label in labels:
        pattern = rf"(?im)^\s*{label}\s*:\s*(\d+)"
        match = re.search(pattern, text)

        if match:
            return int(match.group(1))

    return None


def extract_fields(text):
    """
    Extract the seven required shipment fields from SI or BL text.
    """

    fields = {
        "shipper": None,
        "consignee": None,
        "notify_party": None,
        "port_of_loading": None,
        "port_of_discharge": None,
        "container_count": None,
        "gross_weight_kg": None,
    }

    # ---------------------------------------------------------
    # 1. SHIPPER
    # ---------------------------------------------------------

    fields["shipper"] = extract_line_value(
        text,
        [
            r"Shipper",
        ],
    )

    # ---------------------------------------------------------
    # 2. CONSIGNEE
    # ---------------------------------------------------------

    fields["consignee"] = extract_line_value(
        text,
        [
            r"Consignee(?:\s*\([^)]*\))?",
            r"To the Order of",
        ],
    )

    # ---------------------------------------------------------
    # 3. NOTIFY PARTY
    # ---------------------------------------------------------

    fields["notify_party"] = extract_line_value(
        text,
        [
            r"Notify Party",
            r"Notify",
        ],
    )

    # ---------------------------------------------------------
    # 4. PORT OF LOADING
    # ---------------------------------------------------------

    fields["port_of_loading"] = extract_line_value(
        text,
        [
            r"Port of Loading(?:\s*\(POL\))?",
            r"Load Port",
            r"POL",
        ],
    )

    # ---------------------------------------------------------
    # 5. PORT OF DISCHARGE
    # ---------------------------------------------------------

    fields["port_of_discharge"] = extract_line_value(
        text,
        [
            r"Port of Discharge(?:\s*\(POD\))?",
            r"Discharge Port",
            r"POD",
        ],
    )

    # ---------------------------------------------------------
    # 6. CONTAINER COUNT
    # ---------------------------------------------------------

    fields["container_count"] = extract_container_count(text)

    # ---------------------------------------------------------
    # 7. GROSS WEIGHT
    # ---------------------------------------------------------

    fields["gross_weight_kg"] = extract_number(
        text,
        [
            r"Gross Wt \(kgs\)",
            r"Gross Wt \(kg\)",
            r"Gross Weight \(KG\)",
            r"Gross Weight \(KGS\)",
            r"Gross Weight",
            r"Gross Wt",
        ],
    )

    return fields


def find_missing_fields(fields):
    """
    Return fields that could not be extracted.

    These can later be used by the system to identify
    missing_value cases for human review.
    """

    return [
        field
        for field in FIELDS
        if fields.get(field) is None
    ]


# -------------------------------------------------------------
# TEST
# -------------------------------------------------------------

if __name__ == "__main__":

    test_text = """
SHIPPING INSTRUCTION
====================

Shipper: APRIL FAR EAST (M) SDN BHD
TOWER 2, AVENUE 5, LEVEL 6; BANGSAR SOUTH CITY, NO. 8 JALAN KERINCHI; 59200 KUALA LUMPUR, MALAYSIA
Consignee (Non-Negotiable): EAST BRIGHT FZ-LLC
RAKEZ AMENITY CENTER; AL HAMRA INDUSTRIAL ZONE, RAK, UAE
Notify: EAST BRIGHT FZ-LLC
Port of Loading (POL): NANTONG, CHINA (CNNTG)
POD: KARACHI, PAKISTAN (PKKHI)
Total Containers: 6 x 40'HC
Gross Wt (kgs): 131,058 KG
Vessel: NAP 914 V.BS007
Voyage: BS012
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