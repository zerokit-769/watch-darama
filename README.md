# 🎬 Drama Watcher Auto Bot

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/GitHub_Actions-2088FF.svg?style=for-the-badge&logo=github-actions&logoColor=white" alt="GitHub Actions" />
  <img src="https://img.shields.io/badge/Telegram-2CA5E0.svg?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram API" />
  <img src="https://img.shields.io/badge/Status-Active-success.svg?style=for-the-badge" alt="Status" />
</div>

<br />

**Drama Watcher Auto Bot** adalah skrip otomatisasi (*crawler/bot*) berbasis Python yang dirancang untuk menonton episode dan mengklaim *reward* (koin/DMC) secara otonom. Dibangun dengan arsitektur **Serverless** menggunakan GitHub Actions dan terintegrasi penuh dengan **Telegram Bot** untuk *monitoring* dan *remote control* secara *real-time*.

> ⚠️ **Disclaimer & Sumber Data:**  
> Seluruh data tontonan, episode, dan autentikasi yang digunakan dalam skrip ini bersumber langsung dari API resmi **[https://drama.center](https://drama.center)**. Skrip ini bertindak sebagai *Auto-Client* untuk mempermudah eksekusi tanpa intervensi manual.

---

## 📑 Daftar Isi
- [Arsitektur Sistem](#-arsitektur-sistem)
- [Fitur Unggulan](#-fitur-unggulan)
- [Persyaratan (Prerequisites)](#-persyaratan-prerequisites)
- [Panduan Setup & Deploy](#-panduan-setup--deploy)
- [Pasca-Deploy (Langkah Selanjutnya)](#-pasca-deploy-langkah-selanjutnya)
- [Daftar Perintah Telegram](#-daftar-perintah-telegram)

---

## 🏗️ Arsitektur Sistem

Proyek ini berjalan tanpa server fisik (*serverless*). Alur kerjanya adalah sebagai berikut:

    [ GitHub Actions ] 🔄 Cron Job (Setiap 4 Jam)
           │
           ├─> Membaca Github Secrets (Token Bot & Chat ID)
           ├─> Menarik pesan dari Telegram (/setcookie)
           ├─> Melakukan HTTP Request ke API drama.center
           ├─> Mengirim Log / Laporan ke [ Telegram App ] 📱
           └─> Commit & Push "selesai.json" kembali ke Repository 💾

---

## ✨ Fitur Unggulan

- ☁️ **Zero-Cost Infrastructure** - Berjalan sepenuhnya di atas infrastruktur GitHub Actions (Gratis 100%).
- 📱 **Real-Time Telemetry** - Notifikasi *Credited* dan *Collected* langsung ke chat Telegram Anda.
- 🍪 **Dynamic Remote Cookie** - Pembaruan sesi (Cookie) via chat Telegram tanpa perlu menyentuh *source code*.
- 💾 **Persistent State** - Riwayat (*progress*) tontonan disimpan dalam `selesai.json` dan di-*commit* secara otomatis oleh bot.
- 🛡️ **Anti-Timeout Shield** - Pembatasan sesi (maks. 180 episode/run) untuk menghindari *banned* dari sistem *timeout* GitHub.

---

## ⚙️ Persyaratan (Prerequisites)

Sebelum memulai *deployment*, siapkan kredensial berikut:
1. **GitHub Account** (Gunakan *Private Repository*).
2. **Telegram Bot Token** (Dapatkan dengan membuat bot di [@BotFather](https://t.me/BotFather)).
3. **Telegram Chat ID** (Dapatkan ID akun Anda di [@userinfobot](https://t.me/userinfobot)).
4. **Active Cookie** dari akun [drama.center](https://drama.center) Anda.

---

## 🚀 Panduan Setup & Deploy

Ikuti langkah-langkah di bawah ini secara berurutan untuk men-deploy bot Anda.

### Langkah 1: Siapkan Repositori & File Base
1. Buat repositori baru di GitHub. **Pastikan di-setting ke "Private"**.
2. Buat file baru bernama `main.py` di direktori utama, lalu *paste* seluruh kode Python ke dalamnya.
3. Buat direktori dan file baru dengan mengetikkan path ini di kolom nama file: `.github/workflows/bot.yml`. *Paste* kode konfigurasi *workflow/actions* ke dalamnya.

*Struktur akhir repositori Anda harus seperti ini:*
    📦 Nama-Repo-Anda
     ┣ 📂 .github
     ┃ ┗ 📂 workflows
     ┃   ┗ 📜 bot.yml
     ┣ 📜 main.py
     ┗ 📜 README.md

### Langkah 2: Konfigurasi Environment Variables (Secrets)
Agar bot dapat mengakses Telegram secara aman tanpa mengekspos token di dalam kode:
1. Masuk ke tab **Settings** di repositori GitHub Anda.
2. Di sidebar kiri, navigasi ke **Secrets and variables** > **Actions**.
3. Klik tombol hijau **New repository secret**.
4. Tambahkan kredensial berikut satu per satu:
   - **Name:** `BOT_TOKEN` | **Secret:** `<Token_Dari_BotFather>`
   - **Name:** `CHAT_ID` | **Secret:** `<Chat_ID_Anda>`

### Langkah 3: Beri Akses Write (Wajib!)
Langkah ini sangat penting agar bot dapat menyimpan progres (file `selesai.json` dan `config.json`) kembali ke repositori:
1. Buka **Settings** > **Actions** > **General**.
2. Scroll ke paling bawah pada bagian **Workflow permissions**.
3. Ubah centang ke **Read and write permissions**.
4. Klik **Save**.

### Langkah 4: Trigger Bot (Deploy Pertama)
Karena menggunakan *Cron Job*, bot berjalan otomatis sesuai jadwal. Untuk memancingnya jalan pertama kali:
1. Buka tab **Actions** di bagian atas repositori Anda.
2. Di menu kiri, klik **Drama Watcher TG Bot**.
3. Klik dropdown **Run workflow** di sebelah kanan.
4. Klik tombol hijau **Run workflow**. 
*(Tunggu sekitar 10-20 detik hingga indikator kuning berputar).*

---

## 🎯 Pasca-Deploy (Langkah Selanjutnya)

Apa yang terjadi setelah Anda mengklik *Run workflow*? 

1. **Cek Log Actions:** Di GitHub, klik proses yang sedang berjalan. Anda akan melihat terminal virtual yang sedang menyiapkan *environment* Python.
2. **Notifikasi Telegram:** Jika pengaturan `BOT_TOKEN` dan `CHAT_ID` benar, Bot Telegram Anda akan langsung mengirimkan pesan peringatan:
   > ⚠️ *Script berjalan tapi Cookie kosong! Silakan kirim: /setcookie isi_cookie_kamu_disini*
3. **Kirim Cookie:** Buka Telegram, tempelkan *cookie* Anda dari drama.center, lalu kirim ke bot dengan format:
   `/setcookie _ga=GA1.2...; session_id=12345...`
4. **Duduk & Bersantai:** Bot akan menyimpan *cookie* tersebut. Pada jadwal *run* berikutnya, bot akan otomatis mulai menonton, mendulang *reward*, dan mengirimkan laporan (*Credited & Collected*) langsung ke HP Anda!

---

## 📟 Daftar Perintah Telegram

Kirimkan perintah ini di obrolan Bot Telegram Anda untuk mengontrol bot dari jarak jauh:

| Perintah | Deskripsi |
| :--- | :--- |
| `/setcookie [cookie]` | Memperbarui atau memasukkan Cookie sesi yang baru. |
| *(Otomatis)* | Bot otomatis mengecek *updates* setiap dijalankan oleh GitHub. |

---

<div align="center">
  <i>Dibuat untuk otomatisasi dan efisiensi. Gunakan dengan bijak.</i><br>
  &copy; ZenithHub Project - Open Source Initiative
</div>
