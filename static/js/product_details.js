const userId = localStorage.getItem('userId');
if (!userId) window.location.href = '/login';

const urlPath = window.location.pathname;
const productId = urlPath.split('/').pop();

let currentProduct = null;
let selectedSize = '';
let selectedColor = '';
let selectedRating = 0;

document.getElementById('logoutBtn').addEventListener('click', e => {
    e.preventDefault();
    localStorage.clear();
    window.location.href = '/login';
});

document.getElementById('cartLink').addEventListener('click', e => {
    e.preventDefault();
    window.location.href = `/cart/${userId}`;
});

function search() {
    const q = document.getElementById('searchInput').value;
    if (q) window.location.href = `/home?search=${encodeURIComponent(q)}`;
}

document.getElementById('searchInput').addEventListener('keydown', e => {
    if (e.key === 'Enter') search();
});

async function loadProduct() {
    try {
        const res = await fetch(`/api/products/${productId}`);
        if (!res.ok) {
            document.getElementById('loadingSpinner').innerHTML = 'Product not found.';
            return;
        }
        currentProduct = await res.json();
        renderProduct();
        loadReviews();
        updateCartCount();
    } catch (err) {
        document.getElementById('loadingSpinner').innerHTML = 'Error loading product.';
    }
}

function renderProduct() {
    document.getElementById('loadingSpinner').style.display = 'none';
    document.getElementById('productContent').style.display = 'block';
    
    const p = currentProduct;
    
    document.getElementById('productImage').src = p.image || 'https://via.placeholder.com/600x600?text=No+Image';
    document.getElementById('productName').textContent = p.name;
    document.getElementById('productBrand').textContent = p.brand || 'Generic';
    document.getElementById('productDescription').textContent = p.description || 'No description available.';
    
    const price = formatPrice(p.price);
    document.getElementById('productPrice').textContent = price;
    document.getElementById('buyBoxPrice').textContent = price;
    
    // Rating
    const rating = p.rating || 0;
    const reviewCount = p.reviews_count || 0;
    const fullStars = Math.floor(rating);
    const halfStar = rating % 1 >= 0.5 ? 1 : 0;
    const emptyStars = 5 - fullStars - halfStar;
    const starsHtml = '★'.repeat(fullStars) + (halfStar ? '⯨' : '') + '☆'.repeat(emptyStars);
    
    document.getElementById('productStars').textContent = starsHtml;
    document.getElementById('ratingText').textContent = `${rating.toFixed(1)} out of 5 (${reviewCount.toLocaleString()} ratings)`;
    
    // Stock
    const stockEl = document.getElementById('stockStatus');
    if (p.stock > 0) {
        stockEl.textContent = `In Stock (${p.stock} available)`;
        stockEl.className = 'stock-status';
    } else {
        stockEl.textContent = 'Currently unavailable';
        stockEl.className = 'stock-status out-of-stock';
        document.getElementById('addToCartBtn').disabled = true;
        document.getElementById('addToCartBtn').textContent = 'Out of Stock';
    }
    
    // Size Selection (for clothing)
    if (p.sizes && p.sizes.length > 0) {
        document.getElementById('sizeGroup').style.display = 'block';
        const sizeSelect = document.getElementById('sizeSelect');
        sizeSelect.innerHTML = '<option value="">Choose a size</option>';
        p.sizes.forEach(size => {
            const opt = document.createElement('option');
            opt.value = size;
            opt.textContent = size;
            sizeSelect.appendChild(opt);
        });
        sizeSelect.addEventListener('change', e => {
            selectedSize = e.target.value;
        });
    }
    
    // Color Selection
    if (p.colors && p.colors.length > 0) {
        document.getElementById('colorGroup').style.display = 'block';
        const colorButtons = document.getElementById('colorButtons');
        colorButtons.innerHTML = '';
        p.colors.forEach(color => {
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            btn.textContent = color;
            btn.onclick = () => {
                document.querySelectorAll('#colorButtons .option-btn').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                selectedColor = color;
            };
            colorButtons.appendChild(btn);
        });
        // Auto-select first color
        if (p.colors.length > 0) {
            colorButtons.firstChild.click();
        }
    }
}

function formatPrice(price) {
    return price.toLocaleString('en-IN');
}

async function addToCart() {
    // Validate selections
    if (currentProduct.sizes && currentProduct.sizes.length > 0 && !selectedSize) {
        showToast('Please select a size', 'error');
        return;
    }
    
    if (currentProduct.colors && currentProduct.colors.length > 0 && !selectedColor) {
        showToast('Please select a color', 'error');
        return;
    }
    
    const quantity = parseInt(document.getElementById('quantity').value);
    
    try {
        const res = await fetch(`/api/basket/${userId}/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                product_id: productId, 
                quantity,
                size: selectedSize,
                color: selectedColor
            })
        });
        const data = await res.json();
        if (res.ok) {
            showToast('Added to cart!', 'success');
            updateCartCount();
        } else {
            showToast(data.error || 'Could not add to cart', 'error');
        }
    } catch {
        showToast('Error adding to cart', 'error');
    }
}

function buyNow() {
    addToCart();
    setTimeout(() => {
        window.location.href = `/cart/${userId}`;
    }, 500);
}

async function updateCartCount() {
    try {
        const res = await fetch(`/api/basket/${userId}`);
        const data = await res.json();
        document.getElementById('cartCount').textContent = data.items ? data.items.length : 0;
    } catch {}
}

// Reviews
async function loadReviews() {
    try {
        const res = await fetch(`/api/products/${productId}/reviews`);
        const data = await res.json();
        const list = document.getElementById('reviewsList');
        if (!data.reviews || data.reviews.length === 0) {
            list.innerHTML = '<div class="no-reviews"><p>No reviews yet. Be the first to review this product!</p></div>';
            return;
        }
        list.innerHTML = data.reviews.map(r => {
            const stars = '★'.repeat(r.rating) + '☆'.repeat(5 - r.rating);
            return `
            <div class="review-item">
                <div class="review-header">
                    <span class="review-stars">${stars}</span>
                    <span class="review-title">${r.title || ''}</span>
                </div>
                <div class="review-meta">${new Date(r.created_at).toLocaleDateString('en-IN', {day: 'numeric', month: 'long', year: 'numeric'})}</div>
                <div class="review-text">${r.text}</div>
            </div>`;
        }).join('');
    } catch {
        document.getElementById('reviewsList').innerHTML = '<div class="no-reviews"><p>Could not load reviews.</p></div>';
    }
}

function openReviewModal() {
    document.getElementById('reviewModal').style.display = 'block';
    selectedRating = 0;
    document.querySelectorAll('.star').forEach(s => s.classList.remove('active'));
    document.getElementById('reviewTitle').value = '';
    document.getElementById('reviewText').value = '';
}

function closeReviewModal() {
    document.getElementById('reviewModal').style.display = 'none';
}

// Star rating interaction
document.querySelectorAll('.star').forEach(star => {
    star.addEventListener('click', function() {
        selectedRating = parseInt(this.dataset.rating);
        document.getElementById('rating').value = selectedRating;
        document.querySelectorAll('.star').forEach((s, i) => {
            s.classList.toggle('active', i < selectedRating);
        });
    });
    star.addEventListener('mouseover', function() {
        const r = parseInt(this.dataset.rating);
        document.querySelectorAll('.star').forEach((s, i) => {
            s.style.color = i < r ? '#FFA41C' : '#ddd';
        });
    });
    star.addEventListener('mouseout', function() {
        document.querySelectorAll('.star').forEach((s, i) => {
            s.style.color = i < selectedRating ? '#FFA41C' : '#ddd';
        });
    });
});

document.getElementById('reviewForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    if (!selectedRating) {
        showToast('Please select a star rating', 'error');
        return;
    }

    const payload = {
        user_id: userId,
        rating: selectedRating,
        title: document.getElementById('reviewTitle').value,
        text: document.getElementById('reviewText').value
    };

    try {
        const res = await fetch(`/api/products/${productId}/reviews`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok) {
            closeReviewModal();
            showToast('Review submitted successfully!', 'success');
            loadReviews();
            // Reload product to update rating
            setTimeout(() => loadProduct(), 500);
        } else {
            showToast(data.error || 'Failed to submit review', 'error');
        }
    } catch {
        showToast('Error submitting review', 'error');
    }
});

window.onclick = e => {
    if (e.target === document.getElementById('reviewModal')) closeReviewModal();
};

function showToast(msg, type = 'success') {
    const t = document.createElement('div');
    t.className = 'toast';
    t.textContent = msg;
    t.style.background = type === 'error' ? '#C40000' : '#067D62';
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}

loadProduct();
