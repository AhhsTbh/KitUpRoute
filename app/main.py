"""KitUp Route control plane. No VPN or game-routing claims are made."""
import os
import secrets
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE = Path(__file__).resolve().parent.parent
DB = Path(os.getenv('KITUP_DB', str(BASE / 'kitup.db')))
TOKEN = os.getenv('KITUP_ADMIN_TOKEN', '')
REGIONS = {
 'auto': ('Smart Auto', 'UTC'), 'us-west': ('US West · Los Angeles', 'America/Los_Angeles'),
 'us-central': ('US Central · Dallas', 'America/Chicago'), 'us-east': ('US East · Virginia', 'America/New_York'),
 'uk': ('United Kingdom · London', 'Europe/London'), 'eu': ('Europe · Frankfurt', 'Europe/Berlin'),
 'jp': ('Asia · Tokyo', 'Asia/Tokyo'), 'au': ('Oceania · Sydney', 'Australia/Sydney')
}
app = FastAPI(title='KitUp Route', version='0.1.0')
app.mount('/static', StaticFiles(directory=str(BASE / 'static')), name='static')

def db():
 DB.parent.mkdir(parents=True, exist_ok=True)
 c=sqlite3.connect(DB)
 c.execute('CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY CHECK(id=1), region TEXT NOT NULL)')
 c.execute("INSERT OR IGNORE INTO settings(id,region) VALUES (1,'auto')")
 c.commit()
 return c

class Selection(BaseModel):
 region: str

@app.get('/')
def home(): return FileResponse(BASE/'static'/'index.html')

@app.get('/api/status')
def status():
 with db() as c: region=c.execute('SELECT region FROM settings WHERE id=1').fetchone()[0]
 return {'product':'KitUp Route','region':region,'dns_service':'separate-process','relay_connected':False,
         'game_routing_verified':False,'message':'DNS resolution does not route gameplay traffic.'}

@app.get('/api/regions')
def regions():
 now=datetime.now(timezone.utc)
 return [{'id':key,'name':name,'local_time':now.astimezone(ZoneInfo(tz)).strftime('%I:%M %p'),
          'latency_ms':None,'relay_available':False} for key,(name,tz) in REGIONS.items()]

@app.post('/api/region')
def set_region(value:Selection, authorization:str|None=Header(default=None)):
 if not TOKEN: raise HTTPException(503,'Set KITUP_ADMIN_TOKEN to enable changes')
 if not authorization or not secrets.compare_digest(authorization, f'Bearer {TOKEN}'):
  raise HTTPException(401,'Invalid admin token')
 if value.region not in REGIONS: raise HTTPException(400,'Unknown region')
 with db() as c: c.execute('UPDATE settings SET region=? WHERE id=1',(value.region,)); c.commit()
 return {'selected':value.region,'routing_changed':False,'message':'Saved preference only; no relay configured.'}

@app.get('/healthz')
def health(): return {'ok':True}
