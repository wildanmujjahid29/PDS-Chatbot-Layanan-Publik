# Chatbot RAG Sewakadharma

Proyek Chatbot berbasis Retrieval-Augmented Generation (RAG) untuk layanan informasi Sewakadharma MPP Denpasar.

## 📋 Deskripsi Proyek

Aplikasi chatbot yang menggunakan teknologi RAG (Retrieval-Augmented Generation) untuk memberikan informasi akurat tentang layanan-layanan yang tersedia di Mall Pelayanan Publik (MPP) Denpasar. Sistem ini menggabungkan pencarian informasi dari database dengan kemampuan generasi respons yang natural dan informatif.

## 🗂️ Struktur Folder

```
chatbot-rag-sewakadharma/
│
├── app/                          # Direktori utama aplikasi
│   ├── api/                      # Endpoint API dan route handlers
│   ├── core/                     # Konfigurasi inti aplikasi
│   ├── database/                 # Koneksi dan operasi database
│   │   └── client.py            # Client Supabase untuk koneksi database
│   ├── schemas/                  # Pydantic models untuk validasi data
│   ├── services/                 # Business logic dan layanan aplikasi
│   └── utils/                    # Fungsi utility dan helper functions
│
├── scripts/                      # Script untuk automation dan maintenance
├── tests/                        # Unit tests dan integration tests
├── venv/                         # Virtual environment Python (tidak di-commit)
│
├── .env                          # Environment variables (tidak di-commit)
├── .gitignore                    # File yang diabaikan oleh Git
├── main.py                       # Entry point aplikasi
├── requirements.txt              # Dependencies Python
├── mpp_denpasar_services_cleaned (1).csv  # Dataset layanan MPP
└── README.md                     # Dokumentasi proyek (file ini)
```

## 📁 Penjelasan Direktori

### `/app`

Direktori utama yang berisi seluruh kode aplikasi dengan arsitektur modular.

#### `/app/api`

Berisi endpoint-endpoint API REST untuk komunikasi dengan frontend atau client lain. Menggunakan FastAPI untuk routing dan handling HTTP requests.

#### `/app/core`

Menyimpan konfigurasi inti aplikasi seperti:

- Settings dan environment configuration
- Konstanta aplikasi
- Security dan authentication setup

#### `/app/database`

Mengelola koneksi dan operasi database:

- **`client.py`**: Inisialisasi koneksi ke Supabase database menggunakan environment variables

#### `/app/schemas`

Pydantic schemas untuk:

- Request/response models
- Validasi data input/output
- Type hints dan dokumentasi otomatis API

#### `/app/services`

Business logic dan layanan utama aplikasi:

- RAG processing
- Vector search
- Chatbot logic
- Data processing services

#### `/app/utils`

Fungsi-fungsi utility dan helper:

- Text processing
- Data transformation
- Logging helpers
- Common utilities

### `/scripts`

Script-script untuk keperluan development, deployment, atau maintenance:

- Data ingestion
- Database migration
- Testing automation

### `/tests`

Test suite untuk quality assurance:

- Unit tests
- Integration tests
- API endpoint tests

## 🔧 Teknologi yang Digunakan

### Backend Framework

- **FastAPI**: Modern web framework untuk API development
- **Uvicorn**: ASGI server untuk menjalankan aplikasi

### Database & Storage

- **Supabase**: Backend-as-a-Service untuk database PostgreSQL dan storage
- **FAISS**: Library untuk efficient similarity search dan vector indexing

### AI/ML Components

- **Chonkie**: Text chunking dan processing
- **RAG**: Retrieval-Augmented Generation untuk chatbot

### Data Processing

- **Pandas**: Data manipulation dan analysis
- **NumPy**: Numerical computing

### Utilities

- **Python-dotenv**: Environment variable management
- **Loguru**: Advanced logging
- **Pydantic**: Data validation menggunakan Python type hints

## 🚀 Cara Menjalankan Aplikasi

### Prasyarat

- Python 3.8+
- Virtual environment (recommended)
- Akun Supabase

### Instalasi

1. **Clone repository**

   ```bash
   git clone <repository-url>
   cd chatbot-rag-sewakadharma
   ```

2. **Buat virtual environment**

   ```bash
   python -m venv venv
   ```

3. **Aktifkan virtual environment**

   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Setup environment variables**

   Buat file `.env` di root directory dengan konfigurasi berikut:

   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

6. **Jalankan aplikasi**
   ```bash
   python main.py
   ```
   atau dengan uvicorn:
   ```bash
   uvicorn main:app --reload
   ```

## 📊 Dataset

File `mpp_denpasar_services_cleaned (1).csv` berisi data layanan-layanan yang tersedia di MPP Denpasar, yang digunakan sebagai knowledge base untuk chatbot.

## 🔐 Environment Variables

Variabel yang diperlukan dalam file `.env`:

| Variable            | Deskripsi                              |
| ------------------- | -------------------------------------- |
| `SUPABASE_URL`      | URL endpoint Supabase project          |
| `SUPABASE_ANON_KEY` | Anonymous/public API key dari Supabase |

## 📝 Development Guidelines

1. **Code Style**: Ikuti PEP 8 Python style guide
2. **Type Hints**: Gunakan type hints untuk semua function parameters dan return values
3. **Documentation**: Tambahkan docstrings untuk setiap function dan class
4. **Testing**: Tulis tests untuk setiap fitur baru di folder `/tests`
5. **Git Workflow**:
   - Buat branch untuk setiap feature
   - Commit dengan pesan yang jelas dan deskriptif
   - Pull request untuk merge ke main branch

## 🤝 Kontribusi

Untuk berkontribusi pada proyek ini:

1. Fork repository
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📄 Lisensi

[Tentukan lisensi proyek Anda di sini]

## 👥 Tim Pengembang

[Tambahkan informasi tim pengembang di sini]

## 📞 Kontak

Untuk pertanyaan atau diskusi lebih lanjut, silakan hubungi:

- Email: [email-anda@example.com]
- Project Link: [link-repository]

---

**Note**: Pastikan untuk tidak meng-commit file `.env` atau folder `venv/` ke repository. File-file ini sudah ditambahkan ke `.gitignore`.
