from base64 import b64encode
import os,requests,sys,time,json
from dotenv import load_dotenv

import pprint
from requests.auth import HTTPDigestAuth
from io import BytesIO
from datetime import date, datetime, time, timedelta
from openpyxl import load_workbook
from utils import bucket_timestamps, count_rows_in_window_per_day, extract_timestamps
from liberpassi import fetch_statistics_xlsx

if os.getenv("SENTRY_DSN"):
    # SECURITY: may leak env params/URLS (password!)
    import sentry_sdk

    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        send_default_pii=False
    )
load_dotenv()

PING_URL = os.getenv("PING_URL")

POSTGREST_BASE = os.getenv("POSTGREST_BASE", "https://dfapi.tt.utu.fi")
POSTGREST_TABLE = os.getenv("POSTGREST_TABLE", "site_diner_counts")
POSTGREST_TABLE_BUCKETS = os.getenv("POSTGREST_TABLE_BUCKETS", "site_diners_5m_buckets")
AUTH_BEARER = os.getenv("AUTH_BEARER")
SITEID = int(os.getenv("SITEID", "-1"))

def post_to_postgrest(payload: dict) -> requests.Response:
    url = f"{POSTGREST_BASE}/{POSTGREST_TABLE}?on_conflict=siteid,date"
    headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Prefer": "resolution=merge-duplicates",
    }
    if AUTH_BEARER:
        headers["Authorization"] = f"Bearer {AUTH_BEARER}"

    resp = requests.post(url, json=[payload], headers=headers, timeout=10)
    try:
        resp.raise_for_status()
    except Exception as e:
        print(f"Failed to post to PostgREST: {e}")
        print(f"Response: {resp.status_code} {resp.text}")
        raise
    return resp

def post_to_postgrest_buckets(payload: list) -> requests.Response:
    url = f"{POSTGREST_BASE}/{POSTGREST_TABLE_BUCKETS}?on_conflict=bucket_time"
    headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Prefer": "resolution=merge-duplicates",
    }
    if AUTH_BEARER:
        headers["Authorization"] = f"Bearer {AUTH_BEARER}"

    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    try:
        resp.raise_for_status()
    except Exception as e:
        print(f"Failed to post to PostgREST: {e}")
        print(f"Response: {resp.status_code} {resp.text}")
        raise
    return resp

#post_to_postgrest({"siteid":2,"date":"2025-10-11","count":42})
#post_to_postgrest({"siteid":2,"date":"2025-10-11","count":43})



def post_realtime_state(file_content: bytes):
    result = count_rows_in_window_per_day(file_content)
    for d,c in result.items():
        print(f"{d}: {c}")
        resp = post_to_postgrest({"siteid": SITEID, "date": str(d), "count": c})
        


def post_bucketed_state(file_content: bytes):    
    byte_stream = BytesIO(file_content)
    workbook = load_workbook(byte_stream)
    sheet = workbook['Sheet1']
    timestamps = extract_timestamps(sheet)
    bucketed_timestamps = bucket_timestamps(timestamps)
    payload = []
    # NOTE: there might likely be refunds an hour into the past at least so just dump the whole day every time (For now)
    for timestamp, count in bucketed_timestamps.items():
        entry = {
            "bucket_time": str(timestamp),
            "entry_count": count,
            "siteid": SITEID
        }
        payload.append(entry)
    resp = post_to_postgrest_buckets(payload)

RET=0



def run(target_date: datetime, new_session=True):
    global RET
    file_content = fetch_statistics_xlsx(start_date=target_date, end_date=target_date, new_session=new_session)

    try:
        post_realtime_state(file_content)
    except Exception as e:
        print(f"Failed to post realtime state: {e}")

        RET=1

    try:
        post_bucketed_state(file_content)
    except Exception as e:
        print(f"Failed to post bucketed state: {e}")
        RET=2

run(datetime.now())



def run_range(start_date,end_date):

    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5: 
            run(current_date,False)
        current_date += timedelta(days=1)

if False:
    run_range(datetime(2099, 1, 1),datetime.now())

if PING_URL:
    try:
        pingresp = requests.get(PING_URL, timeout=10)
        print(f"Pinged {PING_URL}: {pingresp.status_code}")
    except Exception as e:
        print(f"Failed to ping {PING_URL}: {e}")


if RET:
    sys.exit(RET)