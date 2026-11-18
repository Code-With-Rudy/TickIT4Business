# 🎟️ Tick.IT: QR Tickets for Any Local Business
 
**One QR. Any local business.**
 
Tick.IT is a lightweight, mobile-first ticketing platform for small businesses such as eco parks, temples, parking lots, auto/ride services and local events. Owners create ticket "services", share a QR code or WhatsApp link, and validate entries at the gate. Customers scan, pay from a wallet, and get a ticket QR in seconds. No hardware, no POS machine and no paper tickets are needed.
 
---
 
## 📑 Table of Contents
 
1. [Uses](#-uses)
2. [Why It's Useful](#-why-its-useful)
3. [Features](#-features)
4. [Advantages](#-advantages)
5. [Tech Stack](#-tech-stack)
6. [How It Works](#-how-it-works)
7. [Backend Logic](#-backend-logic)
8. [API Reference](#-api-reference)
9. [Project Structure](#-project-structure)
10. [Getting Started](#-getting-started)
11. [Testing](#-testing)
12. [Security Notes](#-security-notes)
13. [Known Limitations](#-known-limitations)
---
 
## 🧭 Uses
 
Tick.IT fits any business that sells a time-limited, one-time-use entry or service:
 
| Category | Example services |
|---|---|
| 🌳 Park / Attraction | Adult entry ₹50, Child entry ₹20, Boating ₹100 |
| 🛕 Temple / Religious | Darshan pass, special pooja entry |
| 🅿️ Parking | 2-hour parking ₹30, All-day parking ₹100 |
| 🛺 Ride / Transport | Auto ride ₹25 (valid 30 min) |
| 🎪 Event | Fair entry, workshop or concert pass |
| 🏪 Other | Any business that needs a validated, single-use ticket |
 
---
 
## 💡 Why It's Useful
 
Many small local businesses still rely on paper tickets, cash handling and manual counting. This causes:
 
- **Revenue leakage:** duplicated or reused paper tickets.
- **Queues:** staff spend time handing out tickets and making change.
- **No records:** owners can't see sales, footfall or peak times.
- **High entry cost:** proper ticketing systems need expensive hardware.
Tick.IT solves this with just a smartphone. The owner prints one QR poster, or shares one link on WhatsApp. Customers handle the rest themselves, and each ticket can be redeemed **only once**.
 
---
 
## ✨ Features
 
### For Business Owners
- 🏢 Business sign-up with a name and category
- 🧾 **Multiple services per business**, each with its own ID (e.g. `PRK-7K3QM2`), price and validity
- 🔗 Per-service **booking link + QR code**, plus an **all-services page** link per business
- 📲 One-tap **WhatsApp / native share**, with copy link
- 🖨️ **Printable poster** for the entrance, counter or vehicle
- ⬇️ **Download QR** as PNG or SVG
- ⏸️ **Pause / resume** a service without deleting it (history stays intact)
- 📷 **Gate validation** by camera scan or an 8-character backup code
- ✅ Clear result screens: `VALID - Redeemed, ADMIT N`, `ALREADY USED`, `EXPIRED`, `INVALID`
- 📊 Dashboard with total earnings, today's revenue, unused tickets, customers, revenue per customer, and used/expired counts
- 🔔 Browser notifications for new ticket sales
### For Customers
- 🔍 Open a service by **scanning a QR** (in-app scanner or phone camera), **clicking a shared link**, or **typing the service ID**
- 🔐 Email/password or **Continue with Google** sign-in
- 🔁 After login, return straight to the shared service (safe `next=` redirect)
- 👛 Wallet with a welcome balance (demo) and top-up
- 🎫 Book **1–10 admissions** in one purchase
- 📱 Ticket with QR, backup code, live countdown and expiry time
- 🗂️ Ticket history with filters: All / Valid / Used / Expired
### General
- 🌗 **Light and dark mode** (follows the device; the toggle is remembered)
- 📱 Responsive, mobile-first UI
- 🛡️ Hardened security (see [Security Notes](#-security-notes))
---
 
## 🏆 Advantages
 
- **Zero hardware:** works on any smartphone with a camera.
- **Works with any phone camera:** the QR holds a normal URL, so customers don't need the app first.
- **Change prices without reprinting:** QR codes never contain a price, only the service link.
- **Fraud-resistant:** tickets are consumed atomically, so two simultaneous scans can never both succeed.
- **Server-trusted pricing:** totals are computed on the server and the client can't tamper with them.
- **Fast onboarding:** an owner can go from sign-up to a printable QR poster in about a minute.
- **Serverless and cheap to run:** Vercel + Firestore scale to zero when idle.
- **No frameworks on the frontend:** plain HTML/CSS/JS loads fast on slow mobile networks.
- **Strict CSP:** no inline scripts anywhere.
---
 
## 🛠️ Tech Stack
 
| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3 (custom design system with light/dark theming), Vanilla JavaScript (ES modules for Google auth) |
| **Backend** | Python 3, **Flask** (REST API) |
| **Database** | **Google Cloud Firestore** (via Firebase Admin SDK) |
| **Auth** | PyJWT (HS256 session tokens), Werkzeug password hashing, **Firebase Auth** (Google Sign-In, ID token verified server-side) |
| **QR generation** | [`qrcode-generator`](https://github.com/kazuhikoarase/qrcode-generator) (renders vector SVG and PNG) |
| **QR scanning** | [`html5-qrcode`](https://github.com/mebjas/html5-qrcode) (camera scanner) |
| **Rate limiting** | Flask-Limiter (in-memory by default, Redis recommended) |
| **Hosting** | **Vercel** (`@vercel/python` serverless function + `@vercel/static`) |
| **Testing** | Plain Python test scripts, in-memory fake Firestore, **Playwright** for browser E2E |
 
---
 
## 🔄 How It Works
 
```
 OWNER                                              CUSTOMER
 ─────                                              ────────
 1. Sign up (business + category)
 2. Add services  ──► each gets ID + QR + link
 3. Print poster / share on WhatsApp  ───────────►  4. Scan QR / open link / type ID
                                                    5. Log in or sign up
                                                    6. Pick quantity (1–10), pay from wallet
                                                    7. Receive ticket QR + 8-char code
 8. Scan ticket QR (or type code)  ◄───────────────  (show ticket at the gate)
 9. Screen: "VALID – Redeemed, ADMIT 3"
10. Scanning again: "ALREADY USED"
```
 
---
 
## ⚙️ Backend Logic
 
All backend code lives in [`api/main.py`](api/main.py).
 
### 1. Data Model
 
| Collection | Purpose | Key fields |
|---|---|---|
| `users` | Customers | `email`, `fullName`, `passwordHash`, `walletBalance`, `failedLoginAttempts`, `lockoutUntil`, `authProvider` |
| `owners` | Businesses | `businessName`, `category`, `bizCode`, `totalEarnings`, `passwordHash`, lockout fields |
| `services` | Things an owner sells (doc ID = service ID) | `ownerId`, `name`, `description`, `price`, `validityMinutes`, `active`, `category` |
| `tickets` | One purchase of N admissions | `customerId`, `ownerId`, `serviceId`, `quantity`, `unitPrice`, `farePaid`, `status`, `issuedAt`, `expiresAt`, `validatedAt`, `code` |
 
Ticket documents store a **snapshot** of the service name and business name, so later edits don't rewrite history.
 
### 2. ID Generation
 
- **Service IDs:** `<PREFIX>-<6 chars>`, e.g. `PRK-7K3QM2`. The prefix comes from the category (`PRK` park, `TMP` temple, `PKG` parking, `RDE` ride, `EVT` event, `SVC` other).
- The random part uses `secrets.choice` over `ABCDEFGHJKLMNPQRSTUVWXYZ23456789`, which excludes the confusable characters `0`, `O`, `1` and `I`.
- **Collision check:** up to 10 attempts against Firestore before failing.
- **Business code:** a 6-character code used for the all-services link (`book.html?b=CODE`).
- **Ticket backup code:** 8 characters derived from the ticket's UUID.
### 3. Authentication & Sessions
 
- **Password accounts:** hashed with Werkzeug (`generate_password_hash`). Minimum length is 8 and maximum is 128.
- **Google accounts:**
  1. The browser signs in via Firebase and gets an ID token.
  2. The server verifies it with `firebase_admin.auth.verify_id_token`.
  3. It requires `sign_in_provider == google.com` and `email_verified == true`.
  4. The token is exchanged for a Tick.IT JWT. Firebase is only used to prove identity.
  5. An existing account with the same verified email is reused; otherwise a new one is created. Owners must provide business details first.
- **Session token:** JWT (HS256, 8-hour lifetime) containing `userId` and `role`. It is sent as `Authorization: Bearer <token>`.
- **Role guard:** the `@token_required("customer")` / `@token_required("owner")` decorators enforce roles.
- **Anti-IDOR:** the acting user always comes from the token. Endpoints with a path ID run `require_self()`, so changing an ID in the URL returns `403`.
### 4. Brute-Force Protection (Login Lockout)
 
- Wrong password: `401` with "N attempt(s) remaining".
- **3 failures: `429`, locked for 1 hour.** Even the correct password is rejected during the lock.
- When a lock expires, the counter restarts.
- The counter update runs in a **Firestore transaction**, so parallel guesses can't bypass it.
- If the email doesn't exist, a **dummy hash check** runs so response timing doesn't reveal which emails are registered.
- Google accounts don't use password lockout.
### 5. Payment Flow (`POST /api/pay`)
 
Debiting the customer, crediting the owner and creating the ticket happen in **one atomic Firestore transaction**:
 
1. Validate `serviceId` format and `quantity` (1–10).
2. Read user, service and owner inside the transaction.
3. Verify the service belongs to the owner and is `active`.
4. **Compute `total = price × quantity` on the server.** Any client-sent price is ignored.
5. Reject if `walletBalance < total`.
6. Debit the wallet, add to the owner's `totalEarnings`, and create the ticket with `expiresAt = now + validityMinutes`.
Free services (price `0`) work the same way and don't touch the wallet.
 
### 6. Ticket Redemption (`POST /api/tickets/verify`)
 
A ticket can be redeemed by **scanning the QR** (`{ticketId, customerId}`) or by the **8-character code**. The check-and-consume step runs in a transaction, so two simultaneous scans can never both succeed.
 
| Situation | HTTP | Result |
|---|---|---|
| Ticket not found | 404 | `INVALID` |
| Ticket belongs to another business | 403 | `INVALID` |
| QR's customer doesn't match | 400 | `INVALID` |
| Already redeemed | 409 | `USED` |
| Past `expiresAt` | 410 | `EXPIRED` (not consumed) |
| Valid | 200 | `VALID`, marked `USED`, response includes `quantity` for "ADMIT N" |
 
Ticket state is derived as `VALID | USED | EXPIRED`. Expiry is computed from `expiresAt` at read time, so no background job is needed.
 
### 7. Services
 
- Price: `0 – 100000` (₹). Validity: `5 minutes – 30 days`. Quantity: `1 – 10` per booking.
- Up to **50 services per owner**.
- Services are **paused, never deleted**, so ticket history stays intact.
- An owner can only update their own services. Others get `404`.
### 8. Input Sanitisation
 
- `clean_text()` strips HTML tags and control characters from names, descriptions and business names, and enforces length limits.
- Email addresses are normalised (lowercased and regex-checked).
- All times are stored and returned in **UTC** (ISO strings ending in `Z`).
- The frontend also escapes any user text before it reaches `innerHTML`.
### 9. Rate Limiting & Hardening
 
- Default limit is 300 requests/hour per IP, with tighter limits on sensitive routes (for example registration is 10/hour and login is 20/minute).
- Request bodies are capped at 64 KB.
- API responses send `Cache-Control: no-store` and a locked-down CSP.
- JSON error handlers cover 404, 405, 413 and 429.
---
 
## 📡 API Reference
 
All routes are under `/api`. "Auth" means `Authorization: Bearer <token>` is required.
 
### Public (no login)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/register/user` | Create a customer account |
| `POST` | `/register/owner` | Create a business account |
| `POST` | `/login/user` | Customer login |
| `POST` | `/login/owner` | Owner login |
| `POST` | `/auth/google` | Exchange a Firebase Google ID token for a session |
| `GET` | `/public/service/<serviceId>` | Public service details (for booking pages and QR codes) |
| `GET` | `/public/business/<bizCode>` | Business info plus its active services |
 
### Customer (Auth)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/get-user-details/<uid>` | Profile and wallet balance |
| `GET` | `/get-user-tickets/<uid>` | All tickets, newest first |
| `POST` | `/pay` | Buy tickets: `{serviceId, quantity}` |
| `POST` | `/add-funds` | Demo wallet top-up (max ₹10,000 per request) |
 
### Owner (Auth)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/get-owner-details/<uid>` | Business profile and earnings |
| `GET` | `/owner/services` | List my services |
| `POST` | `/owner/services` | Create a service |
| `PATCH` | `/owner/services/<serviceId>` | Edit or pause/resume a service |
| `GET` | `/get-owner-tickets/<uid>` | Tickets sold, with customer names |
| `POST` | `/sync-owner-earnings/<uid>` | Recompute earnings from tickets |
| `POST` | `/tickets/verify` | Redeem a ticket (QR or code) |
 
### Shared (Auth, customer or owner)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/check-ticket-validity/<ticketId>` | Read-only ticket status (doesn't redeem) |
 
---
 
## 📁 Project Structure
 
```
tickit/
├── api/
│   └── main.py              # Flask backend (all API logic)
├── public/
│   ├── index.html           # Landing + login / sign-up (customer & owner)
│   ├── book.html            # Public booking page (?s=SERVICEID or ?b=BIZCODE)
│   ├── dashboard.html       # Customer dashboard
│   ├── owner_dashboard.html # Business dashboard
│   ├── uber.css             # Design system (light + dark themes)
│   └── js/
│       ├── common.js        # API wrapper, session, QR render, scanner helpers
│       ├── theme.js         # Light/dark theme toggle
│       ├── index.js         # Auth forms
│       ├── google-auth.js   # Google Sign-In via Firebase
│       ├── firebase-config.js
│       ├── book.js          # Booking flow
│       ├── dashboard.js     # Customer dashboard logic
│       └── owner.js         # Owner dashboard logic
├── tests/
│   ├── test_backend.py      # API tests (in-memory Firestore)
│   └── e2e_browser.py       # Playwright browser E2E test
├── firestore.rules          # Deny-all: only the backend touches the DB
├── vercel.json              # Routing + security headers (CSP, HSTS, etc.)
├── requirements.txt
├── .env.example
├── SETUP.md                 # Detailed deployment checklist
└── README.md
```
 
---
 
## 🚀 Getting Started
 
### Prerequisites
- Python 3.9+
- A Firebase project (Firestore enabled, Google sign-in enabled)
- A Vercel account (for deployment)
### 1. Clone and install
```bash
git clone <your-repo-url>
cd tickit
pip install -r requirements.txt
```
 
### 2. Configure environment
Copy `.env.example` to `.env` and fill it in:
 
| Variable | Required | Description |
|---|---|---|
| `JWT_SECRET` | ✅ | Generate with `python -c "import secrets;print(secrets.token_hex(32))"` |
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | ✅ on Vercel | Entire Firebase service-account JSON on **one line**. Locally you can use `serviceAccountKey.json` in the project root. |
| `RATELIMIT_STORAGE_URI` | Recommended | Shared rate-limit store, e.g. a Redis/Upstash URL |
| `ALLOWED_ORIGINS` | Optional | Only if the frontend is served from a different origin |
 
### 3. Firebase setup
1. Create a Firestore database (production mode) and publish the rules from `firestore.rules`.
2. Generate a service-account key (Project settings → Service accounts).
3. Add a Web app, then paste its config into `public/js/firebase-config.js`.
4. Enable **Google** under Authentication → Sign-in method.
5. Add your domain under Authentication → Settings → Authorized domains.
### 4. Run locally
```bash
npm i -g vercel
vercel dev
```
This serves both the static `public/` files and the Flask API as Vercel would. Camera scanning needs HTTPS (`localhost` also works).
 
### 5. Deploy
Push to GitHub, import the repo into Vercel, add the environment variables, then deploy. See [`SETUP.md`](SETUP.md) for the full checklist.
 
---
 
## 🧪 Testing
 
```bash
# API tests: in-memory Firestore, no Firebase needed
python tests/test_backend.py
 
# Browser E2E: owner sign-up → services → customer purchase → gate validation → dark mode
pip install playwright && playwright install chromium
python tests/e2e_browser.py
```
 
The backend tests cover registration, lockout, auth enforcement, IDOR protection, service CRUD, payments, redemption (valid, used, expired), and Google sign-in. The E2E test stubs the QR CDN library, so it verifies UI flows rather than real QR decoding.
 
---
 
## 🔒 Security Notes
 
- **Firestore is closed to browsers.** `firestore.rules` denies all direct access, and only the backend (Admin SDK) reads and writes.
- **Strict CSP** (via `vercel.json`) with no inline scripts, plus HSTS, `X-Frame-Options: DENY`, `nosniff`, a restrictive Referrer-Policy and Permissions-Policy.
- **Session tokens live in `sessionStorage`** (cleared when the tab closes), not `localStorage`.
- **Open-redirect protection:** the post-login `next=` parameter is only accepted if it matches a booking-page pattern.
- **Server-side price calculation**, atomic transactions, and password hashing with a dummy-hash timing defence.
- The Firebase web config in `firebase-config.js` is safe to be public. It identifies the project and isn't a secret. **Never commit** `serviceAccountKey.json` or `.env` (both are in `.gitignore`).
---
 
## ⚠️ Known Limitations
 
- **Add funds is a demo.** There is no real payment gateway. Integrate Razorpay, Stripe or UPI before going live with real money.
- **Rate limiting** uses per-instance memory by default. Set `RATELIMIT_STORAGE_URI` (Redis) in production.
- The wallet welcome bonus (₹500) is for demo purposes.
---
 
## 📄 License
 

 
---
 
<p align="center">Built for the small businesses that keep local life running. 🎟️</p>
 
