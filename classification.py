import re

spam_patterns = [
    r'gift card', r'parcel is on hold', r'storage is full', r'premium logistics software',
    r'confirm your bank details', r'undelivered messages', r'weird trick', r'avoid suspension',
    r'hot singles', r'bitcoin', r'prize-claims', r'parcel-track', r'webmail-verify',
    r'logistics-deals', r'crypto-invest', r'secure-mailbox'
]

invoice_patterns = [
    r'rak billing', r'missing gr', r'cancel invoice', r'local charges', r'd & d charges',
    r'total freight'
]

si_patterns = [
    r'^\s*(re_\s*)?si\s*-', r'cust si', r'request si', r'si needed'
]

bl_patterns = [
    r'to confirm docs', r'^(re_\s*)?(aie|afptme|afrt|afemy)\s*-',
    r'request bl draft', r'draft bl'
]

general_patterns = [
    r'update summary', r'berthing report', r'submit si & aed',
    r'billing process completed', r'list of outstanding bl',
    r'pending bl release', r'welcoming the new year', r'time off request',
    r'miss connection', r'delivery planning'
]

def classify_email(email):
    """
    Classify an email record into one of 5 categories:
    BL_COMPARISON, SI_REQUEST, INVOICE_QUERY, GENERAL, SPAM
    """
    subj = email.get('subject', '').lower()
    body = email.get('body', '').lower()
    frm = email.get('from', '').lower()
    
    # 1. SPAM
    for p in spam_patterns:
        if re.search(p, subj) or re.search(p, frm):
            return 'SPAM'
            
    # 2. INVOICE_QUERY
    for p in invoice_patterns:
        if re.search(p, subj):
            return 'INVOICE_QUERY'
            
    # 3. SI_REQUEST
    for p in si_patterns:
        if re.search(p, subj):
            return 'SI_REQUEST'
            
    # 4. BL_COMPARISON
    for p in bl_patterns:
        if re.search(p, subj):
            return 'BL_COMPARISON'
            
    # 5. GENERAL
    for p in general_patterns:
        if re.search(p, subj):
            return 'GENERAL'
            
    # Fallback: check body keywords
    if 'draft bl' in body or 'shipping instruction' in body:
        return 'BL_COMPARISON'
        
    return 'GENERAL'
