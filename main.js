// Simple cart interaction logic
document.addEventListener('DOMContentLoaded', () => {
    // Add to cart functionality (Mock)
    const addToCartBtns = document.querySelectorAll('.add-to-cart-btn');
    const cartCountEl = document.querySelector('.cart-count');
    
    // Check local storage for cart or initialize
    let cart = JSON.parse(localStorage.getItem('bolddiva_cart')) || [];
    
    const updateCartCount = () => {
        const totalItems = cart.reduce((acc, item) => acc + item.quantity, 0);
        if(cartCountEl) {
            cartCountEl.textContent = totalItems;
        }
    };
    
    updateCartCount();

    addToCartBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            
            const productId = btn.dataset.id;
            const name = btn.dataset.name;
            const price = parseFloat(btn.dataset.price);
            const image = btn.dataset.image;
            
            // Temporary simple animation
            btn.textContent = 'ADDED!';
            btn.style.backgroundColor = '#10B981'; // Green tick feel
            
            setTimeout(() => {
                btn.innerHTML = 'ADD TO CART';
                btn.style.backgroundColor = '';
            }, 1500);

            // Add to local storage cart
            const existingItem = cart.find(i => i.id === productId);
            if(existingItem) {
                existingItem.quantity += 1;
            } else {
                cart.push({ id: productId, name, price, image, quantity: 1 });
            }
            
            localStorage.setItem('bolddiva_cart', JSON.stringify(cart));
            updateCartCount();

            // Create and show Toast Notification
            const toastContainer = document.getElementById('toast-container');
            if (toastContainer) {
                const toast = document.createElement('div');
                toast.style.background = 'rgba(22, 22, 22, 0.95)';
                toast.style.backdropFilter = 'blur(10px)';
                toast.style.border = '1px solid var(--color-border)';
                toast.style.color = '#fff';
                toast.style.padding = '12px 20px';
                toast.style.borderRadius = '8px';
                toast.style.boxShadow = '0 8px 30px rgba(0,0,0,0.5)';
                toast.style.display = 'flex';
                toast.style.alignItems = 'center';
                toast.style.gap = '12px';
                toast.style.transform = 'translateY(50px)';
                toast.style.opacity = '0';
                toast.style.transition = 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)';
                
                toast.innerHTML = `
                    <img src="${image}" style="width: 32px; height: 32px; border-radius: 4px; object-fit: cover;">
                    <div>
                        <div style="font-weight: 600; font-size: 0.9rem;">Added to Cart</div>
                        <div style="font-size: 0.8rem; color: var(--color-text-muted);">${name}</div>
                    </div>
                `;
                
                toastContainer.appendChild(toast);
                
                // Animate in
                setTimeout(() => {
                    toast.style.transform = 'translateY(0)';
                    toast.style.opacity = '1';
                }, 10);
                
                // Animate out and remove
                setTimeout(() => {
                    toast.style.transform = 'translateY(20px)';
                    toast.style.opacity = '0';
                    setTimeout(() => toast.remove(), 300);
                }, 3000);
            }
        });
    });
    
    // Buy Now - add to cart and go straight to checkout
    document.querySelectorAll('.buy-now-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const productId = btn.dataset.id;
            const name = btn.dataset.name;
            const price = parseFloat(btn.dataset.price);
            const image = btn.dataset.image;
            
            const existingItem = cart.find(i => i.id === productId);
            if (existingItem) {
                existingItem.quantity += 1;
            } else {
                cart.push({ id: productId, name, price, image, quantity: 1 });
            }
            localStorage.setItem('bolddiva_cart', JSON.stringify(cart));
            window.location.href = '/checkout/';
        });
    });
    
    // Search Trigger logic
    const searchTrigger = document.querySelector('.search-trigger');
    const searchOverlay = document.getElementById('search-overlay');
    const closeSearch = document.getElementById('close-search');
    
    if (searchTrigger && searchOverlay) {
        searchTrigger.addEventListener('click', (e) => {
            e.preventDefault();
            searchOverlay.classList.add('active');
            setTimeout(() => { searchOverlay.querySelector('input').focus(); }, 100);
        });
    }
    if (closeSearch && searchOverlay) {
        closeSearch.addEventListener('click', () => {
            searchOverlay.classList.remove('active');
        });
    }



    // Shade Finder logic
    const sfTrigger = document.getElementById('open-shade-finder');
    const sfOverlay = document.getElementById('shade-finder-overlay');
    const closeSf = document.getElementById('close-shade-finder');

    if (sfTrigger && sfOverlay) {
        sfTrigger.addEventListener('click', (e) => {
            e.preventDefault();
            sfOverlay.classList.add('active');
            // reset steps
            document.getElementById('shade-step-1').style.display = 'block';
            document.getElementById('shade-step-2').style.display = 'none';
            document.getElementById('shade-step-3').style.display = 'none';
        });
    }
    
    if (closeSf && sfOverlay) {
        closeSf.addEventListener('click', () => {
            sfOverlay.classList.remove('active');
        });
    }

    // Custom Form Validation to replace native browser popups
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.setAttribute('novalidate', true); // Diable native popups
        
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            // Clear old custom errors
            form.querySelectorAll('.custom-error').forEach(el => el.remove());
            
            form.querySelectorAll('input, select, textarea').forEach(field => {
                if (!field.checkValidity()) {
                    isValid = false;
                    const errorMsg = document.createElement('div');
                    errorMsg.className = 'custom-error';
                    errorMsg.textContent = field.validationMessage || 'This field is required';
                    field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    field.classList.add('invalid-field');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
        
        // Remove error correctly on input
        form.addEventListener('input', function(e) {
            if (e.target.classList && e.target.classList.contains('invalid-field')) {
                if (e.target.checkValidity()) {
                    e.target.classList.remove('invalid-field');
                    if (e.target.parentNode) {
                        const err = e.target.parentNode.querySelector('.custom-error');
                        if (err) err.remove();
                    }
                }
            }
        });
    });
});

function nextShadeStep(stepNum) {
    document.getElementById('shade-step-1').style.display = 'none';
    document.getElementById('shade-step-2').style.display = 'none';
    document.getElementById('shade-step-3').style.display = 'none';
    document.getElementById('shade-step-' + stepNum).style.display = 'block';
}

function closeShadeFinder() {
    document.getElementById('shade-finder-overlay').classList.remove('active');
}
