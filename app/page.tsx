import React from "react";

export default function Home() {
  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#f5f5f5" }}>
      {/* Header */}
      <header
        style={{
          backgroundColor: "#fff",
          boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
        }}
      >
        <div
          style={{
            maxWidth: "1200px",
            margin: "0 auto",
            padding: "1rem 2rem",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <h1 style={{ fontSize: "1.5rem", fontWeight: "bold" }}>
            🛍️ E-Commerce Store
          </h1>
          <nav style={{ display: "flex", gap: "2rem" }}>
            <a href="/" style={{ color: "#333", textDecoration: "none" }}>
              Home
            </a>
            <a href="/search" style={{ color: "#333", textDecoration: "none" }}>
              Search
            </a>
            <a
              href="/recommendations"
              style={{ color: "#333", textDecoration: "none" }}
            >
              Recommendations
            </a>
            <a href="/cart" style={{ color: "#333", textDecoration: "none" }}>
              Cart
            </a>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: "1200px", margin: "0 auto", padding: "2rem" }}>
        {/* Hero Section */}
        <section
          style={{
            backgroundColor: "#fff",
            padding: "3rem",
            borderRadius: "8px",
            marginBottom: "2rem",
            textAlign: "center",
          }}
        >
          <h2 style={{ fontSize: "2rem", marginBottom: "1rem" }}>
            Welcome to Our AI-Powered Store
          </h2>
          <p
            style={{ fontSize: "1.1rem", color: "#666", marginBottom: "2rem" }}
          >
            Experience the future of shopping with natural language search, AI
            recommendations, and smart comparisons.
          </p>
          <a
            href="/search"
            style={{
              display: "inline-block",
              backgroundColor: "#007bff",
              color: "#fff",
              padding: "0.75rem 1.5rem",
              borderRadius: "4px",
              textDecoration: "none",
              fontSize: "1rem",
              cursor: "pointer",
            }}
          >
            Start Shopping
          </a>
        </section>

        {/* Features Grid */}
        <section
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
            gap: "2rem",
            marginBottom: "2rem",
          }}
        >
          {/* Feature 1 */}
          <div
            style={{
              backgroundColor: "#fff",
              padding: "2rem",
              borderRadius: "8px",
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
            }}
          >
            <h3 style={{ fontSize: "1.3rem", marginBottom: "1rem" }}>
              🔍 Natural Language Search
            </h3>
            <p style={{ color: "#666" }}>
              Search products using simple, everyday language like "gaming
              laptop under ₹80k" and get AI-powered results.
            </p>
          </div>

          {/* Feature 2 */}
          <div
            style={{
              backgroundColor: "#fff",
              padding: "2rem",
              borderRadius: "8px",
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
            }}
          >
            <h3 style={{ fontSize: "1.3rem", marginBottom: "1rem" }}>
              💡 Smart Recommendations
            </h3>
            <p style={{ color: "#666" }}>
              Get personalized product recommendations based on your browsing
              and purchase history.
            </p>
          </div>

          {/* Feature 3 */}
          <div
            style={{
              backgroundColor: "#fff",
              padding: "2rem",
              borderRadius: "8px",
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
            }}
          >
            <h3 style={{ fontSize: "1.3rem", marginBottom: "1rem" }}>
              ⚖️ Product Comparison
            </h3>
            <p style={{ color: "#666" }}>
              Compare multiple products with AI-generated insights to help you
              make the best choice.
            </p>
          </div>

          {/* Feature 4 */}
          <div
            style={{
              backgroundColor: "#fff",
              padding: "2rem",
              borderRadius: "8px",
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
            }}
          >
            <h3 style={{ fontSize: "1.3rem", marginBottom: "1rem" }}>
              ⭐ Review Summaries
            </h3>
            <p style={{ color: "#666" }}>
              Get AI-summarized reviews that highlight key points, pros, and
              cons at a glance.
            </p>
          </div>

          {/* Feature 5 */}
          <div
            style={{
              backgroundColor: "#fff",
              padding: "2rem",
              borderRadius: "8px",
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
            }}
          >
            <h3 style={{ fontSize: "1.3rem", marginBottom: "1rem" }}>
              🚀 Fast & Reliable
            </h3>
            <p style={{ color: "#666" }}>
              Powered by modern AI and optimized databases for lightning-fast
              results.
            </p>
          </div>

          {/* Feature 6 */}
          <div
            style={{
              backgroundColor: "#fff",
              padding: "2rem",
              borderRadius: "8px",
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
            }}
          >
            <h3 style={{ fontSize: "1.3rem", marginBottom: "1rem" }}>
              💳 Secure Checkout
            </h3>
            <p style={{ color: "#666" }}>
              Shop with confidence using our secure payment processing system.
            </p>
          </div>
        </section>

        {/* API Status Section */}
        <section
          style={{
            backgroundColor: "#fff",
            padding: "2rem",
            borderRadius: "8px",
            marginBottom: "2rem",
          }}
        >
          <h3 style={{ fontSize: "1.3rem", marginBottom: "1rem" }}>
            🔧 API Status
          </h3>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: "1rem",
            }}
          >
            <div
              style={{
                padding: "1rem",
                backgroundColor: "#f0f0f0",
                borderRadius: "4px",
              }}
            >
              <p>
                <strong>Backend API:</strong> http://localhost:5000
              </p>
              <p style={{ color: "#28a745", fontSize: "0.9rem" }}>
                ✅ Running (Flask)
              </p>
            </div>
            <div
              style={{
                padding: "1rem",
                backgroundColor: "#f0f0f0",
                borderRadius: "4px",
              }}
            >
              <p>
                <strong>Database:</strong> MongoDB
              </p>
              <p style={{ color: "#28a745", fontSize: "0.9rem" }}>
                ✅ Connected
              </p>
            </div>
            <div
              style={{
                padding: "1rem",
                backgroundColor: "#f0f0f0",
                borderRadius: "4px",
              }}
            >
              <p>
                <strong>AI Engine:</strong> Gemini API
              </p>
              <p style={{ color: "#28a745", fontSize: "0.9rem" }}>
                ✅ Configured
              </p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer
        style={{
          backgroundColor: "#333",
          color: "#fff",
          textAlign: "center",
          padding: "2rem",
          marginTop: "2rem",
        }}
      >
        <p>&copy; 2024 E-Commerce Store. Powered by AI. All rights reserved.</p>
        <p style={{ fontSize: "0.9rem", color: "#aaa", marginTop: "0.5rem" }}>
          <a href="/search" style={{ color: "#aaa", textDecoration: "none" }}>
            Search
          </a>{" "}
          |
          <a
            href="/recommendations"
            style={{ color: "#aaa", textDecoration: "none" }}
          >
            {" "}
            Recommendations
          </a>{" "}
          |
          <a href="/compare" style={{ color: "#aaa", textDecoration: "none" }}>
            {" "}
            Compare
          </a>
        </p>
      </footer>
    </div>
  );
}
