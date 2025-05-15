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
# siswa_to_nomor = {
#     "Ahmad": "6281234567890",
#     "Budi": "6289876543210",
#     "Citra": "6281122334455",
#     "Dina": "6289988776655",
#     # Tambahkan siswa lainnya di sini
# }

def baca_data_siswa(kelas=None):
    siswa_list = []
    if not os.path.exists('data_siswa.csv'):
        # buat file kosong dengan header jika belum ada
        with open('data_siswa.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['nis', 'nama', 'kelas', 'nomor'])
        return siswa_list

    with open('data_siswa.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Jika ada filter kelas, filter di sini
            if kelas is None or row['kelas'] == kelas:
                siswa_list.append({
                    'nis': row['nis'],
                    'nama': row['nama'],
                    'kelas': row['kelas'],
                    'nomor': row['nomor']
                })
    return siswa_list

def get_siswa_by_nis(nis):
    if not os.path.exists('data_siswa.csv'):
        return None

    with open('data_siswa.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['nis'] == nis:
                return {
                    'nis': row['nis'],
                    'nama': row['nama'],
                    'kelas': row['kelas'],
                    'nomor': row['nomor']
                }
    return None

def baca_semua_absensi():
    hasil = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                if len(row) >= 5:
                    hasil.append({
                        "kelas": row[0],
                        "nis": row[1],
                        "nama": row[2],
                        "tanggal": row[3],
                        "status": row[4]
                    })
    return hasil

def cek_absensi_tercatat(nis, tanggal):
    absensi_list = baca_semua_absensi()
    for entry in absensi_list:
        if entry["nis"] == nis and entry["tanggal"] == tanggal:
            return True, entry
    return False, None


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
    data_absensi = baca_semua_absensi()
    return render_template('laporan.html', data_absensi=data_absensi)


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
    nis = data.get('nis')
    tanggal = data.get('tanggal')
    status = data.get('status')

    # Validasi NIS kosong
    if not nis or nis.strip() == "":
        return jsonify({"message": "NIS tidak ditemukan."}), 200

    # Ambil data siswa berdasarkan NIS
    dSiswa = get_siswa_by_nis(nis)
    if not dSiswa:
        return jsonify({"message": f"Siswa dengan NIS {nis} tidak ditemukan."}), 200

    nama = dSiswa['nama']
    kelas = dSiswa['kelas']
    nomor = dSiswa.get('nomor')

    #  Cek apakah absensi sudah tercatat
    if cek_absensi_tercatat(nis, tanggal)[0]:
        return jsonify({"message": f"Absensi untuk {nama} pada {tanggal} sudah tercatat."}), 200

    file_exists = os.path.exists(CSV_FILE)

    try:
        # Simpan ke CSV
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Tulis header jika file baru
            if not file_exists:
                writer.writerow(['kelas', 'nis', 'nama', 'tanggal', 'status'])

            writer.writerow([kelas, nis, nama, tanggal, status])
    except Exception as e:
        return jsonify({"message": f"Gagal menyimpan absensi: {str(e)}"}), 500

    #  Kirim WA jika nomor tersedia
    if nomor and nomor.strip() != "":
        pesan = f"Hai {nama}, Anda tercatat *{status}* pada {tanggal} di kelas {kelas}."
        wa_response = kirim_whatsapp(nomor, pesan)

        if wa_response.get('sent') or wa_response.get('status') == 'success':
            return jsonify({"message": f"Absensi {nama} berhasil disimpan dan WhatsApp dikirim."}), 200
        else:
            return jsonify({"message": f"Absensi {nama} berhasil disimpan, tapi WhatsApp gagal dikirim."}), 200

    return jsonify({"message": f"Absensi {nama} berhasil disimpan. Nomor WhatsApp tidak tersedia."}), 200



# ➤ API AMBIL DATA ABSENSI
@app.route('/absensi', methods=['GET'])
def ambil_absensi():
    nis = request.args.get("nis")
    tanggal = request.args.get("tanggal")

    if nis and tanggal:
        found, data = cek_absensi_tercatat(nis, tanggal)
        if found:
            return jsonify({"exists": True, "data": data}), 200
        else:
            return jsonify({"exists": False, "message": "Absensi tidak ditemukan"}), 200
    else:
        return jsonify(baca_semua_absensi()), 200

    
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


@app.route('/siswa', methods=["POST"])
def get_siswa():
    data = request.get_json()
    kelas = data.get("kelas") if data else None

    siswa_list = baca_data_siswa(kelas)
    return jsonify(siswa_list)

if __name__ == '__main__':
    app.run(debug=True)
