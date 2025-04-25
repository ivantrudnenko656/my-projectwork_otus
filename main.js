// Main JavaScript file for TechElectronics Store

document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Quantity input validation in cart
    const quantityInputs = document.querySelectorAll('input[name="quantity"]');
    if (quantityInputs) {
        quantityInputs.forEach(input => {
            input.addEventListener('change', function() {
                const min = parseInt(this.getAttribute('min'));
                const max = parseInt(this.getAttribute('max'));
                let value = parseInt(this.value);

                if (value < min) {
                    this.value = min;
                } else if (value > max) {
                    this.value = max;
                    alert(`Sorry, we only have ${max} units in stock.`);
                }

                // Auto-submit the form when quantity changes
                this.closest('form').submit();
            });
        });
    }

    // Product image hover effect
    const productCards = document.querySelectorAll('.card');
    if (productCards) {
        productCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                const img = this.querySelector('img');
                if (img) {
                    img.style.transform = 'scale(1.05)';
                    img.style.transition = 'transform 0.3s ease';
                }
            });

            card.addEventListener('mouseleave', function() {
                const img = this.querySelector('img');
                if (img) {
                    img.style.transform = 'scale(1)';
                }
            });
        });
    }

    // Flash sale countdown timer (if needed)
    function updateTimer() {
        const timerElements = document.querySelectorAll('.flash-sale-timer');
        if (timerElements.length === 0) return;

        timerElements.forEach(timerElement => {
            const endTime = new Date(timerElement.dataset.endTime).getTime();
            const now = new Date().getTime();
            const distance = endTime - now;

            if (distance < 0) {
                timerElement.innerHTML = "Sale Ended";
                return;
            }

            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            timerElement.innerHTML = `${hours}h ${minutes}m ${seconds}s`;
        });
    }

    // If there are any timers on the page, start updating them
    if (document.querySelectorAll('.flash-sale-timer').length > 0) {
        setInterval(updateTimer, 1000);
    }
});

// Function to add animation when adding to cart
function addToCartAnimation(event, buttonElement) {
    event.preventDefault();

    // Add a visual feedback when adding to cart
    buttonElement.innerHTML = '<i class="fas fa-check"></i> Added!';
    buttonElement.classList.replace('btn-primary', 'btn-success');

    setTimeout(() => {
        buttonElement.innerHTML = '<i class="fas fa-cart-plus"></i> Add to Cart';
        buttonElement.classList.replace('btn-success', 'btn-primary');
        buttonElement.closest('form').submit();
    }, 1000);

    return false;
}