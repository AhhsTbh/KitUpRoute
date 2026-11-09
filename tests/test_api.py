import os
os.environ['KITUP_ADMIN_TOKEN']='test-secret'
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_status():
 r=client.get('/api/status'); assert r.status_code==200;assert r.json()['game_routing_verified'] is False
def test_regions():
 r=client.get('/api/regions');assert r.status_code==200;assert len(r.json())==8

def test_auth():
 assert client.post('/api/region',json={'region':'uk'}).status_code==401
 assert client.post('/api/region',json={'region':'bogus'},headers={'Authorization':'Bearer test-secret'}).status_code==400
