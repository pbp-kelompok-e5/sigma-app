# Panduan Git Workflow - Sigma App

> [!IMPORTANT]
> **Setiap anggota tim mengerjakan fitur di branch masing-masing!**

---

## 📥 Clone Repository

1. **Buat direktori lokal** dengan nama `sigma-app`

2. **Buka folder** di VSCode

3. **Clone repository:**
   ```bash
   git clone https://github.com/pbp-kelompok-e5/sigma-app.git
   ```

---

## 🔄 Update ke Versi Main Terbaru

Sebelum membuat branch baru, pastikan Anda memiliki versi terbaru dari `main`:

1. **Pindah ke branch main:**
   ```bash
   git checkout main
   ```

2. **Update dari remote:**
   ```bash
   git pull origin main
   ```

---

## 🌿 Membuat Branch Personal

1. **Buat branch baru** dengan nama Anda:
   ```bash
   git checkout -b nama-kalian
   ```

2. **Cek branch aktif** (pastikan berada di branch Anda):
   ```bash
   git branch
   ```
   
   > [!TIP]
   > Branch yang aktif akan ditandai dengan tanda `*`

---

## 💻 Workflow Development

> [!WARNING]
> - **JANGAN commit langsung ke `main`**
> - **SELALU cek branch sebelum commit** menggunakan `git branch`

> [!NOTE]
> Kerjakan semua fitur di branch masing-masing untuk menghindari konflik

---

## 📚 Referensi

Untuk informasi lebih lengkap, rujuk ke:  
[PBP Fasilkom UI - Development di Feature Branch](https://pbp-fasilkom-ui.github.io/ganjil-2026/assignments/group/midterm-guide#development-di-feature-branch)

---

## 📝 Tips Tambahan

> [!TIP]
> **Best Practices:**
> - Commit secara berkala dengan pesan yang jelas dan deskriptif
> - Pull dari `main` secara rutin untuk menghindari konflik besar
> - Komunikasikan dengan tim sebelum merge ke `main`
> - Test fitur Anda sebelum push ke remote