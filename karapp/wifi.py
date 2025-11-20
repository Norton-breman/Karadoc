from flask import Blueprint, render_template, request, redirect, url_for
import nmcli
import subprocess

connection_bp = Blueprint("wifi", __name__)

@connection_bp.route("/wifi_settings")
def wifi_settings():
    networks = scan_wifi_networks()
    current_wifi = get_current_wifi()
    return render_template('wifi.html', networks=networks, current_wifi=current_wifi)

@connection_bp.route('/wifi/connect', methods=['POST'])
def wifi_connect():
    ssid = request.form.get('ssid')
    password = request.form.get('password')

    if not ssid:
        return redirect(url_for('wifi.wifi_settings'))

    success, message = connect_to_wifi(ssid, password)

    if success:
        return redirect(url_for('wifi.wifi_settings'))
    else:
        networks = scan_wifi_networks()
        current_wifi = get_current_wifi()
        return render_template('wifi.html', networks=networks, current_wifi=current_wifi, error=message)

def scan_wifi_networks():
    """Scanne les réseaux WiFi disponibles (Linux/Raspberry Pi)"""
    nmcli.disable_use_sudo()
    ssids = nmcli.device.wifi()
    best_wifi = {}
    for ap in ssids:
        ssid = ap.ssid
        if ssid:
            best_wifi[ssid] = max([best_wifi.get(ssid, ap), ap], key=lambda x: x.signal)
    networks = []
    for wifi in best_wifi.values():
        networks.append({
            'ssid': wifi.ssid,
            'bssid': wifi.bssid,
            'signal': wifi.signal,
            'security': wifi.security,
            'secured': wifi.security != '' and wifi.security != 'Open'
        })
    return sorted(networks, key=lambda x: int(x['signal']), reverse=True)

def connect_to_wifi(ssid, password=None):
    """Se connecte à un réseau WiFi (Linux/Raspberry Pi)"""
    try:
        # Essayer avec nmcli d'abord
        if password:
            cmd = ['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password]
        else:
            cmd = ['nmcli', 'dev', 'wifi', 'connect', ssid]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            return True, f"Connecté au réseau {ssid}"
        else:
            return False, f"Erreur: {result.stderr.strip()}"

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, "NetworkManager non disponible"

def get_current_wifi():
    """Récupère le réseau WiFi actuellement connecté"""
    try:
        nmcli.disable_use_sudo()
        ssids = nmcli.device.wifi()
        for ssid in ssids:
            if ssid.in_use:
                return ssid.ssid
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return None
