
const kelasSelect = document.getElementById("kelas");
const cboNama = document.getElementById("nama");
// Saat kelas dipilih, tampilkan daftar siswa
kelasSelect.addEventListener("change", () => {
  const kelas = kelasSelect.value;
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
    cboNama.innerHTML = '<option value="">Pilih Nama</option>';

    // Tambahkan nama-nama dari response
    data.forEach(siswa => {
      const option = document.createElement("option");
      option.value = siswa.nama;
      option.textContent = siswa.nama;
      cboNama.appendChild(option);
    });
  })
  .catch(error => {
    console.error("Gagal memuat data siswa:", error);
  });
});


// Simpan ke backend Flask
document.querySelector("button.bg-blue-600").addEventListener("click", () => {
  const kelas = kelasSelect.value;
  const tanggal = tanggalInput.value;

  const data = [];
  document.querySelectorAll(".status-select").forEach(select => {
    data.push({
      nama: select.dataset.nama,
      status: select.value
    });
  });

  fetch("/absensi", {
    method: "GET",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ kelas, tanggal, data })
  })
  .then(res => res.json())
  .then(res => {
    alert("Absensi berhasil disimpan!");
  });
});
