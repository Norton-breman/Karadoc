let photos = [];
let currentPhotoIndex = 0;

// Récupérer toutes les photos
document.addEventListener('DOMContentLoaded', function() {
    const thumbnails = document.querySelectorAll('.file');
    photos = Array.from(thumbnails).map(thumb => thumb.dataset.photoUrl);

    // Ajouter les event listeners
    thumbnails.forEach((thumbnail, index) => {
        thumbnail.addEventListener('click', () => openModal(index));
    });
});

function openModal(index) {
    currentPhotoIndex = index;
    const modal = document.getElementById('photoModal');
    const modalImg = document.getElementById('modalImage');

    modal.style.display = 'block';
    modalImg.src = photos[currentPhotoIndex];
}

function closeModal() {
    document.getElementById('photoModal').style.display = 'none';
}

function nextPhoto() {
    currentPhotoIndex = (currentPhotoIndex + 1) % photos.length;
    document.getElementById('modalImage').src = photos[currentPhotoIndex];
}

function prevPhoto() {
    currentPhotoIndex = (currentPhotoIndex - 1 + photos.length) % photos.length;
    document.getElementById('modalImage').src = photos[currentPhotoIndex];
}

// Event listeners pour le modal
document.getElementById('photoModal').addEventListener('click', function(e) {
    if (e.target === this) closeModal();
});

document.querySelector('.photo-close').addEventListener('click', closeModal);
document.querySelector('.photo-next').addEventListener('click', nextPhoto);
document.querySelector('.photo-prev').addEventListener('click', prevPhoto);

// Navigation au clavier
document.addEventListener('keydown', function(e) {
    if (document.getElementById('photoModal').style.display === 'block') {
        if (e.key === 'Escape') closeModal();
        if (e.key === 'ArrowRight') nextPhoto();
        if (e.key === 'ArrowLeft') prevPhoto();
    }
});