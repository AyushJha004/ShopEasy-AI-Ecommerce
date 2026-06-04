# 🛒 ShopEasy - Quick Start Guide

## ✅ Your site is now ready!

### 🚀 How to Use:

1. **First Time Setup:**
   - Your Flask app is already running at http://127.0.0.1:5000
   - Visit http://127.0.0.1:5000/seed to create sample products (24 products across 6 categories)
   - Or just go to http://127.0.0.1:5000 and it will redirect you to login

2. **Create an Account:**
   - Go to http://127.0.0.1:5000/signup
   - Fill in your details (First Name, Last Name, Email, Phone, Password)
   - Click "Sign Up"
   - You'll be redirected to login

3. **Login:**
   - Use your email and password
   - Click "Login"
   - You'll be taken to the home page

4. **Browse Products:**
   - View all products or filter by category:
     - ⚡ Electronics (headphones, smartphones, TVs, keyboards)
     - 👕 Clothes (jackets, shoes, dresses, sweaters)
     - 🧸 Toys (LEGO, RC cars, teddy bears, board games)
     - 🎨 Paintings (canvas art, prints, oil paintings, paint sets)
     - 🍎 Food (chocolate, tea, pasta, trail mix)
     - ⚽ Sports (basketball, yoga mat, dumbbells, tennis racket)
   - Search products using the search bar
   - Click "Add to Cart" to add items
   - Click "View" to see product details and reviews

5. **Shopping Cart:**
   - Click the cart icon in navigation
   - Increase/decrease quantities with +/- buttons
   - Remove items you don't want
   - Click "Proceed to Checkout"

6. **Checkout:**
   - Enter delivery address
   - Select payment method
   - Review total (includes 10% tax)
   - Click "Place Order"
   - Get order confirmation!

7. **Write Reviews:**
   - In your cart, click "Review" button on any item
   - Give a star rating (1-5 stars)
   - Write a review title and text
   - Submit your review
   - Reviews will appear on the product details page

## 📁 File Structure:

```
templates/
  ├── login.html      # Login page
  ├── signup.html     # Sign up page
  ├── index.html      # Home page with products
  ├── cart.html       # Shopping cart & checkout
  ├── about.html      # About page
  └── seed.html       # Database seed page

static/
  ├── css/
  │   └── style.css   # All styling
  └── js/
      ├── login.js    # Login functionality
      ├── signup.js   # Signup functionality
      ├── home.js     # Product listing & filtering
      └── cart.js     # Cart & checkout logic
```

## 🎨 ShopEasy Logo:

The green checkmark box logo appears on every page in the top left corner.

## 💾 Database:

All data is stored in MongoDB:
- Users (authentication)
- Products (inventory)
- Cart/Basket (shopping cart)
- Orders (purchase history)
- Reviews (product reviews)

## 🔧 Features Included:

✅ User Registration & Login  
✅ Product Browsing with Categories  
✅ Search Functionality  
✅ Add to Cart  
✅ Increment/Decrement Quantities  
✅ Remove from Cart  
✅ Checkout with Address & Payment  
✅ Order Placement  
✅ Product Reviews with Star Ratings  
✅ Responsive Design  
✅ Modern UI with Animations  
✅ Toast Notifications  

## 🌐 Navigation:

- **Home** - Browse all products
- **About** - Information about ShopEasy
- **Cart** - View cart and checkout
- **Logout** - End session

---

**Enjoy shopping at ShopEasy! 🎉**
