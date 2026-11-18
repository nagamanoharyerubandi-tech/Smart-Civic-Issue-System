/**
 * Smart Civic Issue System - Interactive Frontend Logic
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Theme Management (Light / Dark)
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const storedTheme = localStorage.getItem('civic_theme') || 'light';
    applyTheme(storedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function () {
            const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            applyTheme(newTheme);
            localStorage.setItem('civic_theme', newTheme);
        });
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        const icon = document.getElementById('theme-toggle-icon');
        if (icon) {
            if (theme === 'dark') {
                icon.className = 'bi bi-sun-fill text-warning';
            } else {
                icon.className = 'bi bi-moon-stars-fill text-secondary';
            }
        }
        // Emit custom event for Chart.js updates
        document.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: theme } }));
    }

    // 2. Mobile Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.dashboard-sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('show');
            if (sidebarOverlay) sidebarOverlay.classList.toggle('d-none');
        });
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function () {
            if (sidebar) sidebar.classList.remove('show');
            sidebarOverlay.classList.add('d-none');
        });
    }

    // 3. Image Upload Live Preview
    const photoInput = document.getElementById('id_photograph');
    const previewContainer = document.getElementById('image-preview-container');
    const previewImage = document.getElementById('image-preview-element');

    if (photoInput && previewContainer && previewImage) {
        photoInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                // Check 5MB limit client-side
                if (file.size > 5 * 1024 * 1024) {
                    alert('File size exceeds 5MB limit. Please choose a smaller image.');
                    photoInput.value = '';
                    previewContainer.classList.add('d-none');
                    return;
                }
                const reader = new FileReader();
                reader.onload = function (event) {
                    previewImage.src = event.target.result;
                    previewContainer.classList.remove('d-none');
                };
                reader.readAsDataURL(file);
            } else {
                previewContainer.classList.add('d-none');
            }
        });
    }

    // 4. Geolocation Auto-Detection
    const geoBtn = document.getElementById('btn-get-location');
    const latInput = document.getElementById('id_latitude');
    const lngInput = document.getElementById('id_longitude');
    const geoFeedback = document.getElementById('geo-feedback');

    if (geoBtn && latInput && lngInput) {
        geoBtn.addEventListener('click', function () {
            if (navigator.geolocation) {
                geoBtn.disabled = true;
                geoBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Locating...';
                navigator.geolocation.getCurrentPosition(
                    function (position) {
                        latInput.value = position.coords.latitude.toFixed(6);
                        lngInput.value = position.coords.longitude.toFixed(6);
                        geoBtn.innerHTML = '<i class="bi bi-geo-alt-fill text-success me-1"></i> Coordinates Captured';
                        geoBtn.classList.remove('btn-outline-secondary');
                        geoBtn.classList.add('btn-outline-success');
                        if (geoFeedback) {
                            geoFeedback.innerHTML = `<span class="badge bg-success-subtle text-success">Lat: ${latInput.value}, Lng: ${lngInput.value}</span>`;
                        }
                    },
                    function (error) {
                        geoBtn.disabled = false;
                        geoBtn.innerHTML = '<i class="bi bi-geo-alt me-1"></i> Detect Current Location';
                        alert('Could not retrieve current location: ' + error.message);
                    }
                );
            } else {
                alert('Geolocation is not supported by your browser.');
            }
        });
    }

    // 5. Initialize Bootstrap Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 6. Auto-dismiss Alert Messages after 6 seconds
    const autoAlerts = document.querySelectorAll('.alert-dismissible');
    autoAlerts.forEach(function (alertEl) {
        setTimeout(function () {
            try {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
                if (bsAlert) bsAlert.close();
            } catch (err) {}
        }, 6000);
    });
});
