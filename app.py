from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import csv, os, requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN")
ULTRAMSG_INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID")

app = Flask(__name__)
CORS(app)

CSV_FILE = 'absensi.csv'

# ➤ NOMOR HP SETIAP SISWA (WAJIB format internasional: 628xxxx)
siswa_to_nomor = {
    "Ahmad": "6281234567890",
    "Budi": "6289876543210",
    "Citra": "6281122334455",
    "Dina": "6289988776655",
    # Tambahkan siswa lainnya di sini
}

def baca_data_siswa():
    siswa = {}
    if os.path.exists('data_siswa.csv'):
        with open('data_siswa.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                siswa[row['Nama']] = row['Nomor']
    return siswa

# ➤ KIRIM PESAN WHATSAPP
def kirim_whatsapp(nomor, pesan):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
    headers = {"Content-Type": "application/json"}
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": nomor,
        "body": pesan
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# ➤ ROUTING HALAMAN
@app.route('/')
def login():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/input')
def input_absensi():
    return render_template('input.html')

@app.route('/laporan')
def laporan():
    return render_template('laporan.html')

# @app.route('/pengaturan')
# def pengaturan():
#     return render_template('pengaturan.html')

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

# ➤ SIMPAN ABSENSI + KIRIM PESAN WA PER SISWA
@app.route('/simpan_absensi', methods=['POST'])
def simpan_absensi():
    data = request.get_json()
    kelas = data.get('kelas')
    tanggal = data.get('tanggal')
    daftar_siswa = data.get('data')

    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for siswa in daftar_siswa:
            nama = siswa.get('nama')
            status = siswa.get('status')

            writer.writerow([kelas, nama, tanggal, status])

            # Kirim WhatsApp jika nomor tersedia
            nomor = siswa_to_nomor.get(nama)
            if nomor:
                pesan = f"Hai {nama}, Anda tercatat *{status}* pada {tanggal} di kelas {kelas}."
                kirim_whatsapp(nomor, pesan)

    return jsonify({"message": "Absensi dan notifikasi berhasil dikirim"}), 200

# ➤ API AMBIL DATA ABSENSI
@app.route('/absensi', methods=['GET'])
def ambil_absensi():
    hasil = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                hasil.append({
                    "nama": row[1],
                    "kelas": row[0],
                    "tanggal": row[2],
                    "status": row[3]
                })
    return jsonify(hasil)
    
@app.route('/pengaturan', methods=['GET', 'POST'])
def pengaturan():
    pesan = ""
    if request.method == 'POST':
        nama = request.form['nama']
        kelas = request.form['kelas']
        nomor = request.form['nomor']

        # Cek jika sudah ada
        exists = False
        rows = []
        if os.path.exists('data_siswa.csv'):
            with open('data_siswa.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                for row in rows:
                    if row['Nama'] == nama:
                        exists = True
                        row['Nomor'] = nomor
                        row['Kelas'] = kelas

        if not exists:
            rows.append({'Nama': nama, 'Kelas': kelas, 'Nomor': nomor})

        # Simpan kembali
        with open('data_siswa.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Nama', 'Kelas', 'Nomor'])
            writer.writeheader()
            writer.writerows(rows)
        
        pesan = "Data berhasil disimpan."

    # Tampilkan data siswa
    siswa = []
    if os.path.exists('data_siswa.csv'):
        with open('data_siswa.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            siswa = list(reader)

    return render_template('pengaturan.html', siswa=siswa, pesan=pesan)


if __name__ == '__main__':
    app.run(debug=True)
