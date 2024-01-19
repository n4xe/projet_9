document.addEventListener('DOMContentLoaded', (event) => {
        // Affiche le message pendant un court moment avant de le cacher
        const messages = document.querySelectorAll('.message');
        messages.forEach((message) => {
            message.classList.add('visible');
            setTimeout(() => {
                message.classList.remove('visible');
            }, 4000); // Le message reste visible pendant 4 secondes
        });
    });

