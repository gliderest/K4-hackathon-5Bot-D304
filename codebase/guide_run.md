# Guide Run

## 1. Vị trí dự án

Lam viec trong thu muc:

```powershell
cd /Users/thangnguyenvan/K4-hackathon-5Bot-D304/codebase
```

## 2. Chay backend FastAPI

### Bước 1: Tạo virtual environment

```powershell
python -m venv .venv
```

### Bước 2: Kích hoạt môi trường

```powershell
source .venv/bin/activate
```

Neu PowerShell chan script, chay tam:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

roi kich hoat lai:

```powershell
.venv\Scripts\Activate.ps1
```

### Bước 3: Cài thư viện

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Bước 4: Tạo file `.env`

Copy tu file mau:

```powershell
cp .env.example .env
```

Mac dinh hien tai app chay o che do `local`, khong bat buoc co API key.

### Bước 5: Chạy backend

```powershell
PYTHONPATH=. uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

### Bước 6: Kiểm tra backend

Mo trinh duyet:

```text
http://127.0.0.1:8000/api/health
```

Neu dung, ban se thay:

```json
{"status":"ok"}
```

## 3. Chạy frontend React

Mo terminal moi, van o thu muc:

```powershell
cd D:\AITHUCCHIEN\HACKATHON\K4-hackathon-5Bot-D304\codebase\frontend
```

### Buoc 1: Cai dependencies

```powershell
npm install
```

### Buoc 2: Chay frontend

```powershell
npm run dev
```

Frontend mac dinh chay tai:

```text
http://localhost:5173
```

## 4. Thử nghiệm demo

Sau khi backend va frontend cung dang chay:

1. Mo `http://localhost:5173`
2. Chon lesson ben trai
3. Xem slide/transcript o giua
4. Dat cau hoi trong khung chat ben phai
5. Thu upload them file `.pdf`, `.docx`, `.txt`, hoac `.md`
6. Bam vao citation de mo dung nguon slide hoac transcript

## 5. Luu y du lieu

- Hoc lieu khoa hoc dang doc tu `data\vlearn-pack`
- File upload cua nguoi hoc se vao `data\user_uploads`
- Memory tien do hoc tap luu o `storage\vlearn.db`
- Metadata catalog/chunks phat sinh se vao `data\processed\chunks`

## 6. Neu gap loi

### Backend khong len

Kiem tra:

```powershell
python --version
pip --version
```

va dam bao dang o dung thu muc `codebase`.

### Frontend khong goi duoc API

Kiem tra backend co dang chay o `127.0.0.1:8000` khong.

### Loi import Python

Chay lai backend bang:

```powershell
$env:PYTHONPATH = (Get-Location).Path
uvicorn backend.app.main:app --reload
```

### Loi upload file

Chi ho tro:

- `.pdf`
- `.docx`
- `.txt`
- `.md`

## 7. Lệnh tắt nhanh

Backend:

```powershell
cd /Users/thangnguyenvan/K4-hackathon-5Bot-D304/codebase
source .venv/bin/activate
PYTHONPATH=. uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd D:\AITHUCCHIEN\HACKATHON\K4-hackathon-5Bot-D304\codebase\frontend
npm install
npm run dev
```
