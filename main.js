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
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ kelas, tanggal, data })
  })
  .then(res => res.json())
  .then(res => {
    alert("Absensi berhasil disimpan!");
  });
});
