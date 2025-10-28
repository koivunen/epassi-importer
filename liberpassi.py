from base64 import b64encode
import os,requests,sys,time,json
from dotenv import load_dotenv

import pprint
from requests.auth import HTTPDigestAuth
from io import BytesIO
from datetime import datetime, time

load_dotenv()

s = requests.Session()
s.headers.update({"User-Agent":os.getenv("USERAGENT","epassi-importer/1.0 (+github.com/lamkoi/epassi-importer)")})

BASE="https://services.epassi.fi"


STATS_SITE="https://services.epassi.fi/site/statistics"
LOGIN = f"{BASE}/api/merchant/login/v1"

USERNAME=os.getenv("USERNAME")
PASSWORD=os.getenv("PASSWORD")

REDIRECT=f"{BASE}/redirect?l=fi"
LOGIN_TOKEN_COMB=f"{USERNAME}:{PASSWORD}"
LOGIN_TOKEN=b64encode(LOGIN_TOKEN_COMB.encode()).decode()

def fetch_statistics_xlsx(start_date: datetime | None = None, end_date: datetime | None = None, new_session=True) -> bytes:
    start_date=start_date or datetime.now()
    end_date=end_date or start_date
    STATISTICS_XSLX=f"{BASE}/site/statistics/export?end_date={end_date.strftime("%Y-%m-%d")}&start_date={start_date.strftime("%Y-%m-%d")}"

    if new_session:
        # main page for jsession
        frontpage=s.request("GET",BASE,timeout=30)
        frontpage.raise_for_status()
        #pprint.pprint(s.cookies.get_dict())
        
        # login token
        response=s.post(LOGIN,json={"login_token":LOGIN_TOKEN},headers={"Content-Type":"application/json"},timeout=30)
        try:
            response.raise_for_status()
        except Exception as e:
            print(f"Login failed: {e}")
            raise


        ret=response.json()
        #print(json.dumps(ret,indent='\t'))

        if ret["status_code"]!="OK":
            print("Login failed")
            sys.exit(1)

        token = ret["response"]["token"]
        if not token:
            print("No token received")
            sys.exit(1)

        auth_header = {"Authorization":f"{token}"}

        #pprint.pprint(s.cookies.get_dict())

        # required for mangling serverside session
        resp=s.get(REDIRECT,headers=auth_header,timeout=30)
        print(resp.url,resp.status_code)

    # statistics page

    statresp=s.get(STATISTICS_XSLX,timeout=60)
    statresp.raise_for_status()
    file_content = statresp.content
    
    if b'<html' in file_content[:256]:
        print("Got HTML, something went wrong")
        print(file_content.decode("utf-8",errors="replace"))
        sys.exit(1)
    return file_content