import threading
import time
import webview
from werkzeug.serving import make_server
from dotenv import load_dotenv

# Importer l'application Flask
from app import app

load_dotenv()

class ServerThread(threading.Thread):
    """Thread pour exécuter le serveur Flask en arrière-plan"""
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.server = make_server('127.0.0.1', 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        print('Démarrage du serveur Flask...')
        self.server.serve_forever()

    def shutdown(self):
        print('Arrêt du serveur Flask...')
        self.server.shutdown()


class NavigationAPI:
    """API exposée au JavaScript pour contrôler la navigation"""
    def __init__(self):
        self._window = None

    def go_back(self):
        """Retour en arrière dans l'historique"""
        self._window.evaluate_js('window.history.back()')

    def go_forward(self):
        """Avancer dans l'historique"""
        self._window.evaluate_js('window.history.forward()')

    def reload(self):
        """Recharger la page"""
        self._window.evaluate_js('window.location.reload()')

    def go_home(self):
        """Retourner à l'accueil"""
        self._window.evaluate_js('window.location.href = "http://127.0.0.1:5000"')

    def set_window(self, window):
        self._window = window


def inject_navigation_bar(window):
    """Injecter une barre de navigation permanente dans toutes les pages"""
    js_code = """
    (function() {
        // Ne pas injecter si déjà présent
        if (document.getElementById('webview-navbar')) return;

        // Charger Font Awesome si pas déjà présent
        if (!document.querySelector('link[href*="font-awesome"]')) {
            const faLink = document.createElement('link');
            faLink.rel = 'stylesheet';
            faLink.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css';
            document.head.appendChild(faLink);
        }

        // Créer la barre de navigation
        const navbar = document.createElement('div');
        navbar.id = 'webview-navbar';
        navbar.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 0 10px;
            z-index: 999999;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        `;

        const buttonStyle = `
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            font-size: 16px;
            width: 35px;
            height: 35px;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        `;

        // Bouton retour
        const btnBack = document.createElement('button');
        btnBack.innerHTML = '<i class="fas fa-arrow-left"></i>';
        btnBack.style.cssText = buttonStyle;
        btnBack.onmouseover = () => btnBack.style.background = 'rgba(255,255,255,0.3)';
        btnBack.onmouseout = () => btnBack.style.background = 'rgba(255,255,255,0.2)';
        btnBack.onclick = () => window.history.back();

        // Bouton home
        const btnHome = document.createElement('button');
        btnHome.innerHTML = '<i class="fas fa-home"></i>';
        btnHome.style.cssText = buttonStyle;
        btnHome.onmouseover = () => btnHome.style.background = 'rgba(255,255,255,0.3)';
        btnHome.onmouseout = () => btnHome.style.background = 'rgba(255,255,255,0.2)';
        btnHome.onclick = () => window.location.href = 'http://127.0.0.1:5000';

        // Bouton reload
        const btnReload = document.createElement('button');
        btnReload.innerHTML = '<i class="fas fa-sync-alt"></i>';
        btnReload.style.cssText = buttonStyle;
        btnReload.onmouseover = () => btnReload.style.background = 'rgba(255,255,255,0.3)';
        btnReload.onmouseout = () => btnReload.style.background = 'rgba(255,255,255,0.2)';
        btnReload.onclick = () => window.location.reload();

        // Titre
        const title = document.createElement('span');
        title.textContent = 'Karadoc';
        title.style.cssText = `
            color: white;
            font-weight: bold;
            margin-left: auto;
            font-size: 16px;
        `;

        navbar.appendChild(btnBack);
        navbar.appendChild(btnHome);
        navbar.appendChild(btnReload);
        navbar.appendChild(title);
        document.body.appendChild(navbar);

        // Ajuster le body pour ne pas être caché par la navbar
        document.body.style.paddingTop = '40px';
    })();
    """
    window.evaluate_js(js_code)


def on_loaded(window):
    """Callback appelé quand une page est chargée"""
    inject_navigation_bar(window)


def main():
    # Démarrer le serveur Flask dans un thread séparé
    server = ServerThread(app)
    server.daemon = True
    server.start()

    # Attendre que le serveur soit prêt
    time.sleep(1)

    # Créer l'API de navigation (sans fenêtre pour l'instant)
    api = NavigationAPI()

    # Créer et afficher la fenêtre webview avec l'API
    window = webview.create_window(
        title='Karadoc',
        url='http://127.0.0.1:5000',
        width=800,
        height=600,
        resizable=True,
        fullscreen=False,
        min_size=(400, 300),
        js_api=api
    )

    # Maintenant assigner la fenêtre à l'API
    api.set_window(window)

    # Injecter la barre de navigation après le chargement
    window.events.loaded += lambda: on_loaded(window)

    # Démarrer webview (bloquant jusqu'à fermeture de la fenêtre)
    webview.start(debug=False)

    # Arrêter le serveur Flask quand la fenêtre est fermée
    server.shutdown()


if __name__ == '__main__':
    main()
