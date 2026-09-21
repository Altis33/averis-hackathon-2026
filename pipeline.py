import json
import os
import sys
sys.path.insert(0, "sdoc-hackathon-bundle")
from loader import Inbox
import extraction
import comparison

def categorize_email(email):
    subject = email.get('subject', '').lower()
    body = email.get('body', '').lower()
    
    if "invoice" in subject:
        return "INVOICE_QUERY"
    if "new si" in subject or "new shipping instruction" in subject:
        return "SI_REQUEST"
    if "spam" in subject:
        return "SPAM"
    
    # Check if there are attachments and if they look like SI and BL
    attachments = email.get('attachments', [])
    has_si = any("si" in a.lower() for a in attachments)
    has_bl = any("bl" in a.lower() for a in attachments)
    
    if has_si and has_bl:
        return "BL_COMPARISON"
        
    return "GENERAL"

def run_pipeline(data_dir, output_file):
    inbox = Inbox(data_dir)
    submission = {}
    
    for email in inbox:
        eid = email['email_id']
        category = categorize_email(email)
        
        if category == "BL_COMPARISON":
            attachments = email.get('attachments', [])
            si_path = next((a for a in attachments if 'si' in a.lower()), None)
            bl_path = next((a for a in attachments if 'bl' in a.lower()), None)
            
            if not si_path or not bl_path:
                submission[eid] = {
                    "category": category,
                    "status": "NEEDS_REVIEW",
                    "review_reason": "missing_attachment",
                    "has_defect": False,
                    "defect_fields": []
                }
                continue
                
            si_bytes = inbox.read_bytes(si_path)
            bl_bytes = inbox.read_bytes(bl_path)
            
            import doc_parser
            si_text = doc_parser.extract_text_from_bytes(si_bytes, si_path)
            bl_text = doc_parser.extract_text_from_bytes(bl_bytes, bl_path)
            
            si_fields = extraction.extract_fields(si_text)
            bl_fields = extraction.extract_fields(bl_text)
            
            status, has_defect, defect_fields, review_reason = comparison.compare_fields(si_fields, bl_fields)
            
            submission[eid] = {
                "category": category,
                "status": status,
                "review_reason": review_reason,
                "has_defect": has_defect,
                "defect_fields": defect_fields
            }
        else:
            submission[eid] = {
                "category": category,
                "status": "OK",
                "review_reason": None,
                "has_defect": False,
                "defect_fields": []
            }
            
    with open(output_file, "w") as f:
        json.dump(submission, f, indent=2)

if __name__ == "__main__":
    run_pipeline("sdoc-hackathon-bundle", "submission.json")
