/**
 * School Lost & Found - Frontend Vanilla JavaScript
 * Class 12 CBSE Computer Science (083) Project
 */

document.addEventListener('DOMContentLoaded', function() {
    initMobileNav();
    initAlertDismissal();
    initFormValidation();
    initPasswordToggle();
    initConfirmationModals();
    initLiveSearchFilter();
});

/* -------------------------------------------------------------------------
   1. Mobile Navigation Toggle
   ------------------------------------------------------------------------- */
function initMobileNav() {
    const toggleBtn = document.querySelector('.mobile-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (toggleBtn && navLinks) {
        toggleBtn.addEventListener('click', function() {
            navLinks.classList.toggle('show');
            const isOpen = navLinks.classList.contains('show');
            toggleBtn.setAttribute('aria-expanded', isOpen);
            toggleBtn.innerHTML = isOpen ? '&#10005;' : '&#9776;';
        });

        // Close when clicking outside
        document.addEventListener('click', function(e) {
            if (!navLinks.contains(e.target) && !toggleBtn.contains(e.target) && navLinks.classList.contains('show')) {
                navLinks.classList.remove('show');
                toggleBtn.innerHTML = '&#9776;';
            }
        });
    }
}

/* -------------------------------------------------------------------------
   2. Alert Dismissal
   ------------------------------------------------------------------------- */
function initAlertDismissal() {
    const closeButtons = document.querySelectorAll('.alert-close');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const alert = this.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-6px)';
                setTimeout(() => alert.remove(), 250);
            }
        });
    });

    // Auto-dismiss success/info alerts after 6 seconds
    const autoAlerts = document.querySelectorAll('.alert-success, .alert-info');
    autoAlerts.forEach(alert => {
        setTimeout(() => {
            if (alert && alert.parentElement) {
                alert.style.opacity = '0';
                alert.style.transition = 'all 0.4s ease';
                setTimeout(() => alert.remove(), 400);
            }
        }, 6000);
    });
}

/* -------------------------------------------------------------------------
   3. Form Validation (Client-Side Enhancements)
   ------------------------------------------------------------------------- */
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate="true"]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const requiredInputs = form.querySelectorAll('[required]');

            // Clear previous errors
            form.querySelectorAll('.validation-msg').forEach(el => el.remove());
            form.querySelectorAll('.input-error').forEach(el => el.classList.remove('input-error'));

            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    highlightInputError(input, 'This field is required.');
                }
            });

            // Email check
            const emailInput = form.querySelector('input[type="email"]');
            if (emailInput && emailInput.value.trim()) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(emailInput.value.trim())) {
                    isValid = false;
                    highlightInputError(emailInput, 'Please enter a valid email address.');
                }
            }

            // Password confirmation check
            const password = form.querySelector('input[name="password"]');
            const confirmPassword = form.querySelector('input[name="confirm_password"]');
            if (password && confirmPassword) {
                if (password.value !== confirmPassword.value) {
                    isValid = false;
                    highlightInputError(confirmPassword, 'Passwords do not match.');
                } else if (password.value.length < 6) {
                    isValid = false;
                    highlightInputError(password, 'Password must be at least 6 characters long.');
                }
            }

            if (!isValid) {
                e.preventDefault();
                // Scroll to first error
                const firstError = form.querySelector('.input-error');
                if (firstError) {
                    firstError.focus();
                }
            }
        });
    });
}

function highlightInputError(input, message) {
    input.classList.add('input-error');
    input.style.borderColor = '#ef4444';
    
    const msg = document.createElement('div');
    msg.className = 'validation-msg';
    msg.style.color = '#f87171';
    msg.style.fontSize = '0.78rem';
    msg.style.marginTop = '4px';
    msg.textContent = message;
    
    input.parentNode.appendChild(msg);

    input.addEventListener('input', function() {
        input.style.borderColor = '';
        msg.remove();
    }, { once: true });
}

/* -------------------------------------------------------------------------
   4. Password Visibility Toggle
   ------------------------------------------------------------------------- */
function initPasswordToggle() {
    const toggleButtons = document.querySelectorAll('.toggle-password-btn');
    toggleButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const input = document.getElementById(targetId);
            if (input) {
                const isPassword = input.getAttribute('type') === 'password';
                input.setAttribute('type', isPassword ? 'text' : 'password');
                this.textContent = isPassword ? '🔒 Hide' : '👁 Show';
            }
        });
    });
}

/* -------------------------------------------------------------------------
   5. Reusable Confirmation Modal Dialog
   ------------------------------------------------------------------------- */
function initConfirmationModals() {
    const modalBackdrop = document.getElementById('confirmModal');
    if (!modalBackdrop) return;

    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    const modalConfirmBtn = document.getElementById('modalConfirmBtn');
    const modalCancelBtn = document.getElementById('modalCancelBtn');

    let activeForm = null;

    document.querySelectorAll('[data-confirm]').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            activeForm = this.closest('form');
            const message = this.getAttribute('data-confirm') || 'Are you sure you want to proceed?';
            const actionType = this.getAttribute('data-action-type') || 'danger';
            const title = this.getAttribute('data-title') || 'Confirm Action';

            modalTitle.textContent = title;
            modalBody.textContent = message;

            if (actionType === 'danger') {
                modalConfirmBtn.className = 'btn btn-danger';
                modalConfirmBtn.textContent = 'Confirm Delete';
            } else if (actionType === 'approve') {
                modalConfirmBtn.className = 'btn btn-success';
                modalConfirmBtn.textContent = 'Confirm Approval';
            } else {
                modalConfirmBtn.className = 'btn btn-primary';
                modalConfirmBtn.textContent = 'Confirm';
            }

            modalBackdrop.classList.add('active');
        });
    });

    if (modalCancelBtn) {
        modalCancelBtn.addEventListener('click', () => {
            modalBackdrop.classList.remove('active');
            activeForm = null;
        });
    }

    if (modalConfirmBtn) {
        modalConfirmBtn.addEventListener('click', () => {
            if (activeForm) {
                activeForm.submit();
            }
            modalBackdrop.classList.remove('active');
        });
    }

    modalBackdrop.addEventListener('click', (e) => {
        if (e.target === modalBackdrop) {
            modalBackdrop.classList.remove('active');
            activeForm = null;
        }
    });
}

/* -------------------------------------------------------------------------
   6. Snappy Live Table Filter
   ------------------------------------------------------------------------- */
function initLiveSearchFilter() {
    const liveInput = document.getElementById('liveTableSearch');
    if (!liveInput) return;

    liveInput.addEventListener('input', function() {
        const term = this.value.toLowerCase().trim();
        const rows = document.querySelectorAll('tbody tr[data-search-row]');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(term)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}
