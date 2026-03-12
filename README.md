<div align="center">

# ⚡ ActiveCore — Backend API

**Premium Workout Wear E-Commerce Platform**

[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.x-red?style=for-the-badge)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Stripe](https://img.shields.io/badge/Stripe-Payments-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://stripe.com/)
[![AWS EC2](https://img.shields.io/badge/AWS-EC2-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/ec2/)
[![CI/CD](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/features/actions)

</div>

---

## 📖 Overview

ActiveCore is a full-featured, production-ready **REST API backend** for a premium workout wear e-commerce platform. Built with Django and Django REST Framework, it handles everything from authentication and product management to real-time order notifications and Stripe-powered payments — deployed on AWS EC2 with automated CI/CD.

### 🌐 Live API
> **`https://activecore.duckdns.org`** — Served via Daphne (ASGI) + Nginx with full SSL

---

## ✨ Features

### 🔐 Authentication & Users
- **Cookie-based JWT authentication** — secure HttpOnly cookies (no localStorage exposure)
- **Google OAuth 2.0** social login
- **OTP verification** via Email (SMTP) and WhatsApp (Twilio) for account verify & password reset
- **Role-based access control** — `customer` and `admin` roles with custom permission classes
- Custom `AbstractUser` model with UUID primary keys and Cloudinary profile images
- WebSocket authentication via JWT middleware for Django Channels

### 🛍️ Products
- Full product catalog with categories, product types, variants (size-based), and inventory tracking
- Cloudinary-powered product image management (primary + secondary images with DB constraints)
- Product ratings (1–5 stars) with automatic `ProductMetrics` recalculation via signals
- Featured products list (max 8 enforced at serializer level)
- Advanced product list with filtering by category, size, price range, and sorting (newest, price asc/desc)
- Global search across name, description, category, and product type
- Separate admin and public serializers for fine-grained response control

### 🛒 Cart
- Per-user persistent cart with atomic stock validation using `select_for_update`
- Real-time subtotal, 18% GST, shipping, and total recalculation
- Pre-checkout cart validation — detects stale prices and stock issues before payment
- Full CRUD: add, update quantity, remove item, clear cart, item count

### 💳 Orders & Payments
- **Stripe Payment Intent** integration with webhook event handling
- Support for `ONLINE` and `COD` (Cash on Delivery) payment methods
- Full order lifecycle: `PENDING → CONFIRMED → PROCESSING → SHIPPED → DELIVERED → CANCELLED / FAILED / REFUNDED`
- Order status history tracking with `changed_by` audit trail
- Order expiry management via custom management command (`cancel_expired_orders`)
- Per-user account overview with order statistics

### 🔔 Real-Time Notifications
- **Django Channels** + WebSocket-based push notifications
- Per-user notification groups; notifications persisted to DB
- Admin can broadcast global notifications to all users
- Admin can send targeted notifications to a specific user
- Triggered automatically on order events via Django signals

### ❤️ Wishlist
- Single wishlist per user (auto-created on registration via signals)
- Add/remove items, item count, clear all
- **Price-drop detection** — flags items where current price is below `price_at_added`
- **Move all wishlist items to cart** in one atomic operation

### 📊 Admin & Reports
- Admin APIs for user management: list, search, detail, block/unblock, delete
- Admin product CRUD with full variant and inventory management
- Admin order management: list with filters, search, detail, status update, stats
- Dashboard metrics: total users, revenue, revenue by category, top-selling products/types, order status distribution

### 🔒 Production Security
- HTTPS enforced with HSTS preloading (1 year)
- CSRF and CORS protection with cross-origin cookie support for Vercel frontend
- `X-Frame-Options: DENY`, XSS filter, Content-Type-NoSniff
- `SameSite=None; Secure` cookies for cross-domain authentication

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | Django 6.0, Django REST Framework |
| **Database** | PostgreSQL (via `dj-database-url`) |
| ** Channels** |  Django Channels |
| **ASGI Server** | Daphne |
| **Reverse Proxy** | Nginx + Let's Encrypt SSL |
| **Payments** | Stripe (Payment Intents + Webhooks) |
| **Media Storage** | Cloudinary |
| **Auth** | SimpleJWT (cookie-based, blacklisting), Google OAuth |
| **OTP** | Twilio WhatsApp API + Django SMTP |
| **API Docs** | drf-spectacular (OpenAPI 3 — Swagger + ReDoc) |
| **Deployment** | AWS EC2, GitHub Actions CI/CD |

---

## 📁 Project Structure

```
activecore-backend/
├── core/                        # Django project settings & routing
│   ├── settings/
│   │   ├── base.py              # Shared settings (JWT, DRF, Stripe, Cloudinary, etc.)
│   │   ├── dev.py               # Development overrides
│   │   └── prod.py              # Production security config (HSTS, secure cookies)
│   ├── asgi.py                  # ASGI + WebSocket routing
│   ├── pricing.py               # GST + shipping pricing engine
│   └── urls.py                  # Root URL configuration
│
├── apps/
│   ├── accounts/                # Auth, users, OTP, Google OAuth, address
│   │   ├── authentication.py    # Cookie-based JWT authentication backend
│   │   ├── middleware/          # JWT WebSocket auth middleware
│   │   └── api/
│   │       ├── serializers/     # 8 purpose-built serializers
│   │       └── views/
│   │           ├── admin/       # Admin user management views
│   │           └── public/      # Login, register, OTP, Google auth, me
│   │
│   ├── products/                # Catalog, variants, inventory, ratings
│   │   ├── models.py            # Category, ProductType, Product, Variant, Inventory, Metrics
│   │   ├── signals.py           # Auto-create ProductMetrics on product creation
│   │   └── api/
│   │       ├── serializers/     # 14 purpose-built serializers
│   │       └── views/
│   │           ├── admin/       # Category, ProductType, Product, Variant CRUD
│   │           └── public/      # List, detail, search, featured, ratings
│   │
│   ├── cart/                    # Shopping cart with atomic stock validation
│   │   └── api/views/
│   │       ├── cart_read_views.py
│   │       ├── cart_write_views.py
│   │       ├── cart_meta_views.py
│   │       └── cart_validation_views.py
│   │
│   ├── orders/                  # Checkout, Stripe, webhooks, order lifecycle
│   │   ├── services.py          # OrderService — create, cancel, update status
│   │   └── management/commands/
│   │       └── cancel_expired_orders.py
│   │
│   ├── wishlist/                # Single wishlist per user with price-drop detection
│   ├── notifications/           # WebSocket real-time notifications
│   │   ├── consumers.py         # AsyncWebsocketConsumer
│   │   └── services.py          # notify_user, notify_all_users helpers
│   ├── reports/                 # Admin analytics dashboard
│   └── common/                  # Shared pagination (page_size=12, max=100)
│
├── deploy/
│   ├── nginx.conf               # Nginx reverse proxy + SSL config
│   ├── daphne.service           # Systemd service for Daphne ASGI
│   └── deploy.sh                # Manual deploy script
│
└── .github/
    └── workflows/
        └── deploy.yml           # GitHub Actions CI/CD pipeline
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Cloudinary account
- Stripe account (with webhooks configured)
- Twilio account (for WhatsApp OTP)

### 1. Clone & Install

```bash
git clone https://github.com/adinathmk/activecore-backend.git
cd activecore-backend

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Environment Variables

```bash
cp .env.example .env
```

```env
# Django
DJANGO_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/activecore

# Cloudinary
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your@email.com

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Twilio
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Google OAuth
GOOGLE_CLIENT_ID=...
```

### 3. Database & Static Files

```bash
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
# HTTP only
python manage.py runserver

# With WebSocket support (recommended)
daphne core.asgi:application
```

---

## 🔌 API Reference

All endpoints are prefixed with `/api/`. Interactive docs available at:
- **Swagger UI:** `/api/docs/`
- **ReDoc:** `/api/redoc/`
- **OpenAPI Schema:** `/api/schema/`

**Auth legend:** ❌ Public &nbsp;|&nbsp; ✅ Authenticated &nbsp;|&nbsp; 🔒 Admin only

---

### 🔐 Auth — `/api/auth/`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/register/` | ❌ | Register a new user |
| POST | `/login/` | ❌ | Login — sets HttpOnly JWT cookies |
| POST | `/logout/` | ✅ | Logout and clear auth cookies |
| POST | `/refresh/` | ❌ | Refresh access token using refresh cookie |
| GET | `/me/` | ✅ | Get current user profile + address |
| PATCH | `/me/` | ✅ | Update profile (name, phone, avatar, address) |
| POST | `/send-otp/` | ❌ | Send account verification OTP to email |
| POST | `/verify-otp/` | ❌ | Verify OTP and activate account |
| POST | `/forgot-password/` | ❌ | Send password reset OTP via email or WhatsApp |
| POST | `/reset-password/` | ❌ | Reset password using OTP |
| POST | `/google/` | ❌ | Sign in / register with Google OAuth2 |
| GET | `/admin/users/` | 🔒 | List all users (paginated) |
| GET | `/admin/users/search/` | 🔒 | Search users by name |
| GET | `/admin/users/<uuid>/` | 🔒 | Get detailed user info |
| POST | `/admin/users/<uuid>/block/` | 🔒 | Toggle user active/blocked status |
| DELETE | `/admin/users/<uuid>/delete/` | 🔒 | Delete a user account |

---

### 🛍️ Products — `/api/products/`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | ❌ | List products (paginated, 12 per page) |
| GET | `/?category=<slug>` | ❌ | Filter by category slug |
| GET | `/?size=<S\|M\|L\|XL>` | ❌ | Filter by size |
| GET | `/?min_price=&max_price=` | ❌ | Filter by selling price range |
| GET | `/?sort=newest\|price_asc\|price_desc` | ❌ | Sort products |
| GET | `/search/?q=<query>&limit=<n>` | ❌ | Full-text product search (max 20 results) |
| GET | `/home/featured/` | ❌ | Get featured products (up to 8) |
| GET | `/<slug>/` | ❌ | Product detail with variants, images, features, ratings |
| POST | `/<slug>/rate/` | ✅ | Submit or update a product rating (1–5 stars) |
| GET | `/admin/` | 🔒 | List all products with optional filters |
| POST | `/admin/` | 🔒 | Create new product (multipart/form-data with images) |
| GET | `/admin/<id>/` | 🔒 | Admin product detail |
| PATCH | `/admin/<id>/` | 🔒 | Update product (partial, supports image replacement) |
| DELETE | `/admin/<id>/` | 🔒 | Soft-delete product (sets `is_active=False`) |
| GET | `/admin/search/` | 🔒 | Search products across name, category, type |
| GET | `/admin/categories/` | 🔒 | List all categories |
| POST | `/admin/categories/` | 🔒 | Create new category (auto-generates slug) |
| GET | `/admin/product-types/` | 🔒 | List all product types |
| POST | `/admin/product-types/` | 🔒 | Create new product type |
| GET | `/admin/variants/` | 🔒 | List all variants with inventory |
| POST | `/admin/variants/` | 🔒 | Create a new variant + inventory record |
| GET | `/admin/variants/<id>/` | 🔒 | Get variant detail |
| PATCH / PUT | `/admin/variants/<id>/` | 🔒 | Update variant and stock |
| DELETE | `/admin/variants/<id>/` | 🔒 | Deactivate a variant |

---

### 🛒 Cart — `/api/cart/`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | ✅ | Get cart with all items, subtotal, tax, total |
| GET | `/count/` | ✅ | Get total item quantity in cart |
| POST | `/add/` | ✅ | Add a variant to cart (with stock check) |
| PATCH | `/items/<id>/` | ✅ | Update item quantity (set 0 to remove) |
| DELETE | `/items/<id>/remove/` | ✅ | Remove a specific cart item |
| DELETE | `/clear/` | ✅ | Remove all items from cart |
| POST | `/validate/` | ✅ | Validate cart before checkout (stock + price sync) |

---

### 📦 Orders — `/api/orders/`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/checkout/` | ✅ | Create order from cart (ONLINE or COD) |
| GET | `/` | ✅ | List all orders for current user |
| GET | `/<uuid>/` | ✅ | Order detail with items and status history |
| POST | `/<uuid>/cancel/` | ✅ | Cancel an order |
| GET | `/account-overview/` | ✅ | Summary: total orders, delivered, cancelled, total spent |
| POST | `/<uuid>/create-payment-intent/` | ✅ | Create Stripe Payment Intent for an order |
| POST | `/payments/webhook/` | ❌ | Stripe webhook (handles payment success / failure) |
| GET | `/admin/` | 🔒 | List all orders with filters and ordering |
| GET | `/admin/search/` | 🔒 | Search orders by ID, email, customer name |
| GET | `/admin/<uuid>/` | 🔒 | Admin order detail |
| PATCH | `/admin/<uuid>/update-status/` | 🔒 | Update order status |
| GET | `/admin/stats/` | 🔒 | Order statistics and analytics |

---

### ❤️ Wishlist — `/api/wishlist/`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | ✅ | Get wishlist items (includes `is_price_dropped` flag) |
| DELETE | `/` | ✅ | Clear entire wishlist |
| GET | `/count/` | ✅ | Get wishlist item count |
| POST | `/items/` | ✅ | Add a product variant to wishlist |
| DELETE | `/items/<variant_id>/` | ✅ | Remove a specific item from wishlist |
| POST | `/move-to-cart/` | ✅ | Atomically move all wishlist items to cart |

---

### 🔔 Notifications — `/api/notifications/`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | ✅ | Get notifications (admin can pass `?user_id=<uuid>`) |
| POST | `/send/` | 🔒 | Broadcast notification to all users via WebSocket |
| POST | `/send-user/` | 🔒 | Send notification to a specific user via WebSocket |

**WebSocket Endpoint:** `ws://<host>/ws/notifications/`
- Requires valid `access` JWT cookie
- Joins a per-user channel group (`user_<uuid>`) on connect
- Receives real-time JSON messages on order status changes

---

### 📊 Reports — `/api/reports/`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/dashboard/` | 🔒 | Dashboard: users, revenue, top products/types, order status distribution |

---

## ⚙️ Deployment

### CI/CD Pipeline

Every push to `main` triggers a GitHub Actions workflow that SSHs into the EC2 instance and runs:

```bash
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart daphne
```

### Manual Deploy

```bash
bash deploy/deploy.sh
```

### Infrastructure

```
Internet ──► Nginx (443/SSL) ──► Daphne (127.0.0.1:8001) ──► Django / Channels ->  PostgreSQL
                                   
```

- **Daphne** runs as a `systemd` service bound to `127.0.0.1:8001`
- **Nginx** handles HTTPS termination (Let's Encrypt) and proxies all traffic including WebSocket upgrades

---

## 🔧 Management Commands

```bash
# Cancel unpaid orders that have exceeded their expiry window
python manage.py cancel_expired_orders
```

> Recommended to schedule as a cron job every 5–10 minutes in production.

---

## 🧪 Running Tests

```bash
python manage.py test apps
```

---

## 📦 Key Dependencies

```
Django 6.0
djangorestframework
djangorestframework-simplejwt
django-channels
daphne
drf-spectacular
django-environ
dj-database-url
cloudinary / django-cloudinary-storage
stripe
twilio
phonenumbers
psycopg2-binary
```

---

<div align="center">
  Built with ❤️ for <strong>ActiveCore</strong> — Where performance meets style.
</div>
