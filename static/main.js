
const kelasSelect = document.getElementById("kelas");
const cboSiswa = document.getElementById("siswa");
const dtAbsensi = document.getElementById("dt_absensi");
const cboStatus = document.getElementById("cbo_status");

// Saat kelas dipilih, tampilkan daftar siswa
kelasSelect.addEventListener("change", () => {
  let kelas = kelasSelect.value;
  fetch("/siswa", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ kelas: kelas })
  })
  .then(response => response.json())
  .then(data => {
    // Kosongkan dulu opsi nama
    cboSiswa.innerHTML = '<option value="">Pilih Nama</option>';

    // Tambahkan nama-nama dari response
    data.forEach(siswa => {
      const option = document.createElement("option");
      option.value = siswa.nis;
      option.textContent = "[ " + siswa.nis + " ] " + siswa.kelas + " : " + siswa.nama + " - " + siswa .nomor ;
      cboSiswa.appendChild(option);
    });
  })
  .catch(error => {
    console.error("Gagal memuat data siswa:", error);
  });
});


// Simpan ke backend Flask
document.getElementById("form_input_absensi").addEventListener("submit", function (event) {
  event.preventDefault(); 

  // let kelas = kelasSelect.value;
  let tanggal = dtAbsensi.value;
  let nis = cboSiswa.value;
  let status = cboStatus.value;

  fetch("/simpan_absensi", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({nis, tanggal, status })
  })
  .then(res => res.json())
  .then(res => {
    alert(res.message || "Absensi berhasil disimpan!");
    // window.location.href = "/input"; // Redirect jika berhasil
  })
  .catch(err => {
    console.error("Gagal simpan:", err);
    alert("Terjadi kesalahan saat menyimpan absensi.");
  });
});

