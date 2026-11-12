<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=0,2,2&height=220&section=header&text=M4DI~UciH4%20PROXY%20CHECKER&fontSize=42&fontAlignY=38&desc=Cyber%20Sharingan%20GUI%20Edition%20•%20High-Precision%20Multi-Protocol%20Auditor&descAlignY=62&descSize=16&descAlign=50&stroke=ff2a44&strokeWidth=2" width="100%" />
</p>

<p align="center">
  <a href="https://github.com/RizkyEvory">
    <img src="https://img.shields.io/badge/Author-RizkyEvory%20%7C%20M4DI~UciH4-ff2a44?style=for-the-badge&logo=github&logoColor=white" />
  </a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-00f0ff?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/GUI-Tkinter%20Built--in-00e676?style=for-the-badge&logo=windows&logoColor=white" />
  <img src="https://img.shields.io/badge/Protocols-HTTP%20%7C%20SOCKS4%20%7C%20SOCKS5-ffd166?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Status-Active%20%26%20Bug--Free-ff2a44?style=for-the-badge" />
</p>

---

## ⚡ Sekilas Tentang M4DI~UciH4 Proxy Checker (GUI Edition)

**M4DI~UciH4 Proxy Checker Elite GUI** adalah aplikasi desktop modern berbasis Python dengan antarmuka grafis (**Tkinter Built-in**) bertema *Cyberpunk Dark Mode / Uchiha Sharingan*. Didesain khusus untuk melakukan audit, validasi, dan benchmarking proxy berkecepatan tinggi dengan tingkat akurasi maksimal.

Berbeda dari proxy checker konvensional yang sering menghasilkan *false positive*, tools ini menggunakan **Multi-Stage Verification Engine**: memverifikasi keaslian IP keluar (*Egress IP*), mendeteksi captive portal / blokir ISP, menguji kemampuan SSL/HTTPS Tunneling, hingga mendeteksi tingkat anonimitas secara mendalam (*Elite*, *Anonymous*, atau *Transparent*).

> [!TIP]
> **100% Native GUI**: Menggunakan modul bawaan Python `tkinter` sehingga sangat ringan, tidak membutuhkan instalasi framework GUI berat seperti PyQt/PySide, dan langsung siap dijalankan di Windows dengan sekali klik!

---

## 📸 Tampilan Antarmuka (Cyber Sharingan Dark UI)

```text
+----------------------------------------------------------------------------------------------------+
| ⚡ M4DI~UciH4 PROXY CHECKER ELITE          [HTTP • HTTPS • SOCKS4 • SOCKS5]   [ CODED BY: M4DI~UciH4 ] |
+----------------------------------------------------------------------------------------------------+
| File: [ C:/proxies.txt ] [ Browse ]   Quick IP:Port: [ 198.51.100.25:9050 ] [ Check Single ]       |
| Mode: [ Auto-Detect ▼ ]  Threads: [ 50 ]  Timeout: [ 5s ]  [x] Fast TCP Ping  [▶ START] [⏹ STOP]  |
+----------------------------------------------------------------------------------------------------+
|  [ TOTAL: 150 ]   [ ALIVE: 42 ]   [ DEAD: 108 ]   [ SOCKS5: 28 ]   [ SOCKS4: 5 ]   [ HTTP: 9 ]     |
|  Progress: [████████████████████████████████████████████████░░░░░░░░] 70% (105/150)                |
+----------------------------------------------------------------------------------------------------+
| #  | Proxy Address        | Protocol | Status | Speed   | Anonymity | SSL | Country      | ISP         |
|----+----------------------+----------+--------+---------+-----------+-----+--------------+-------------|
| 1  | 198.51.100.12:1080   | SOCKS5   | ALIVE  | 185ms   | ELITE     | YES | US - United  | CloudHost   |
| 2  | 203.0.113.88:8080    | HTTP     | ALIVE  | 240ms   | ELITE     | YES | SG - Singapo | SingTel     |
| 3  | 192.0.2.45:3128      | SOCKS4   | ALIVE  | 320ms   | ANONYMOUS | NO  | DE - Germany | Hetzner     |
+----------------------------------------------------------------------------------------------------+
| 🔒 Real IP Baseline: xxx.xxx.xxx.xxx [Protected]        💾 Auto-saved to: results.txt              |
+----------------------------------------------------------------------------------------------------+
```

---

## 🌟 Fitur Unggulan

### 1. 🛡️ Multi-Protocol & Smart Auto-Detection
* **HTTP / HTTPS**: Menguji metode `CONNECT` tunneling untuk enkripsi SSL.
* **SOCKS4 & SOCKS4A**: Mendukung proxy TCP standar.
* **SOCKS5 & SOCKS5H**: Mendukung proxy generasi modern dengan *remote DNS resolution* untuk mencegah kebocoran (*DNS Leak*).
* **Smart Auto-Detect**: Cukup masukkan format `IP:PORT` biasa, mesin secara cerdas akan mem-probe dan menentukan protokol yang aktif secara otomatis.

### 2. 🎯 Anti-False-Positive Engine (Akurasi Tinggi)
* **Pre-flight TCP Ping**: Memeriksa konektivitas port awal dalam hitungan milidetik. IP yang mati langsung dibuang tanpa menunggu batas waktu HTTP timeout.
* **Multi-Redundant Judge Verification**: Menguji lalu lintas data langsung ke berbagai endpoint verifikasi independen (`ipify.org`, `ip-api.com`, `httpbin.org`).
* **Content Integrity Check**: Memastikan respon bukan merupakan halaman error 200 OK palsu, captive portal, atau halaman blokir internet positif/ISP.

### 3. 🕵️ Deteksi Tingkat Anonimitas Mendalam
* **ELITE (High Anonymity)**: IP asli Anda tersembunyi 100%, web target tidak menerima header proxy sama sekali.
* **ANONYMOUS**: IP asli tersembunyi, namun web target mendeteksi header perantara (`Via`, `Proxy-Connection`).
* **TRANSPARENT**: Proxy membocorkan IP publik asli Anda ke web target.

### 4. 🌍 GeoIP & Network Intelligence
* Menampilkan informasi geografis secara akurat:
  * **Negara & Kode Negara (ISO)** (Contoh: `US`, `ID`, `SG`, `DE`)
  * **Kota & Wilayah**
  * **Nama ISP / Organisasi Hosting** (Contoh: *DigitalOcean, Biznet, Hetzner*)
  * **Autonomous System Number (ASN)**

### 5. 🚀 Arsitektur Anti-Freeze (Multi-Threaded)
* Proses pengecekan berjalan di background daemon thread terpisah menggunakan sinkronisasi `queue.Queue`.
* Antarmuka GUI tetap responsif, mulus, dan **tidak akan pernah mengalami "Not Responding"** meski memproses ribuan proxy dengan 200 thread.

### 6. 🌐 Built-in Auto-Harvester / Scraper
* Tersedia tombol **`🌐 AUTO-HARVEST`**: sekali klik, aplikasi akan menyedot ribuan proxy publik gratis (SOCKS5, SOCKS4, HTTP) dari sumber-sumber terkurasi ber-uptime tinggi dan langsung memasukkannya ke antrean scan.

### 7. 📋 Manajemen Data Interaktif
* **Klik Kanan (Context Menu)**:
  * *Copy Proxy (IP:Port)*
  * *Copy Full URL (`socks5://ip:port` atau `http://ip:port`)*
  * *Copy Entire Row*
* **Double Click**: Salin instan URL proxy langsung ke clipboard.
* **Checkbox "Show Alive Only"**: Filter instan untuk hanya menampilkan proxy yang hidup.
* **Tombol "Copy All Alive"**: Salin semua proxy yang hidup dalam satu kali klik.

---

## 📝 Format Input yang Didukung

Aplikasi ini mendukung berbagai format input:

```text
# Contoh Format standar IP:Port
198.51.100.10:8080
203.0.113.45:3128
192.0.2.99:1080
198.51.100.77:9050

# Contoh Format dengan protokol
socks5://198.51.100.10:1080
socks4://203.0.113.45:1080
http://192.0.2.99:8080

# Contoh Format dengan autentikasi (Username & Password)
username:password@198.51.100.10:8080
198.51.100.10:8080:username:password
```

---

## 📁 Format Hasil Scan (`results.txt`)

Setiap proxy aktif yang ditemukan otomatis disimpan secara real-time ke file **`results.txt`**:

```text
# =====================================================================
#       ⚡ M4DI~UciH4 PROXY CHECKER ELITE v4.0 - FINAL AUDIT REPORT ⚡
#                      Coded with Pride by: M4DI~UciH4
# =====================================================================
#  Scan Date        : 2026-11-12 20:00:00
#  Total Checked    : 100
#  Alive Proxies    : 42
#  Dead / Timeout   : 58
#  Success Rate     : 42.00%
# =====================================================================

# [ 1. DETAILED PROXY AUDIT LIST ]
# FORMAT: PROTOCOL://IP:PORT | ANONYMITY | SPEED | SSL | COUNTRY | ISP
# ---------------------------------------------------------------------
socks5://198.51.100.12:1080 | ELITE | 185ms | SSL:YES | US (United States) | CloudHost
http://203.0.113.88:8080 | ELITE | 240ms | SSL:YES | SG (Singapore) | SingTel

# [ 2. READY-TO-USE PROXY URLS (FOR SWITCHYOMEGA / CURL / PYTHON) ]
# ---------------------------------------------------------------------
socks5://198.51.100.12:1080
http://203.0.113.88:8080

# [ 3. PURE IP:PORT LIST (STANDARD INPUT FORMAT) ]
# ---------------------------------------------------------------------
198.51.100.12:1080
203.0.113.88:8080
```

---

## 📦 Instalasi & Persiapan

### 1. Clone Repository
```bash
git clone https://github.com/RizkyEvory/M4DI-UciH4-ProxyChecker-GUI.git
cd M4DI-UciH4-ProxyChecker-GUI
```

### 2. Install Dependencies
Pastikan Python 3.10+ sudah terpasang di komputer Anda. Install paket pendukung jaringan:
```bash
pip install -r requirements.txt
```

---

## 🚀 Cara Menjalankan GUI

### Cara 1: Double-Click File Batch (Windows)
Cukup klik ganda file:
```text
run_gui.bat
```

### Cara 2: Melalui Terminal / Command Prompt
```bash
python gui.py
```

---

## 🗂️ Struktur Direktori

```text
M4DI_UciH4_ProxyChecker/
│
├── gui.py              # Script GUI Utama (Tkinter Cyber Dark Theme)
├── checker.py          # Core Engine Pengecekan & Algoritma Audit
├── scraper.py          # Modul Auto-Harvester / Scraper Proxy Publik
├── run_gui.bat         # Launcher Windows 1-Klik untuk GUI
├── run.bat             # Launcher Menu Windows
├── proxies.example.txt # Contoh Template Format Input Proxy
├── requirements.txt    # Daftar Dependensi Python
├── .gitignore          # Menjaga Proxy & Hasil Anda Tidak Ter-upload
└── README.md           # Dokumentasi Resmi Project
```

---

## ⚖️ Lisensi & Etika Penggunaan

Proyek ini dirilis di bawah lisensi **MIT License**.  
Tools ini dibuat untuk tujuan edukasi, pengujian keamanan jaringan, benchmarking infrastruktur, dan administrasi sistem yang sah.

---

<p align="center">
  <b>Developed with ❤️ & ⚡ by <a href="https://github.com/RizkyEvory">M4DI~UciH4 / RizkyEvory</a></b><br>
  <i>"Cyber Sharingan Engine — Precision, Speed, and Stealth."</i>
</p>
