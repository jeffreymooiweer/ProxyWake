"""Tests for device dependency ordering and cycle detection."""

import pytest

from models import Device, db
from services.dependency_service import (
    DependencyCycleError,
    get_wake_order,
    set_device_dependencies,
)


def _device(name, domain, ip_suffix):
    device = Device(
        name=name,
        domain=domain,
        ip=f'192.168.1.{ip_suffix}',
        mac=f'AA:BB:CC:DD:EE:{ip_suffix:02X}',
    )
    db.session.add(device)
    db.session.commit()
    return device


def test_wake_order_respects_dependencies(client):
    router = _device('Router', 'router.test.local', 10)
    nas = _device('NAS', 'nas.test.local', 20)
    pc = _device('PC', 'pc.test.local', 30)

    set_device_dependencies(nas.id, [router.id])
    set_device_dependencies(pc.id, [nas.id])

    order = get_wake_order(pc.id)
    assert [device.id for device in order] == [router.id, nas.id, pc.id]


def test_self_dependency_rejected(client):
    device = _device('Solo', 'solo.test.local', 40)
    with pytest.raises(DependencyCycleError):
        set_device_dependencies(device.id, [device.id])


def test_circular_dependency_rejected(client):
    a = _device('A', 'a.test.local', 50)
    b = _device('B', 'b.test.local', 51)
    set_device_dependencies(a.id, [b.id])
    with pytest.raises(DependencyCycleError):
        set_device_dependencies(b.id, [a.id])
