const userId = localStorage.getItem('userId');
if (!userId) window.location.href = '/login';

document.getElementById('logoutBtn').addEventListener('click', e => {
    e.preventDefault();
    localStorage.clear();
    window.location.href = '/login';
});
document.getElementById('cartLink').addEventListener('click', e => {
    e.preventDefault();
    window.location.href = `/cart/${userId}`;
});

let allProducts = [];
let activeCategory = 'all';

async function loadProducts() {
    document.getElementById('loadingSpinner').style.display = 'block';
    try {
        const res = await fetch('/api/products');
        allProducts = await res.json();
        if (allProducts.length === 0) {
            document.getElementById('productsContainer').innerHTML =
                '<p style="text-align:center;font-size:15px;color:var(--text-muted);grid-column:1/-1;padding:40px 0">No products yet. <a href="/seed" style="color:var(--primary)">Seed products</a></p>';
        } else {
            renderProducts(getSorted(allProducts));
        }
    } catch {
        document.getElementById('productsContainer').innerHTML =
            '<p style="text-align:center;color:var(--accent);grid-column:1/-1;padding:40px 0">Failed to load products.</p>';
    }
    document.getElementById('loadingSpinner').style.display = 'none';
}

function starsHtml(rating) {
    const full = Math.floor(rating);
    const half = rating % 1 >= 0.5 ? 1 : 0;
    const empty = 5 - full - half;
    return '★'.repeat(full) + (half ? '½' : '') + '☆'.repeat(empty);
}

function formatPrice(p) {
    return Number(p).toLocaleString('en-IN');
}

function renderProducts(products) {
    const grid = document.getElementById('productsContainer');
    grid.innerHTML = '';
    if (!products.length) {
        grid.innerHTML = '<p style="text-align:center;font-size:15px;color:var(--text-muted);grid-column:1/-1;padding:40px 0">No products in this category.</p>';
        return;
    }
    products.forEach(p => {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.onclick = () => window.location.href = `/product/${p._id}`;

        const isNew = p.reviews_count < 50;
        const badge = isNew
            ? '<span class="product-badge new">New</span>'
            : (p.stock < 10 && p.stock > 0 ? '<span class="product-badge sale">Low Stock</span>' : '');

        card.innerHTML = `
            ${badge}
            <div class="product-image-container">
                <img src="${p.image}" alt="${p.name}" class="product-image"
                     onerror="this.src='https://placehold.co/400x300?text=${encodeURIComponent(p.name)}'">
            </div>
            <div class="product-info">
                <div class="product-brand">${p.brand || 'ShopEasy'}</div>
                <div class="product-name">${p.name}</div>
                <div class="product-rating">
                    <span class="stars">${starsHtml(p.rating || 0)}</span>
                    <span class="rating-count">(${(p.reviews_count || 0).toLocaleString()})</span>
                </div>
                <div class="product-price">
                    <span class="price-currency">₹</span>${formatPrice(p.price)}
                </div>
                <div class="product-stock ${p.stock < 10 ? 'low-stock' : ''}">
                    ${p.stock > 0 ? (p.stock < 10 ? `Only ${p.stock} left` : 'In Stock') : 'Out of Stock'}
                </div>
                <div class="product-actions">
                    <button class="btn-add-cart" onclick="addToCart('${p._id}', event)">Add to Cart</button>
                    <button class="btn-view-details" onclick="event.stopPropagation(); window.location.href='/product/${p._id}'">View</button>
                </div>
            </div>`;
        grid.appendChild(card);
    });
}

function getFiltered() {
    return activeCategory === 'all' ? [...allProducts] : allProducts.filter(p => p.category === activeCategory);
}

function getSorted(products) {
    const val = document.getElementById('sortSelect').value;
    const arr = [...products];
    if (val === 'price_asc')    return arr.sort((a, b) => a.price - b.price);
    if (val === 'price_desc')   return arr.sort((a, b) => b.price - a.price);
    if (val === 'rating_desc')  return arr.sort((a, b) => (b.rating||0) - (a.rating||0));
    if (val === 'rating_asc')   return arr.sort((a, b) => (a.rating||0) - (b.rating||0));
    if (val === 'reviews_desc') return arr.sort((a, b) => (b.reviews_count||0) - (a.reviews_count||0));
    return arr;
}

function applySort() {
    renderProducts(getSorted(getFiltered()));
}

function filterCategory(cat, btn) {
    document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeCategory = cat;
    renderProducts(getSorted(getFiltered()));
}

function searchProducts() {
    const q = document.getElementById('searchInput').value.toLowerCase().trim();
    if (!q) { renderProducts(allProducts); return; }
    const filtered = allProducts.filter(p =>
        p.name.toLowerCase().includes(q) ||
        (p.description || '').toLowerCase().includes(q) ||
        (p.category || '').toLowerCase().includes(q) ||
        (p.brand || '').toLowerCase().includes(q)
    );
    // Reset filter buttons
    document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
    document.querySelector('[data-cat="all"]').classList.add('active');
    activeCategory = 'all';
    renderProducts(getSorted(filtered));
}

document.getElementById('searchInput').addEventListener('keydown', e => {
    if (e.key === 'Enter') searchProducts();
});

async function addToCart(productId, e) {
    e.stopPropagation();
    try {
        const res = await fetch(`/api/basket/${userId}/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId, quantity: 1 })
        });
        const data = await res.json();
        if (res.ok) { showToast('✓ Added to cart'); updateCartCount(); }
        else showToast(data.error || 'Could not add to cart', 'error');
    } catch { showToast('Error adding to cart', 'error'); }
}

async function updateCartCount() {
    try {
        const res = await fetch(`/api/basket/${userId}`);
        const data = await res.json();
        document.getElementById('cartCount').textContent = data.items ? data.items.length : 0;
    } catch {}
}

function showToast(msg, type = 'success') {
    const t = document.createElement('div');
    t.className = 'toast';
    t.textContent = msg;
    t.style.background = type === 'error' ? '#FF6B6B' : '#6C63FF';
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}

loadProducts();
updateCartCount();
