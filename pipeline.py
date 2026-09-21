import json
import os
import sys

sys.path.insert(0, "sdoc-hackathon-bundle")
from loader import Inbox
import extraction
import comparison
import doc_parser
import classification

def run_pipeline(data_dir, output_file):
    inbox = Inbox(data_dir)
    submission = {}
    
    for email in inbox:
        eid = email['email_id']
        category = classification.classify_email(email)
        
        if category == "BL_COMPARISON":
            attachments = email.get('attachments', [])
            si_path = next((a for a in attachments if 'si' in a.lower()), None)
            bl_path = next((a for a in attachments if 'bl' in a.lower()), None)
            
            # Fallback if names don't contain 'si' or 'bl' but it has exactly 2 attachments
            if not si_path and len(attachments) >= 1:
                si_path = attachments[0]
            if not bl_path and len(attachments) >= 2:
                bl_path = attachments[1]
            
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
            
            si_text = doc_parser.extract_text_from_bytes(si_bytes, si_path)
            bl_text = doc_parser.extract_text_from_bytes(bl_bytes, bl_path)
            
            si_fields = extraction.extract_fields(si_text)
            bl_fields = extraction.extract_fields(bl_text)
            
            status, has_defect, defect_fields, review_reason = comparison.compare_fields(si_fields, bl_fields)
            
            if not si_text.strip() or not bl_text.strip():
                status = "NEEDS_REVIEW"
                review_reason = "unreadable"
            
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
    run_pipeline("sdoc-hackathon-bundle", "submission_final.json")
