import socket
import threading

import pytest
from conftest import NetworkBlocked


def test_guard_blocks_remote_host():
    """Broken case: without the guard this connect would try the network.
    192.0.2.1 is a TEST-NET documentation address (RFC 5737), so no real host is involved."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        with pytest.raises(NetworkBlocked):
            s.connect(("192.0.2.1", 80))
    finally:
        s.close()


def test_guard_allows_loopback():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]
    t = threading.Thread(target=lambda: server.accept()[0].close())
    t.start()
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.connect(("127.0.0.1", port))
    c.close()
    t.join(timeout=5)
    server.close()
