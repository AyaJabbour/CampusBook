/**
 * CampusBook — Interactions Client JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Fermeture automatique douce des alertes flash après 6 secondes
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 6000);
    });

    // 2. Définition automatique de la date minimale (aujourd'hui) pour les sélecteurs de date
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    dateInputs.forEach(function (input) {
        if (!input.getAttribute('min')) {
            input.setAttribute('min', today);
        }
    });

    // 3. Calcul dynamique de la durée de réservation et validation visuelle
    const startTimeInput = document.getElementById('start_time');
    const endTimeInput = document.getElementById('end_time');
    const durationDisplay = document.getElementById('duration_preview');

    function updateDurationPreview() {
        if (!startTimeInput || !endTimeInput || !durationDisplay) return;

        const startVal = startTimeInput.value;
        const endVal = endTimeInput.value;

        if (startVal && endVal) {
            const [startH, startM] = startVal.split(':').map(Number);
            const [endH, endM] = endVal.split(':').map(Number);

            const startTotal = startH * 60 + startM;
            const endTotal = endH * 60 + endM;
            const diffMin = endTotal - startTotal;

            if (diffMin <= 0) {
                durationDisplay.innerHTML = '<span class="text-danger"><i class="bi bi-x-circle me-1"></i>L\'heure de fin doit être après le début.</span>';
            } else {
                const hours = Math.floor(diffMin / 60);
                const minutes = diffMin % 60;
                let durationText = '';
                if (hours > 0) durationText += `${hours}h `;
                if (minutes > 0) durationText += `${minutes}min`;
                durationDisplay.innerHTML = `<span class="text-success"><i class="bi bi-clock-history me-1"></i>Durée estimée : <strong>${durationText}</strong></span>`;
            }
        }
    }

    if (startTimeInput && endTimeInput) {
        startTimeInput.addEventListener('change', updateDurationPreview);
        endTimeInput.addEventListener('change', updateDurationPreview);
        updateDurationPreview();
    }

    // 4. Confirmation avant annulation
    const cancelForms = document.querySelectorAll('form.confirm-cancel');
    cancelForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const confirmed = window.confirm("Êtes-vous sûr de vouloir annuler cette réservation ? Cette action est irréversible et libérera le créneau.");
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });
});
