import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'

def test_predict_positive():
    r = client.post('/predict', json={'text': 'I love this great product'})
    assert r.status_code == 200
    assert r.json()['label'] == 'positive'

def test_predict_negative():
    r = client.post('/predict', json={'text': 'This is the worst and I hate it'})
    assert r.status_code == 200
    assert r.json()['label'] == 'negative'

def test_predict_not_bad_positive():
    r = client.post('/predict', json={'text': 'The movie is not bad'})
    assert r.status_code == 200
    assert r.json()['label'] == 'positive'

def test_predict_not_good_negative():
    r = client.post('/predict', json={'text': 'The product is not good'})
    assert r.status_code == 200
    assert r.json()['label'] == 'negative'

def test_predict_neutral():
    r = client.post('/predict', json={'text': 'This is a table'})
    assert r.status_code == 200
    assert r.json()['label'] == 'neutral'

def test_validation_error_missing_text():
    r = client.post('/predict', json={})
    assert r.status_code == 422
