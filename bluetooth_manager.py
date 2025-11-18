"""
Gestionnaire Bluetooth utilisant pydbus pour interagir avec BlueZ via D-Bus
"""
import time
from pydbus import SystemBus


class BluetoothManager:
    """Gestionnaire Bluetooth utilisant D-Bus"""

    BLUEZ_SERVICE = 'org.bluez'
    ADAPTER_INTERFACE = 'org.bluez.Adapter1'
    DEVICE_INTERFACE = 'org.bluez.Device1'

    def __init__(self):
        """Initialise le gestionnaire Bluetooth"""
        self.bus = SystemBus()
        self.adapter_path = self._get_adapter_path()
        self.adapter = None
        if self.adapter_path:
            self.adapter = self.bus.get(self.BLUEZ_SERVICE, self.adapter_path)

    def _get_adapter_path(self):
        """Récupère le chemin D-Bus du premier adaptateur Bluetooth"""
        try:
            manager = self.bus.get(self.BLUEZ_SERVICE, '/')
            managed_objects = manager.GetManagedObjects()

            for path, interfaces in managed_objects.items():
                if self.ADAPTER_INTERFACE in interfaces:
                    return path
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération de l'adaptateur: {e}")
            return None

    def _get_device_objects(self):
        """Récupère tous les objets device de BlueZ"""
        try:
            manager = self.bus.get(self.BLUEZ_SERVICE, '/')
            return manager.GetManagedObjects()
        except Exception as e:
            print(f"Erreur lors de la récupération des devices: {e}")
            return {}

    def scan_devices(self, duration=5):
        """
        Scanne les périphériques Bluetooth disponibles

        Args:
            duration: Durée du scan en secondes (défaut: 5)

        Returns:
            Liste de dictionnaires contenant les infos des périphériques
        """
        if not self.adapter:
            return []

        devices = []

        try:
            # Démarrer le scan
            self.adapter.StartDiscovery()
            time.sleep(duration)
            self.adapter.StopDiscovery()

            # Récupérer les devices découverts
            managed_objects = self._get_device_objects()

            for path, interfaces in managed_objects.items():
                if self.DEVICE_INTERFACE not in interfaces:
                    continue

                device_props = interfaces[self.DEVICE_INTERFACE]

                # Filtrer les devices qui appartiennent à notre adaptateur
                if not path.startswith(self.adapter_path):
                    continue

                device_info = {
                    'mac': device_props.get('Address', 'Unknown'),
                    'name': device_props.get('Name', device_props.get('Alias', 'Unknown')),
                    'connected': device_props.get('Connected', False),
                    'paired': device_props.get('Paired', False),
                    'trusted': device_props.get('Trusted', False),
                    'rssi': device_props.get('RSSI', None),
                    'path': path,
                    'device_type': 'unknown'
                }

                # Déterminer le type de périphérique
                uuids = device_props.get('UUIDs', [])
                if any('110b' in uuid.lower() for uuid in uuids):  # A2DP
                    device_info['device_type'] = 'audio'
                elif any('1124' in uuid.lower() for uuid in uuids):  # HID
                    device_info['device_type'] = 'input'

                devices.append(device_info)

            return devices

        except Exception as e:
            print(f"Erreur lors du scan Bluetooth: {e}")
            # Essayer d'arrêter le scan en cas d'erreur
            try:
                self.adapter.StopDiscovery()
            except:
                pass
            return []

    def pair_device(self, mac_address):
        """
        Appaire un périphérique Bluetooth

        Args:
            mac_address: Adresse MAC du périphérique

        Returns:
            Tuple (success: bool, message: str)
        """
        if not self.adapter:
            return False, "Adaptateur Bluetooth non trouvé"

        try:
            # Trouver le device
            device_path = self._find_device_path(mac_address)
            if not device_path:
                return False, f"Périphérique {mac_address} non trouvé"

            device = self.bus.get(self.BLUEZ_SERVICE, device_path)

            # Vérifier si déjà appairé
            if device.Paired:
                # Faire confiance au périphérique
                device.Trusted = True
                return True, "Périphérique déjà appairé"

            # Appairer
            device.Pair()

            # Faire confiance au périphérique
            device.Trusted = True

            return True, "Appairage réussi"

        except Exception as e:
            return False, f"Erreur d'appairage: {str(e)}"

    def connect_device(self, mac_address):
        """
        Se connecte à un périphérique Bluetooth

        Args:
            mac_address: Adresse MAC du périphérique

        Returns:
            Tuple (success: bool, message: str)
        """
        if not self.adapter:
            return False, "Adaptateur Bluetooth non trouvé"

        try:
            device_path = self._find_device_path(mac_address)
            if not device_path:
                return False, f"Périphérique {mac_address} non trouvé"

            device = self.bus.get(self.BLUEZ_SERVICE, device_path)

            # Vérifier si déjà connecté
            if device.Connected:
                return True, "Périphérique déjà connecté"

            # Se connecter
            device.Connect()

            return True, "Connexion réussie"

        except Exception as e:
            return False, f"Erreur de connexion: {str(e)}"

    def disconnect_device(self, mac_address):
        """
        Se déconnecte d'un périphérique Bluetooth

        Args:
            mac_address: Adresse MAC du périphérique

        Returns:
            Tuple (success: bool, message: str)
        """
        if not self.adapter:
            return False, "Adaptateur Bluetooth non trouvé"

        try:
            device_path = self._find_device_path(mac_address)
            if not device_path:
                return False, f"Périphérique {mac_address} non trouvé"

            device = self.bus.get(self.BLUEZ_SERVICE, device_path)

            # Se déconnecter
            device.Disconnect()

            return True, "Déconnexion réussie"

        except Exception as e:
            return False, f"Erreur de déconnexion: {str(e)}"

    def remove_device(self, mac_address):
        """
        Supprime un périphérique Bluetooth (unpair)

        Args:
            mac_address: Adresse MAC du périphérique

        Returns:
            Tuple (success: bool, message: str)
        """
        if not self.adapter:
            return False, "Adaptateur Bluetooth non trouvé"

        try:
            device_path = self._find_device_path(mac_address)
            if not device_path:
                return False, f"Périphérique {mac_address} non trouvé"

            # Supprimer le périphérique via l'adaptateur
            self.adapter.RemoveDevice(device_path)

            return True, "Périphérique supprimé"

        except Exception as e:
            return False, f"Erreur de suppression: {str(e)}"

    def get_connected_devices(self):
        """
        Récupère la liste des périphériques connectés

        Returns:
            Liste de dictionnaires contenant les infos des périphériques connectés
        """
        if not self.adapter:
            return []

        connected_devices = []

        try:
            managed_objects = self._get_device_objects()

            for path, interfaces in managed_objects.items():
                if self.DEVICE_INTERFACE not in interfaces:
                    continue

                device_props = interfaces[self.DEVICE_INTERFACE]

                # Filtrer les devices connectés
                if not device_props.get('Connected', False):
                    continue

                # Filtrer les devices qui appartiennent à notre adaptateur
                if not path.startswith(self.adapter_path):
                    continue

                device_info = {
                    'mac': device_props.get('Address', 'Unknown'),
                    'name': device_props.get('Name', device_props.get('Alias', 'Unknown')),
                    'device_type': 'unknown'
                }

                # Déterminer le type de périphérique
                uuids = device_props.get('UUIDs', [])
                if any('110b' in uuid.lower() for uuid in uuids):  # A2DP
                    device_info['device_type'] = 'audio'
                elif any('1124' in uuid.lower() for uuid in uuids):  # HID
                    device_info['device_type'] = 'input'

                connected_devices.append(device_info)

            return connected_devices

        except Exception as e:
            print(f"Erreur lors de la récupération des devices connectés: {e}")
            return []

    def _find_device_path(self, mac_address):
        """
        Trouve le chemin D-Bus d'un périphérique par son adresse MAC

        Args:
            mac_address: Adresse MAC du périphérique

        Returns:
            Chemin D-Bus du périphérique ou None
        """
        try:
            managed_objects = self._get_device_objects()

            for path, interfaces in managed_objects.items():
                if self.DEVICE_INTERFACE not in interfaces:
                    continue

                device_props = interfaces[self.DEVICE_INTERFACE]
                if device_props.get('Address', '').upper() == mac_address.upper():
                    return path

            return None

        except Exception as e:
            print(f"Erreur lors de la recherche du device: {e}")
            return None
