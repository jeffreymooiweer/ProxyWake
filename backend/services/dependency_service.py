from models import Device, DeviceDependency, db


class DependencyCycleError(Exception):
    pass


def get_dependencies(device_id):
    rows = DeviceDependency.query.filter_by(device_id=device_id).all()
    return [row.depends_on_device_id for row in rows]


def get_dependency_devices(device_id):
    ids = get_dependencies(device_id)
    if not ids:
        return []
    return Device.query.filter(Device.id.in_(ids)).order_by(Device.name.asc()).all()


def get_wake_order(device_id):
    """Return devices to wake in order: dependencies first, target device last."""
    order = []
    visited = set()

    def visit(current_id):
        if current_id in visited:
            return
        visited.add(current_id)
        for dep_id in get_dependencies(current_id):
            visit(dep_id)
        device = Device.query.get(current_id)
        if device:
            order.append(device)

    visit(device_id)
    return order


def would_create_cycle(device_id, depends_on_id):
    if device_id == depends_on_id:
        return True
    order = get_wake_order(depends_on_id)
    return any(device.id == device_id for device in order)


def set_device_dependencies(device_id, depends_on_ids):
    cleaned = []
    for dep_id in depends_on_ids or []:
        dep_id = int(dep_id)
        if dep_id == device_id:
            raise DependencyCycleError('A device cannot depend on itself.')
        if would_create_cycle(device_id, dep_id):
            raise DependencyCycleError('Circular dependency detected.')
        if dep_id not in cleaned:
            cleaned.append(dep_id)

    DeviceDependency.query.filter_by(device_id=device_id).delete()
    for dep_id in cleaned:
        db.session.add(DeviceDependency(device_id=device_id, depends_on_device_id=dep_id))
    db.session.commit()
    return cleaned


def dependencies_to_dict(device_id):
    devices = get_dependency_devices(device_id)
    return [{'id': device.id, 'name': device.name or device.domain, 'domain': device.domain} for device in devices]
