# 🚀 Cloud Deployment Guide: Render & Firebase Hosting

This guide provides step-by-step instructions to deploy the **School Lost & Found Management System** to both **Render** and **Firebase Hosting**.

---

## 🌐 Live Deployments
* **Dynamic Python Flask App (Render):** [https://school-lost-and-found-vboh.onrender.com](https://school-lost-and-found-vboh.onrender.com)
* **Firebase CDN Portal:** [https://school-lost-found-2026.web.app](https://school-lost-found-2026.web.app)
* **GitHub Repository:** [https://github.com/Manvik2009/school-lost---found](https://github.com/Manvik2009/school-lost---found)

---

## 📑 Quick Navigation
1. [Dual-Database Architecture (Zero-Crash Cloud Deploy)](#1-dual-database-architecture)
2. [Deploying to Render (Recommended for Flask)](#2-deploying-to-render)
3. [Deploying to Firebase Hosting](#3-deploying-to-firebase-hosting)
4. [Connecting an External Cloud MySQL Database (Optional)](#4-connecting-an-external-cloud-mysql-database)
5. [Pre-Configured Demo Credentials](#5-pre-configured-demo-credentials)

---

## 1. Dual-Database Architecture

Cloud platforms (such as Render free tier or Cloud Run) do not run a local MySQL server on `127.0.0.1:3306`. To prevent connection crashes while keeping **100% CBSE Class 12 CS (083) curriculum compliance**, the project has an intelligent **Dual-Database Mode (`DB_MODE: auto`)**:

- **Local Machine / School Lab**: If MySQL is running locally (XAMPP / MySQL Server), the app connects to **MySQL 8.0** using `mysql.connector`.
- **Cloud Hosting / Render / Firebase**: If MySQL is offline or not configured, it seamlessly falls back to **SQLite** (`school_lost_found.db`), initializes the tables, and seeds the sample demo records automatically!
- **External Cloud MySQL**: If you set `MYSQL_HOST`, `MYSQL_USER`, and `MYSQL_PASSWORD` environment variables in Render/Firebase, it connects to that cloud MySQL instance.

---

## 2. Deploying to Render

Render is the simplest and most powerful free hosting platform for Python Flask web applications.

### Option A: 1-Click Blueprint Deploy (Using `render.yaml`)

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Add Render & Firebase Hosting configurations"
   git remote add origin https://github.com/YOUR_USERNAME/school-lost-found.git
   git branch -M main
   git push -u origin main
   ```

2. **Deploy on Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com/) and log in (with GitHub).
   - Click **New +** in the top right corner and select **Blueprint**.
   - Connect your GitHub repository `school-lost-found`.
   - Render will detect [`render.yaml`](file:///d:/CS%20holiday%20homework/school-lost-found/render.yaml) automatically.
   - Click **Apply**.
   - Render will build your dependencies, initialize the database, and launch the web service!

---

### Option B: Manual Web Service on Render

If you prefer to configure the service manually in the Render dashboard:

1. Click **New +** → **Web Service**.
2. Select your repository from GitHub.
3. Configure the settings:
   - **Name:** `school-lost-found`
   - **Region:** Any (e.g. `Oregon (US West)` or `Frankfurt (EU Central)`)
   - **Branch:** `main`
   - **Root Directory:** `school-lost-found` (or leave empty if repo root is the project)
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && python init_db.py
     ```
   - **Start Command:**
     ```bash
     gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
     ```
   - **Instance Type:** `Free`
4. In **Advanced** → **Environment Variables**, add:
   - `PYTHON_VERSION`: `3.10.12`
   - `SECRET_KEY`: `your-random-production-secret-key`
   - `DB_MODE`: `auto`
   - `FLASK_DEBUG`: `False`
5. Click **Create Web Service**. Your portal will be live in 2-3 minutes at `https://school-lost-found-xxxx.onrender.com`!

---

## 3. Deploying to Firebase Hosting

Firebase Hosting serves files across Google's worldwide Content Delivery Network (CDN) with free SSL and custom domain support.

Because Flask is a dynamic Python backend, Firebase pairs Firebase Hosting with **Google Cloud Run** using rewrites defined in [`firebase.json`](file:///d:/CS%20holiday%20homework/school-lost-found/firebase.json).

### Prerequisites:
1. Install [Node.js](https://nodejs.org/) (if not already installed).
2. Install the Firebase CLI:
   ```bash
   npm install -g firebase-tools
   ```
3. Install the [Google Cloud SDK (gcloud CLI)](https://cloud.google.com/sdk/docs/install).

---

### Step 1: Log in and Initialize Firebase

Run in your project directory:
```bash
firebase login
```
Select or create your Firebase project in the [Firebase Console](https://console.firebase.google.com/).

Link the project in your local directory:
```bash
firebase use --add
```
(Select your Firebase project ID, e.g., `school-lost-found-portal`)

---

### Step 2: Deploy the Flask Backend to Cloud Run

The included [`Dockerfile`](file:///d:/CS%20holiday%20homework/school-lost-found/Dockerfile) builds the production container with Gunicorn:

```bash
# Build and deploy the container to Google Cloud Run
gcloud run deploy school-lost-found \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars DB_MODE=auto,FLASK_DEBUG=False
```

---

### Step 3: Deploy Firebase Hosting

Once Cloud Run is live, deploy Firebase Hosting:
```bash
firebase deploy --only hosting
```

Firebase Hosting will link your live domain (e.g., `https://school-lost-found-portal.web.app`) to your Cloud Run Flask service, giving you global CDN caching, custom domains, and automatic SSL!

---

### Quick Preview Deploy (Firebase Hosting Static Showcase)

If you only want to deploy the static preview showcase to Firebase Hosting without Cloud Run:
```bash
firebase deploy --only hosting
```
The files in [`public/index.html`](file:///d:/CS%20holiday%20homework/school-lost-found/public/index.html) will be published immediately on your Firebase Hosting URL.

---

## 4. Connecting an External Cloud MySQL Database (Optional)

If you wish to use a cloud-hosted MySQL 8.0 database rather than the automatic SQLite fallback, you can create a free cloud MySQL instance on:
- **Aiven for MySQL** (Free tier available)
- **TiDB Cloud Serverless** (Free tier available)
- **Clever Cloud** (Free 20MB MySQL add-on)

Once you obtain your database connection credentials, add these environment variables in Render (or Cloud Run):

| Environment Variable | Description | Example |
| :--- | :--- | :--- |
| `DB_MODE` | Force MySQL mode | `mysql` |
| `MYSQL_HOST` | Remote MySQL server host | `mysql-3a0b-project.aivencloud.com` |
| `MYSQL_PORT` | Remote MySQL port | `12345` |
| `MYSQL_USER` | MySQL username | `avnadmin` |
| `MYSQL_PASSWORD` | MySQL password | `secret_password` |
| `MYSQL_DB` | Database name | `school_lost_found` |

Run `python init_db.py` once on that remote database, and the portal will use MySQL directly in the cloud.

---

## 5. Pre-Configured Demo Credentials

Both Render and Firebase deployments will come pre-seeded with these demonstration accounts:

| Role | Email | Password |
| :--- | :--- | :--- |
| **Administrator** | `admin@school.local` | `Admin@123` |
| **Student** | `aravind@school.local` | `Student@123` |
| **Student** | `priya@school.local` | `Student@123` |

---

## 6. Verification & Health Check

After deploying to either host:
1. Open the homepage: verify the **"Recent Reports"** and **"Live Campus Statistics"** show up.
2. Click **Login** → Log in as Administrator using `admin@school.local` / `Admin@123`.
3. Check the **Admin Dashboard** to see pending reports, match scores, and claims.
4. Log out and register a new student account to test real-time record insertion.
