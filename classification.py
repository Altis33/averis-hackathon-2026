import re

def classify_email(email):
    """
    Classify an email into one of 5 categories:
    BL_COMPARISON, SI_REQUEST, INVOICE_QUERY, GENERAL, SPAM
    """
    subject = email.get('subject', '').lower()
    body = email.get('body', '').lower()
    
    # 1. SPAM
    spam_words = ['bitcoin', 'singles', 'suspension', 'weird trick', 'mailbox', 'storage is full']
    if any(w in subject or w in body for w in spam_words):
        return "SPAM"
        
    # 2. INVOICE_QUERY
    invoice_words = ['invoice', 'billing', 'freight', 'local charges']
    if any(w in subject for w in invoice_words):
        return "INVOICE_QUERY"
        
    # 3. SI_REQUEST
    if "request si" in subject or "cust si" in subject or "si -" in subject or "si _" in subject:
        return "SI_REQUEST"
        
    # 4. BL_COMPARISON
    bl_words = ['aie -', 'afrt -', 'confirm docs', 'bl draft', 'draft bl', 'draft bill of lading']
    if any(w in subject for w in bl_words):
        return "BL_COMPARISON"
        
    # Fallback to BL_COMPARISON if 2 attachments with SI and BL in them
    attachments = email.get('attachments', [])
    has_si = any("si" in a.lower() for a in attachments)
    has_bl = any("bl" in a.lower() for a in attachments)
    if has_si and has_bl:
        return "BL_COMPARISON"

    # 5. GENERAL
    return "GENERAL"

