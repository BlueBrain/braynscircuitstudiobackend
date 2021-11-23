from bcsb.asgi import application_mapping


def test_application_mapping():
    assert "http" in application_mapping
    assert "websocket" in application_mapping
