// Ecommerence - Common JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alerts after 5 seconds.
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // Quantity input validation on cart page.
    const qtyInputs = document.querySelectorAll('input[name="quantity"]');
    qtyInputs.forEach(function (input) {
        input.addEventListener('change', function () {
            if (this.value < 1) this.value = 1;
        });
    });

    // Confirm delete actions.
    const deleteLinks = document.querySelectorAll('a[href*="delete"], a[href*="remove"]');
    deleteLinks.forEach(function (link) {
        if (!link.dataset.confirm) {
            link.dataset.confirm = 'Are you sure?';
            link.addEventListener('click', function (e) {
                if (!confirm(this.dataset.confirm)) {
                    e.preventDefault();
                }
            });
        }
    });
});
