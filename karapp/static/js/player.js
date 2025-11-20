/**
 * Lecteur audio modal pour Karadoc
 * Utilisé pour la musique et les podcasts
 */

let tracks = [];
let currentTrackIndex = 0;
let audioPlayer = null;
let isPlaying = false;

// Initialisation du lecteur
document.addEventListener('DOMContentLoaded', function() {
    console.log('Player.js: Initialisation...');

    audioPlayer = document.getElementById('audioPlayer');

    if (!audioPlayer) {
        console.error('Audio player element not found');
        return;
    }

    console.log('Player.js: Audio player trouvé');

    // Récupérer toutes les pistes de musique
    const musicCards = document.querySelectorAll('.file');
    console.log('Player.js: Nombre de pistes trouvées:', musicCards.length);

    tracks = Array.from(musicCards).map(card => ({
        url: card.dataset.trackUrl,
        title: card.dataset.trackTitle,
        artist: card.dataset.trackArtist,
        artwork: card.dataset.trackArtwork
    }));

    console.log('Player.js: Tracks chargées:', tracks);

    // Ajouter les event listeners pour ouvrir le modal
    musicCards.forEach((card, index) => {
        card.addEventListener('click', () => {
            console.log('Click sur la piste:', index);
            openPlayer(index);
        });
    });

    // Event listeners pour les contrôles du lecteur
    document.querySelector('.player-close').addEventListener('click', closePlayer);
    document.getElementById('playPauseBtn').addEventListener('click', togglePlayPause);
    document.getElementById('prevBtn').addEventListener('click', previousTrack);
    document.getElementById('nextBtn').addEventListener('click', nextTrack);
    document.getElementById('volumeUpBtn').addEventListener('click', volumeUp);
    document.getElementById('volumeDownBtn').addEventListener('click', volumeDown);

    // Timeline
    const timeline = document.getElementById('timeline');
    timeline.addEventListener('input', seekTrack);

    // Mise à jour de la timeline pendant la lecture
    audioPlayer.addEventListener('timeupdate', updateTimeline);

    // Passage automatique au morceau suivant
    audioPlayer.addEventListener('ended', nextTrack);

    // Fermer le modal si on clique sur le fond
    document.getElementById('playerModal').addEventListener('click', function(e) {
        if (e.target === this) closePlayer();
    });
});

// Ouvrir le lecteur avec une piste spécifique
function openPlayer(index) {
    console.log('openPlayer appelé avec index:', index);
    currentTrackIndex = index;
    const modal = document.getElementById('playerModal');
    console.log('Modal trouvé:', modal);
    modal.style.display = 'block';

    loadTrack(currentTrackIndex);

    // Essayer de lancer la lecture (avec gestion d'erreur pour autoplay)
    console.log('Tentative de lecture...');
    const playPromise = audioPlayer.play();
    if (playPromise !== undefined) {
        playPromise.then(() => {
            console.log('Lecture lancée avec succès');
            isPlaying = true;
            updatePlayPauseButton();
        }).catch(error => {
            console.log("Autoplay bloqué:", error);
            isPlaying = false;
            updatePlayPauseButton();
        });
    }
}

// Fermer le lecteur
function closePlayer() {
    const modal = document.getElementById('playerModal');
    modal.style.display = 'none';
    audioPlayer.pause();
    isPlaying = false;
    updatePlayPauseButton();
}

// Charger une piste
function loadTrack(index) {
    const track = tracks[index];
    console.log('Chargement de la piste:', track);
    console.log('URL audio:', track.url);
    audioPlayer.src = track.url;
    console.log('Audio src assigné:', audioPlayer.src);

    // Mettre à jour l'affichage
    document.getElementById('trackTitle').textContent = track.title || 'Sans titre';
    document.getElementById('trackArtist').textContent = track.artist || '';

    // Afficher l'artwork si disponible
    const artworkDiv = document.getElementById('trackArtwork');
    if (track.artwork) {
        artworkDiv.style.backgroundImage = `url('data:image/jpeg;base64,${track.artwork}')`;
    } else {
        artworkDiv.style.backgroundImage = 'none';
        artworkDiv.style.backgroundColor = '#f3d2c1';
    }

    // Réinitialiser la timeline
    document.getElementById('timeline').value = 0;
    document.getElementById('currentTime').textContent = '0:00';
    document.getElementById('duration').textContent = '0:00';
}

// Toggle play/pause
function togglePlayPause() {
    if (isPlaying) {
        audioPlayer.pause();
        isPlaying = false;
        updatePlayPauseButton();
    } else {
        const playPromise = audioPlayer.play();
        if (playPromise !== undefined) {
            playPromise.then(() => {
                isPlaying = true;
                updatePlayPauseButton();
            }).catch(error => {
                console.error("Erreur de lecture:", error);
                isPlaying = false;
                updatePlayPauseButton();
            });
        }
    }
}

// Mettre à jour le bouton play/pause
function updatePlayPauseButton() {
    const btn = document.getElementById('playPauseBtn');
    btn.textContent = isPlaying ? '⏸' : '▶️';
}

// Piste précédente
function previousTrack() {
    currentTrackIndex = (currentTrackIndex - 1 + tracks.length) % tracks.length;
    loadTrack(currentTrackIndex);
    if (isPlaying) {
        const playPromise = audioPlayer.play();
        if (playPromise !== undefined) {
            playPromise.catch(error => {
                console.error("Erreur de lecture:", error);
                isPlaying = false;
                updatePlayPauseButton();
            });
        }
    }
}

// Piste suivante
function nextTrack() {
    currentTrackIndex = (currentTrackIndex + 1) % tracks.length;
    loadTrack(currentTrackIndex);
    if (isPlaying) {
        const playPromise = audioPlayer.play();
        if (playPromise !== undefined) {
            playPromise.catch(error => {
                console.error("Erreur de lecture:", error);
                isPlaying = false;
                updatePlayPauseButton();
            });
        }
    }
}

// Augmenter le volume
function volumeUp() {
    if (audioPlayer.volume < 1) {
        audioPlayer.volume = Math.min(1, audioPlayer.volume + 0.1);
        updateVolumeDisplay();
    }
}

// Diminuer le volume
function volumeDown() {
    if (audioPlayer.volume > 0) {
        audioPlayer.volume = Math.max(0, audioPlayer.volume - 0.1);
        updateVolumeDisplay();
    }
}

// Afficher le volume
function updateVolumeDisplay() {
    const volumePercent = Math.round(audioPlayer.volume * 100);
    document.getElementById('volumeLevel').textContent = `${volumePercent}%`;
}

// Chercher dans la timeline
function seekTrack() {
    const timeline = document.getElementById('timeline');
    const time = (timeline.value / 100) * audioPlayer.duration;
    audioPlayer.currentTime = time;
}

// Mettre à jour la timeline
function updateTimeline() {
    const timeline = document.getElementById('timeline');
    const percent = (audioPlayer.currentTime / audioPlayer.duration) * 100;
    timeline.value = percent || 0;

    // Mettre à jour les temps affichés
    document.getElementById('currentTime').textContent = formatTime(audioPlayer.currentTime);
    document.getElementById('duration').textContent = formatTime(audioPlayer.duration);
}

// Formater le temps (secondes -> mm:ss)
function formatTime(seconds) {
    if (isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Navigation au clavier
document.addEventListener('keydown', function(e) {
    const modal = document.getElementById('playerModal');
    if (modal.style.display === 'block') {
        if (e.key === 'Escape') closePlayer();
        if (e.key === ' ') {
            e.preventDefault();
            togglePlayPause();
        }
        if (e.key === 'ArrowRight') nextTrack();
        if (e.key === 'ArrowLeft') previousTrack();
        if (e.key === 'ArrowUp') {
            e.preventDefault();
            volumeUp();
        }
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            volumeDown();
        }
    }
});
