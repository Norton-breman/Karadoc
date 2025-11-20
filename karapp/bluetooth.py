from flask import Blueprint, render_template, request, redirect, url_for

bluetooth_bp = Blueprint("bluetooth", __name__)
_bt_manager = None

@bluetooth_bp.route('/bluetooth_settings')
def bluetooth_settings():
    devices = bluetooth_scan_devices()
    connected_devices = get_connected_bluetooth_devices()
    return render_template('bluetooth.html', devices=devices, connected_devices=connected_devices)


@bluetooth_bp.route('/bluetooth/pair', methods=['POST'])
def bluetooth_pair():
    mac_address = request.form.get('mac')
    if not mac_address:
        return redirect(url_for('bluetooth_settings'))

    success, message = bluetooth_pair_device(mac_address)

    devices = bluetooth_scan_devices()
    connected_devices = get_connected_bluetooth_devices()

    if success:
        return render_template('bluetooth.html', devices=devices, connected_devices=connected_devices, success=message)
    else:
        return render_template('bluetooth.html', devices=devices, connected_devices=connected_devices, error=message)


@bluetooth_bp.route('/bluetooth/connect', methods=['POST'])
def bluetooth_connect():
    mac_address = request.form.get('mac')
    if not mac_address:
        return redirect(url_for('bluetooth_settings'))

    success, message = bluetooth_connect_device(mac_address)

    devices = bluetooth_scan_devices()
    connected_devices = get_connected_bluetooth_devices()

    if success:
        return render_template('bluetooth.html', devices=devices, connected_devices=connected_devices, success=message)
    else:
        return render_template('bluetooth.html', devices=devices, connected_devices=connected_devices, error=message)


@bluetooth_bp.route('/bluetooth/disconnect', methods=['POST'])
def bluetooth_disconnect():
    mac_address = request.form.get('mac')
    if not mac_address:
        return redirect(url_for('bluetooth_settings'))

    success, message = bluetooth_disconnect_device(mac_address)

    devices = bluetooth_scan_devices()
    connected_devices = get_connected_bluetooth_devices()

    if success:
        return render_template('bluetooth.html', devices=devices, connected_devices=connected_devices, success=message)
    else:
        return render_template('bluetooth.html', devices=devices, connected_devices=connected_devices, error=message)


@bluetooth_bp.route('/bluetooth/remove', methods=['POST'])
def bluetooth_remove():
    mac_address = request.form.get('mac')
    if not mac_address:
        return redirect(url_for('bluetooth_settings'))

    success, message = bluetooth_remove_device(mac_address)

    devices = bluetooth_scan_devices()
    connected_devices = get_connected_bluetooth_devices()

    if success:
        return render_template('bluetooth.html', devices=devices, connected_devices=connected_devices, success=message)
    else:
        return render_template('bluetooth.html', devices=devices, connected_devices=connected_devices, error=message)


def _get_bt_manager():
    """Récupère ou crée l'instance du gestionnaire Bluetooth"""
    global _bt_manager
    if _bt_manager is None:
        try:
            from karapp.bluetooth_manager import BluetoothManager
            _bt_manager = BluetoothManager()
        except Exception as e:
            print(f"Erreur lors de l'initialisation du gestionnaire Bluetooth: {e}")
            _bt_manager = None
    return _bt_manager

def bluetooth_scan_devices():
    """Scanne les périphériques Bluetooth disponibles"""
    manager = _get_bt_manager()
    if manager is None:
        return []
    return manager.scan_devices(duration=5)

def bluetooth_pair_device(mac_address):
    """Appaire un périphérique Bluetooth"""
    manager = _get_bt_manager()
    if manager is None:
        return False, "Gestionnaire Bluetooth non disponible"
    return manager.pair_device(mac_address)

def bluetooth_connect_device(mac_address):
    """Se connecte à un périphérique Bluetooth"""
    manager = _get_bt_manager()
    if manager is None:
        return False, "Gestionnaire Bluetooth non disponible"
    return manager.connect_device(mac_address)

def bluetooth_disconnect_device(mac_address):
    """Se déconnecte d'un périphérique Bluetooth"""
    manager = _get_bt_manager()
    if manager is None:
        return False, "Gestionnaire Bluetooth non disponible"
    return manager.disconnect_device(mac_address)

def get_connected_bluetooth_devices():
    """Récupère la liste des appareils Bluetooth connectés"""
    manager = _get_bt_manager()
    if manager is None:
        return []
    return manager.get_connected_devices()

def bluetooth_remove_device(mac_address):
    """Supprime un périphérique Bluetooth (unpair)"""
    manager = _get_bt_manager()
    if manager is None:
        return False, "Gestionnaire Bluetooth non disponible"
    return manager.remove_device(mac_address)