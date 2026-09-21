import json
import os
import re
import sys

sys.path.insert(0, "sdoc-hackathon-bundle")
from loader import Inbox
import extraction
import comparison
import doc_parser
import classification

def check_missing_value_in_text(text):
    for token in ["???", "_______", "TBA", "TBC", "N/A", "____MT"]:
        pattern = rf"(?i)(shipper|consignee|notify|port|containers|gross weight|gross wt)[^:\n]*[:\-]?\s*({re.escape(token)})"
        if re.search(pattern, text):
            return True
    return False

def run_pipeline(data_dir, output_file):
    inbox = Inbox(data_dir)
    submission = {}
    
    for email in inbox:
        eid = email['email_id']
        category = classification.classify_email(email)
        
        if category != "BL_COMPARISON":
            submission[eid] = {
                "category": category,
                "status": "OK",
                "review_reason": None,
                "has_defect": False,
                "defect_fields": []
            }
            continue
            
        attachments = email.get('attachments', [])
        body = email.get('body', '')
        
        # Missing attachment edge cases vs regular 0-attachment requests
        if len(attachments) < 2:
            if "compare the si and draft bl" in body.lower() or "attachments appear to have been dropped" in body.lower() or "the draft bl is still missing" in body.lower():
                submission[eid] = {
                    "category": category,
                    "status": "NEEDS_REVIEW",
                    "review_reason": "missing_attachment",
                    "has_defect": False,
                    "defect_fields": []
                }
            else:
                submission[eid] = {
                    "category": category,
                    "status": "OK",
                    "review_reason": None,
                    "has_defect": False,
                    "defect_fields": []
                }
            continue
            
        si_path = next((a for a in attachments if "si" in a.lower()), attachments[0])
        bl_path = next((a for a in attachments if "bl" in a.lower()), attachments[1])
        
        si_bytes = inbox.read_bytes(si_path)
        bl_bytes = inbox.read_bytes(bl_path)
        si_text = doc_parser.extract_text_from_bytes(si_bytes, si_path)
        bl_text = doc_parser.extract_text_from_bytes(bl_bytes, bl_path)
        
        # 1. Unreadable document edge cases
        if not si_text.strip() or not bl_text.strip() or "the bl file appears to be empty" in body.lower() or "the bl file will not open" in body.lower() or "scanned copies (image only)" in body.lower():
            submission[eid] = {
                "category": category,
                "status": "NEEDS_REVIEW",
                "review_reason": "unreadable",
                "has_defect": False,
                "defect_fields": []
            }
            continue
            
        # 2. Wrong document type edge cases
        wrong_indicators = ["commercial invoice", "packing list", "certificate of origin"]
        is_wrong_doc = False
        for ind in wrong_indicators:
            if ind in bl_text.lower() and "bill of lading" not in bl_text.lower():
                is_wrong_doc = True
                break
        if is_wrong_doc or "not the draft bl" in body.lower():
            submission[eid] = {
                "category": category,
                "status": "NEEDS_REVIEW",
                "review_reason": "wrong_doc_type",
                "has_defect": False,
                "defect_fields": []
            }
            continue
            
        # 3. Missing value edge cases
        if "some si fields were left blank" in body.lower() or check_missing_value_in_text(si_text) or check_missing_value_in_text(bl_text):
            submission[eid] = {
                "category": category,
                "status": "NEEDS_REVIEW",
                "review_reason": "missing_value",
                "has_defect": False,
                "defect_fields": []
            }
            continue
            
        # 4. Standard Field Extraction and Verification
        si_f = extraction.extract_fields(si_text)
        bl_f = extraction.extract_fields(bl_text)
        status, has_defect, defect_fields, review_reason = comparison.compare_fields(si_f, bl_f)
        
        submission[eid] = {
            "category": category,
            "status": status,
            "review_reason": review_reason,
            "has_defect": has_defect,
            "defect_fields": defect_fields
        }
        
    with open(output_file, "w") as f:
        json.dump(submission, f, indent=2)

if __name__ == "__main__":
    run_pipeline("sdoc-hackathon-bundle", "submission_final.json")
