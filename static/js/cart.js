const userId = localStorage.getItem('userId');
if (!userId) window.location.href = '/login';

document.getElementById('logoutBtn').addEventListener('click', e => {
    e.preventDefault();
    localStorage.clear();
    window.location.href = '/login';
});

let cartData = { items: [], total: 0 };
let productImageCache = {};
let selectedRating = 0;

// Pre-fetch all product images once
async function prefetchImages() {
    try {
        const res = await fetch('/api/products');
        const products = await res.json();
        products.forEach(p => { productImageCache[p._id] = p.image; });
    } catch {}
}

async function loadCart() {
    await prefetchImages();
    try {
        const res = await fetch(`/api/basket/${userId}`);
        cartData = await res.json();
        renderCart();
    } catch {
        document.getElementById('cartItems').innerHTML = '<p style="color:var(--accent);padding:20px">Failed to load cart.</p>';
    }
}

function renderCart() {
    const container = document.getElementById('cartItems');
    if (!cartData.items || cartData.items.length === 0) {
        container.innerHTML = `
            <div class="empty-cart">
                <div class="empty-cart-icon">🛒</div>
                <h3>Your cart is empty</h3>
                <p>Looks like you haven't added anything yet.<br>
                   <a href="/home">Start shopping →</a>
                </p>
            </div>`;
        updateTotals(0);
        return;
    }

    container.innerHTML = '<h2>My Cart (' + cartData.items.length + ' items)</h2>' +
        cartData.items.map((item, idx) => {
            const img = productImageCache[item.product_id] || '';
            const imgHtml = img
                ? `<img src="${img}" alt="${item.name}" class="cart-item-image" onerror="this.style.display='none'">`
                : `<div class="cart-item-image" style="background:var(--bg);display:flex;align-items:center;justify-content:center;font-size:32px;border-radius:10px;border:1.5px solid var(--border)">🛍️</div>`;

            const opts = [
                item.size ? `<span class="item-tag">Size: ${item.size}</span>` : '',
                item.color ? `<span class="item-tag">Color: ${item.color}</span>` : ''
            ].filter(Boolean).join('');

            return `
            <div class="cart-item" id="item-${idx}">
                ${imgHtml}
                <div class="cart-item-details">
                    <div class="cart-item-name" onclick="window.location.href='/product/${item.product_id}'">${item.name}</div>
                    <div class="cart-item-price">₹${fmt(item.price)}</div>
                    ${opts ? `<div class="cart-item-options">${opts}</div>` : ''}
                    <div class="cart-item-quantity">
                        <button class="qty-btn" onclick="changeQty('${item.product_id}', -1)">−</button>
                        <span class="qty-value">${item.quantity}</span>
                        <button class="qty-btn" onclick="changeQty('${item.product_id}', 1)">+</button>
                        <span class="item-subtotal">= ₹${fmt(item.price * item.quantity)}</span>
                    </div>
                    <div class="cart-item-actions">
                        <button class="btn-remove" onclick="removeItem('${item.product_id}')">🗑 Remove</button>
                        <button class="btn-review" onclick="openReviewModal('${item.product_id}', '${item.name.replace(/'/g,"\\'")}')">✍ Review</button>
                    </div>
                </div>
            </div>`;
        }).join('');

    updateTotals(cartData.total || 0);
}

function updateTotals(subtotal) {
    const tax = subtotal * 0.18;
    const total = subtotal + tax;
    document.getElementById('subtotal').textContent = '₹' + fmt(subtotal);
    document.getElementById('tax').textContent = '₹' + fmt(tax);
    document.getElementById('total').textContent = '₹' + fmt(total);
    document.getElementById('checkoutTotal').textContent = fmt(total);
}

function fmt(n) { return Math.round(n).toLocaleString('en-IN'); }

async function changeQty(productId, delta) {
    const item = cartData.items.find(i => i.product_id === productId);
    if (!item) return;
    const newQty = item.quantity + delta;
    if (newQty <= 0) { removeItem(productId); return; }
    try {
        await fetch(`/api/basket/${userId}/item`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId })
        });
        await fetch(`/api/basket/${userId}/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId, quantity: newQty, size: item.size, color: item.color })
        });
        loadCart();
    } catch { showToast('Could not update quantity', 'error'); }
}

async function removeItem(productId) {
    try {
        const res = await fetch(`/api/basket/${userId}/remove`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId })
        });
        if (res.ok) { showToast('✓ Item removed'); loadCart(); }
    } catch { showToast('Could not remove item', 'error'); }
}

async function clearCart() {
    if (!confirm('Remove all items from cart?')) return;
    try {
        await fetch(`/api/basket/${userId}/clear`, { method: 'DELETE' });
        loadCart();
    } catch { showToast('Error clearing cart', 'error'); }
}

function showCheckoutForm() {
    if (!cartData.items || !cartData.items.length) { showToast('Your cart is empty!', 'error'); return; }
    document.getElementById('checkoutModal').style.display = 'block';
}

function closeCheckoutModal() { document.getElementById('checkoutModal').style.display = 'none'; }

document.getElementById('checkoutForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const address = {
        street: document.getElementById('street').value,
        city:   document.getElementById('city').value,
        state:  document.getElementById('state').value,
        zip:    document.getElementById('zip').value,
        country: document.getElementById('country').value
    };
    const paymentMethod = document.getElementById('paymentMethod').value;
    const selectedItems = cartData.items.map(i => ({ product_id: i.product_id, quantity: i.quantity }));
    try {
        const res = await fetch(`/api/basket/${userId}/purchase`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ selected_items: selectedItems, address, payment_method: paymentMethod })
        });
        const data = await res.json();
        if (res.ok) { closeCheckoutModal(); showSuccessOverlay(data.order_id, data.total); }
        else showToast(data.error || 'Order failed', 'error');
    } catch { showToast('Error placing order', 'error'); }
});

function showSuccessOverlay(orderId, total) {
    const ov = document.createElement('div');
    ov.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(26,26,46,0.85);z-index:9999;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(8px)';
    ov.innerHTML = `
        <div style="background:white;padding:48px 40px;border-radius:24px;text-align:center;max-width:460px;width:90%;box-shadow:0 24px 80px rgba(0,0,0,0.4)">
            <div style="font-size:64px;margin-bottom:16px">🎉</div>
            <h2 style="font-size:26px;font-weight:800;color:#1A1A2E;margin-bottom:8px">Order Confirmed!</h2>
            <p style="color:#7A7A9A;font-size:13px;margin-bottom:6px">Order ID: <strong style="color:#1A1A2E">${orderId}</strong></p>
            <p style="font-size:32px;font-weight:800;color:#6C63FF;letter-spacing:-1px;margin:16px 0">₹${fmt(total)}</p>
            <p style="color:#7A7A9A;font-size:14px;margin-bottom:28px">Thank you for shopping with ShopEasy!</p>
            <button onclick="window.location.href='/home'"
                style="padding:13px 36px;background:linear-gradient(135deg,#6C63FF,#5A52E0);color:white;border:none;border-radius:50px;font-size:15px;font-weight:700;cursor:pointer;font-family:Inter,sans-serif">
                Continue Shopping →
            </button>
        </div>`;
    document.body.appendChild(ov);
    loadCart();
}

// Reviews
function openReviewModal(productId, productName) {
    document.getElementById('reviewProductId').value = productId;
    document.getElementById('reviewModalTitle').textContent = `Review: ${productName}`;
    selectedRating = 0;
    document.querySelectorAll('.star').forEach(s => { s.classList.remove('active'); s.style.color = '#ddd'; });
    document.getElementById('reviewTitle').value = '';
    document.getElementById('reviewText').value = '';
    document.getElementById('reviewModal').style.display = 'block';
}

function closeReviewModal() { document.getElementById('reviewModal').style.display = 'none'; }

document.querySelectorAll('.star').forEach(star => {
    star.addEventListener('click', function() {
        selectedRating = parseInt(this.dataset.rating);
        document.getElementById('rating').value = selectedRating;
        document.querySelectorAll('.star').forEach((s, i) => {
            s.classList.toggle('active', i < selectedRating);
            s.style.color = i < selectedRating ? '#FBBF24' : '#ddd';
        });
    });
    star.addEventListener('mouseover', function() {
        const r = parseInt(this.dataset.rating);
        document.querySelectorAll('.star').forEach((s, i) => { s.style.color = i < r ? '#FBBF24' : '#ddd'; });
    });
    star.addEventListener('mouseout', function() {
        document.querySelectorAll('.star').forEach((s, i) => { s.style.color = i < selectedRating ? '#FBBF24' : '#ddd'; });
    });
});

document.getElementById('reviewForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    if (!selectedRating) { showToast('Please select a star rating', 'error'); return; }
    const productId = document.getElementById('reviewProductId').value;
    try {
        const res = await fetch(`/api/products/${productId}/reviews`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                rating: selectedRating,
                title: document.getElementById('reviewTitle').value,
                text: document.getElementById('reviewText').value
            })
        });
        const data = await res.json();
        if (res.ok) { closeReviewModal(); showToast('⭐ Review submitted!'); }
        else showToast(data.error || 'Failed to submit review', 'error');
    } catch { showToast('Error submitting review', 'error'); }
});

window.onclick = e => {
    if (e.target === document.getElementById('checkoutModal')) closeCheckoutModal();
    if (e.target === document.getElementById('reviewModal')) closeReviewModal();
};

function showToast(msg, type = 'success') {
    const t = document.createElement('div');
    t.className = 'toast';
    t.textContent = msg;
    t.style.background = type === 'error' ? '#FF6B6B' : '#6C63FF';
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}

loadCart();
