import os
import json
from pathlib import Path

import requests
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# ---------------------------------
# Config
# ---------------------------------
LOCAL_DATA_FILE = "data_sample.json"          # local dev fallback

# Option A: set a full URL in Render (includes ?sp=...&sig=...)
ENV_SAS_URL = "DATA_SAMPLE_SAS_URL"

# Option B: set base + token in Render (recommended)
ENV_BLOB_URL = "BLOB_URL"     # e.g. https://lab94290.blob.core.windows.net/submissions/Aml_Sham_Nada/data_sample.json
ENV_SAS_TOKEN = "SAS_TOKEN"   # e.g. sp=...&sig=...

HTTP_TIMEOUT_SECS = 45


# ---------------------------------
# Download / parse
# ---------------------------------
def _download(url: str) -> str:
    r = requests.get(url, timeout=HTTP_TIMEOUT_SECS)
    r.raise_for_status()
    # force utf-8 decoding (fixes weird characters)
    r.encoding = "utf-8"
    return r.text


def _parse_json_content(text: str):
    """
    Supports:
      1) JSON array: [ {...}, {...} ]
      2) JSON object: {...} or {"data":[...]}
      3) JSONL: one JSON object per line
    """
    text = (text or "").strip()
    if not text:
        return []

    # Try normal JSON first
    try:
        obj = json.loads(text)
        if isinstance(obj, list):
            return obj
        if isinstance(obj, dict):
            if "data" in obj and isinstance(obj["data"], list):
                return obj["data"]
            return [obj]
    except Exception:
        pass

    # Fallback: JSONL
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        out.append(json.loads(line))
    return out


def _join_blob_and_token(blob_url: str, sas_token: str) -> str:
    blob_url = (blob_url or "").strip()
    sas_token = (sas_token or "").strip()

    if not blob_url:
        return ""
    if not sas_token:
        return blob_url

    if sas_token.startswith("?"):
        sas_token = sas_token[1:]

    if "?" in blob_url:
        if blob_url.endswith("?") or blob_url.endswith("&"):
            return blob_url + sas_token
        return blob_url + "&" + sas_token

    return blob_url + "?" + sas_token


def load_records():
    """
    Returns dict: listing_id(str) -> record(dict)

    Priority:
      1) DATA_SAMPLE_SAS_URL (full url)
      2) BLOB_URL + SAS_TOKEN
      3) local json file
    """
    full_url = os.getenv(ENV_SAS_URL, "").strip()

    if not full_url:
        blob_url = os.getenv(ENV_BLOB_URL, "").strip()
        sas_token = os.getenv(ENV_SAS_TOKEN, "").strip()
        full_url = _join_blob_and_token(blob_url, sas_token)

    if full_url:
        raw_text = _download(full_url)
        records = _parse_json_content(raw_text)
        source = "azure_url"
    else:
        p = Path(LOCAL_DATA_FILE)
        if not p.exists():
            raise RuntimeError(
                "No data source found.\n"
                f"- Set env var {ENV_SAS_URL} (full URL), OR\n"
                f"- Set env vars {ENV_BLOB_URL} and {ENV_SAS_TOKEN}, OR\n"
                f"- Put {LOCAL_DATA_FILE} next to app.py for local testing."
            )
        raw_text = p.read_text(encoding="utf-8")
        records = _parse_json_content(raw_text)
        source = "local_file"

    indexed = {}
    for rec in records:
        if not isinstance(rec, dict):
            continue
        listing_id = str(rec.get("listing_id", "")).strip()
        if listing_id:
            indexed[listing_id] = rec

    if not indexed:
        raise RuntimeError("Loaded data is empty or missing listing_id fields.")

    return indexed, source


records_by_listing, data_source = load_records()


# ---------------------------------
# Helpers
# ---------------------------------
def as_str(x):
    return "" if x is None else str(x)

def as_float(x):
    try:
        if x is None or x == "":
            return None
        return float(x)
    except Exception:
        return None

def safe_list(v):
    """
    Normalize to list[str].
    If Spark wrote arrays, JSON should keep them as lists.
    """
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x) for x in v if str(x).strip()]
    s = str(v).strip()
    return [s] if s else []


def high_rated_banner(country: str, high_rated: int):
    country = country or "your country"
    if high_rated == 1:
        return {
            "type": "good",
            "title": "✅ Great news!",
            "message": f"Your Airbnb is considered one of the top high-rated listings in {country}."
        }
    return {
        "type": "info",
        "title": "ℹ️ Insight",
        "message": (
            f"There are Airbnb listings rated higher than yours in {country}. "
            f"We suggest several improvements below to help you improve."
        )
    }


def centrality_explain(score):
    s = as_float(score)
    if s is None:
        return {"value": "N/A", "label": "Not available",
                "text": "Centrality score is not available for this listing."}

    if s >= 0.70:
        label = "High"
        text = "Your listing is in a very central area."
    elif s >= 0.45:
        label = "Medium"
        text = "Your listing is moderately central."
    else:
        label = "Low"
        text = "Your listing is less central — mentioning nearby landmarks can help boost appeal."

    return {"value": f"{s:.3f}", "label": label, "text": text}


def description_explain(score):
    s = as_float(score)
    if s is None:
        return {"value": "N/A", "label": "Not available",
                "text": "Description score is not available for this listing."}

    # assumed 0..100
    if s >= 80:
        label = "High"
        text = "Your description is clear, well-structured, and informative."
    elif s >= 50:
        label = "Medium"
        text = "Your description is good, but it can be improved with clearer structure or missing details."
    else:
        label = "Low"
        text = "Your description could benefit from clearer structure and additional important details."

    return {"value": f"{s:.1f}%", "label": label, "text": text}


def build_suggestions(rec: dict):
    items = []

    add_amen = safe_list(rec.get("suggest_add_amenities"))
    if add_amen:
        items.append({"title": "Add amenities", "list": add_amen})

    mention_amen = safe_list(rec.get("suggest_mention_amenities"))
    if mention_amen:
        items.append({"title": "Mention amenities in your description", "list": mention_amen})

    pet = safe_list(rec.get("suggest_pet_friendly"))
    if pet:
        items.append({"title": "Pet-friendly note", "list": pet})

    missing_phrases = safe_list(rec.get("suggest_missing_phrases"))
    if missing_phrases:
        items.append({"title": "Add missing phrases", "list": missing_phrases})

    mention_landmarks = safe_list(rec.get("suggest_mention_landmarks"))
    top_landmarks = safe_list(rec.get("top_landmarks_to_mention"))
    if mention_landmarks or top_landmarks:
        out = []
        out += mention_landmarks
        if top_landmarks:
            out.append("Top landmarks to mention:")
            out += top_landmarks
        items.append({"title": "Improve location appeal (landmarks)", "list": out})

    if not items:
        items.append({
            "title": "No major issues detected",
            "list": ["Your listing looks good! Consider small refinements to stay competitive."]
        })

    return items


# ---------------------------------
# Routes
# ---------------------------------
@app.get("/")
def home():
    return render_template("index.html", result=None, error=None)


@app.post("/")
def analyze():
    seller_id = (request.form.get("seller_id") or "").strip()
    listing_id = (request.form.get("listing_id") or "").strip()

    if not listing_id:
        return render_template("index.html", result=None, error="Please enter a Listing ID.")

    rec = records_by_listing.get(listing_id)
    if not rec:
        return render_template(
            "index.html",
            result=None,
            error=f"Listing ID '{listing_id}' was not found in the sample file."
        )

    expected_seller = as_str(rec.get("seller_id")).strip()
    if seller_id and expected_seller and seller_id != expected_seller:
        return render_template(
            "index.html",
            result=None,
            error=f"Seller ID does not match this listing. Expected Seller ID: {expected_seller}"
        )

    country = as_str(rec.get("country")).strip()
    high_rated = int(rec.get("high_rated") or 0)

    result = {
        "seller_id": expected_seller,
        "listing_id": listing_id,
        "country": country,
        "banner": high_rated_banner(country, high_rated),
        "description": description_explain(rec.get("description_score")),
        "centrality": centrality_explain(rec.get("centrality_score_sel")),
        "suggestions": build_suggestions(rec)
    }

    return render_template("index.html", result=result, error=None)


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "records_loaded": len(records_by_listing),
        "data_source": data_source,
        "sample_listing_ids": list(records_by_listing.keys())[:5],
        "expected_envs": [ENV_SAS_URL, ENV_BLOB_URL, ENV_SAS_TOKEN],
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
