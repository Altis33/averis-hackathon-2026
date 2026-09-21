import json
import os

def llm_extract_fields(text, provider="openai"):
    """
    Use an LLM (GPT or Claude) to extract the 7 shipping fields from document text.
    Falls back to None values if the API call fails.
    """
    prompt = f"""Extract the following 7 fields from this shipping document text. 
Return ONLY a valid JSON object with these exact keys. Use null for any field you cannot find.

Keys:
- "shipper": The shipper / exporter company name (string or null)
- "consignee": The consignee company name (string or null)  
- "notify_party": The notify party company name (string or null)
- "port_of_loading": The port of loading / load port (string or null)
- "port_of_discharge": The port of discharge / discharge port (string or null)
- "container_count": The number of containers (integer or null)
- "gross_weight_kg": The gross weight in KG (integer or null)

Document text:
\"\"\"
{text[:3000]}
\"\"\"

Return ONLY the JSON object, no markdown, no explanation."""

    try:
        if provider == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=500,
            )
            raw = response.choices[0].message.content.strip()
        elif provider == "anthropic":
            from anthropic import Anthropic
            client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
        else:
            return None

        # Clean markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            raw = raw.rsplit("```", 1)[0]

        fields = json.loads(raw)
        # Ensure integer types
        if fields.get("container_count") is not None:
            fields["container_count"] = int(fields["container_count"])
        if fields.get("gross_weight_kg") is not None:
            fields["gross_weight_kg"] = int(fields["gross_weight_kg"])
        return fields

    except Exception as e:
        print(f"LLM extraction failed ({provider}): {e}")
        return None
