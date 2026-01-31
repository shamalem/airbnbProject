import os
from io import StringIO

import pandas as pd
import requests
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# -----------------------------
# CONFIG (Environment Variables)
# -----------------------------
# Option A: DATA_URL = full URL (public OR SAS URL)
# Option B: BLOB_URL + SAS_TOKEN (token only)
DATA_URL_ENV = "DATA_URL"
BLOB_URL_ENV = "BLOB_URL"
SAS_TOKEN_ENV = "SAS_TOKEN"

# Local fallback
LOCAL_CSV_FILE = "data_sample.csv"

# Increase a bit in case Azure is slow
HTTP_TIMEOUT_SECS = 45


# -----------------------------
# HELPERS
# -----------------------------
def _download_text(url: str) -> str:
    r = requests.get(url, timeout=HTTP_TIMEOUT_SECS)
    r.raise_for_status()
    return r.text


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def _as_str(x):
    if x is None:
        return ""
    return str(x).strip()


def _as_int(x, default=0):
    try:
        if x is None:
            return default
        s = str(x).strip()
        if s == "" or s.lower() in {"nan", "none", "null"}:
            return default
        return int(float(s))
    except Exception:
        return default


def _as_float(x):
    try:
        if x is None:
            return None
        s = str(x).strip()
        if s == "" or s.lower() in {"nan", "none", "null"}:
            return None
        return float(s)
    except Exception:
        return None


def _safe_list(x):
    """
    CSV can store arrays as:
    - empty / NaN
    - "['a','b']"
    - "a; b"
    - "a, b"
    We convert to list[str].
    """
    if x is None:
        return []

    s = str(x).strip()
    if not s or s.lower() in {"nan", "none", "null", "[]"}:
        return []

    # strip brackets/quotes
    s2 = s.strip().strip("[]").replace("'", "").replace('"', "").strip()
    if not s2:
        return []

    # split
    if ";" in s2:
        parts = [p.strip() for p in s2.split(";")]
    elif "," in s2:
        parts = [p.strip() for p in s2.split(",")]
    else:
        parts = [s2]

    return [p for p in parts if p]


def _join_blob_and_token(blob_url: str, sas_token: str) -> str:
    """
    Build full URL:
      full = blob_url + "?" + sas_token
    Handles: token with/without leading '?', blob_url with/without existing query.
    """
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


def _read_csv_from_text(csv_text: str) -> pd.DataFrame:
    """
    Critical fix:
    - Force dtype=str so listing_id doesn't become float/scientific notation.
    """
    return pd.read_csv(StringIO(csv_text), dtype=str)


def _clean_id_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure IDs exist as clean strings (prevents "Listing not found")
    if "listing_id" in df.columns:
        df["listing_id"] = df["listing_id"].astype(str).str.strip()
        # treat blanks as missing
        df.loc[df["listing_id"].isin(["", "nan", "None", "null"]), "listing_id"] = None

    if "seller_id" in df.columns:
        df["seller_id"] = df["seller_id"].astype(str).str.strip()
        df.loc[df["seller_id"].isin(["", "nan", "None", "null"]), "seller_id"] = None

    return df


# -----------------------------
# UI TEXT
# -----------------------------
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
            f"There are listings rated higher than yours in {country}. "
            f"Below are actionable suggestions to help you improve."
        )
    }


def description_explain(score):
    s = _as_float(score)
    if s is None:
        return {"value": "N/A", "label": "Not available",
                "text": "Description score is not available for this listing."}

    # assumed 0..100
    if s >= 80:
        label = "High"
        text = "Your description is clear, well-structured, and informative."
    elif s >= 50:
        label = "Medium"
        text = "Your description is good, but it could be improved with clearer structure and more details."
    else:
        label = "Low"
        text = "Your description likely needs clearer structure and important missing details."

    return {"value": f"{s:.1f} / 100", "label": label, "text": text}


def centrality_explain(score):
    s = _as_float(score)
    if s is None:
        return {"value": "N/A", "label": "Not available",
                "text": "Centrality score is not available for this listing."}

    # assumed normalized 0..1
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


def build_suggestions(rec: dict):
    items = []

    add_amen = _safe_list(rec.get("suggest_add_amenities"))
    if add_amen:
        items.append({"title": "Add amenities", "list": add_amen})

    mention_amen = _safe_list(rec.get("suggest_mention_amenities"))
    if mention_amen:
        items.append({"title": "Mention amenities in your description", "list": mention_amen})

    pet = _safe_list(rec.get("suggest_pet_friendly"))
    if pet:
        items.append({"title": "Pet-friendly note", "list": pet})

    missing_phrases = _safe_list(rec.get("suggest_missing_phrases"))
    if missing_phrases:
        items.append({"title": "Add missing phrases", "list": missing_phrases})

    mention_landmarks = _safe_list(rec.get("suggest_mention_landmarks"))
    top_landmarks = _safe_list(rec.get("top_landmarks_to_mention"))
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


# -----------------------------
# DATA LOADING (CSV)
# -----------------------------
def load_records_from_csv():
    data_url = os.getenv(DATA_URL_ENV, "").strip()
    blob_url = os.getenv(BLOB_URL_ENV, "").strip()
    sas_token = os.getenv(SAS_TOKEN_ENV, "").strip()

    if data_url:
        url = data_url
        source = "data_url"
        csv_text = _download_text(url)
        df = _read_csv_from_text(csv_text)
    else:
        url2 = _join_blob_and_token(blob_url, sas_token)
        if url2:
            source = "blob_url+sas_token"
            csv_text = _download_text(url2)
            df = _read_csv_from_text(csv_text)
        else:
            if not os.path.exists(LOCAL_CSV_FILE):
                raise RuntimeError(
                    "Missing data source.\n"
                    f"- Set env var {DATA_URL_ENV} to full URL, OR\n"
                    f"- Set env vars {BLOB_URL_ENV} and {SAS_TOKEN_ENV}, OR\n"
                    f"- Put {LOCAL_CSV_FILE} next to app.py for local testing."
                )
            source = "local_file"
            df = pd.read_csv(LOCAL_CSV_FILE, dtype=str)

    df = _normalize_columns(df)
    df = df.where(pd.notnull(df), None)
    df = _clean_id_columns(df)

    if "listing_id" not in df.columns:
        raise RuntimeError(f"CSV missing required column 'listing_id'. Columns: {list(df.columns)}")

    # index by listing_id (string-safe)
    indexed = {}
    for rec in df.to_dict(orient="records"):
        listing_id = _as_str(rec.get("listing_id"))
        if listing_id:
            indexed[listing_id] = rec

    if not indexed:
        raise RuntimeError("Loaded CSV has 0 valid listing_id rows.")

    return indexed, source


records_by_listing, data_source = load_records_from_csv()


# -----------------------------
# ROUTES
# -----------------------------
@app.get("/")
def home():
    return render_template("index.html", result=None, error=None)


@app.post("/")
def analyze():
    seller_id = _as_str(request.form.get("seller_id"))
    listing_id = _as_str(request.form.get("listing_id"))

    if not listing_id:
        return render_template("index.html", result=None, error="Please enter a Listing ID.")

    rec = records_by_listing.get(listing_id)
    if not rec:
        return render_template(
            "index.html",
            result=None,
            error=f"Listing ID '{listing_id}' was not found in the sample data."
        )

    expected_seller = _as_str(rec.get("seller_id"))
    if seller_id and expected_seller and seller_id != expected_seller:
        return render_template(
            "index.html",
            result=None,
            error=f"Seller ID does not match this listing. Expected Seller ID: {expected_seller}"
        )

    country = _as_str(rec.get("country"))
    high_rated = _as_int(rec.get("high_rated"), default=0)

    result = {
        "seller_id": expected_seller,
        "listing_id": listing_id,
        "country": country,
        "banner": high_rated_banner(country, high_rated),

        "description": description_explain(rec.get("description_score")),
        "centrality": centrality_explain(rec.get("centrality_score_sel")),

        "suggestions": build_suggestions(rec),
    }

    return render_template("index.html", result=result, error=None)


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "records_loaded": len(records_by_listing),
        "data_source": data_source,
        # helpful sanity check: shows you that IDs are normal strings (not scientific notation)
        "sample_listing_ids": list(records_by_listing.keys())[:5],
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
