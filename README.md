Nama : Rayna Kayla Rayvanka 
NPM : 2506657283
Kelas : PBP F


## Refleksi Tugas 1

### 1. Penggunaan elemen semantik HTML5

Pada Tugas 1 ini, saya menggunakan beberapa elemen semantik HTML5 seperti `<section>`, `<article>`, dan `<header>` untuk menyusun konten pada halaman portofolio. Saya menggunakan `<section>` untuk memisahkan bagian besar seperti profile dan experience, sedangkan `<article>` digunakan untuk setiap card kategori pengalaman karena masing-masing card memiliki isi yang berdiri sendiri.

Menurut saya, penggunaan elemen semantik membuat struktur HTML menjadi lebih mudah dibaca dan dipahami dibandingkan jika seluruh bagian hanya menggunakan `<div>`. Selain itu, saya juga menjadi lebih mudah memahami hubungan antarbagian saat melakukan styling karena struktur halaman sudah terbagi berdasarkan fungsi kontennya.

Untuk static web, elemen semantik tidak secara langsung menambahkan fungsi baru, tetapi membantu menjaga struktur kode agar lebih rapi, terorganisir, dan lebih mudah dikembangkan pada tahap berikutnya.

### 2. Tantangan dalam membuat CSS responsive

Tantangan utama yang saya temui adalah menjaga tampilan tetap proporsional ketika berpindah dari desktop ke mobile. Pada desktop, beberapa elemen seperti card pengalaman dapat ditampilkan dalam beberapa kolom, tetapi ketika ukuran layar semakin kecil, layout tersebut menjadi terlalu sempit jika tetap dipertahankan.

Saya mengatasinya dengan menggunakan media query dan menyesuaikan jumlah kolom pada layout. Pada desktop, card dapat ditampilkan dalam beberapa kolom, sedangkan pada mobile card disusun menjadi satu kolom agar isi tetap mudah dibaca.

Selain itu, saya juga perlu mempertimbangkan ukuran font, jarak antar elemen, ukuran gambar, dan padding pada card. Saya mencoba memprioritaskan keterbacaan dan isi utama terlebih dahulu. Elemen dekoratif seperti background effect dibuat lebih fleksibel agar tidak mengganggu konten pada layar kecil.

Saya juga menemukan bahwa fitur hover tidak dapat menjadi interaksi utama pada mobile karena perangkat mobile tidak menggunakan cursor. Oleh karena itu, detail pengalaman yang pada desktop dapat muncul saat hover tetap dibuat dapat terlihat pada tampilan mobile.

### 3. Batasan static web dan rencana pengembangan berikutnya

Batasan yang paling terasa dari static web adalah seluruh informasi harus ditulis langsung di dalam file HTML. Jika saya ingin menambahkan pengalaman, project, atau sertifikasi baru, saya harus mengubah kode secara manual.

Selain itu, halaman belum dapat menyimpan atau mengambil data secara dinamis. Konten yang ditampilkan juga sama untuk setiap pengguna karena belum ada database maupun interaksi dari pengguna.

Pada iterasi berikutnya, saya ingin membuat data portofolio seperti pengalaman, project, kompetisi, dan sertifikasi dapat dikelola secara dinamis. Saya ingin konten tersebut nantinya tersimpan dalam database sehingga dapat ditambahkan, diubah, atau dihapus tanpa harus mengubah struktur HTML secara langsung.

Saya juga tertarik untuk menambahkan fitur seperti halaman detail project, filter berdasarkan kategori, dan form kontak agar website tidak hanya berfungsi sebagai halaman informasi, tetapi juga menjadi portofolio yang lebih interaktif.

## Penggunaan AI

Dalam pengerjaan Tugas 1, saya menggunakan AI sebagai alat bantu untuk brainstorming, mengevaluasi ide desain, dan membantu memahami beberapa bagian implementasi HTML dan CSS.

Saya tidak langsung menggunakan seluruh hasil yang diberikan AI. Saya tetap menyesuaikan kembali struktur HTML, isi portofolio, styling, serta detail implementasi berdasarkan kebutuhan tugas dan desain yang saya inginkan.

AI juga saya gunakan untuk membantu menjelaskan beberapa konsep seperti semantic HTML, responsive design, CSS Grid, hover interaction, serta workflow Git. Hal ini membantu saya memahami alasan di balik implementasi yang digunakan, bukan hanya menyalin kode.

Beberapa saran dari AI juga perlu saya revisi karena terkadang terlalu kompleks atau tidak sesuai dengan struktur project yang sudah saya miliki. Oleh karena itu, saya menggunakan AI sebagai alat bantu untuk mempercepat proses belajar dan eksplorasi, sementara keputusan akhir, isi data, dan penyesuaian kode tetap saya lakukan sendiri.


## Refleksi Tugas 2

### 1. Jelaskan alur yang terjadi ketika pengguna membuka halaman portofolio baru

Jadi pas user buka `/projects/`, request-nya pertama masuk dulu ke `portofolio/urls.py`. Terus dari situ karena pakai `include()`, URL-nya diterusin ke `main/urls.py`. Nah di sana ada path `projects/` yang nanti nyambung ke view `show_projects`.

Di `show_projects`, data Project diambil semua pakai `Project.objects.all()`. Habis itu datanya dimasukin ke context, namanya `project_list`, terus dikirim ke `projects.html`.

Di HTML-nya nanti ada perulangan buat nampilin semua project. Jadi setiap project dibuat card. Kalau ternyata project-nya belum ada, bagian `{% empty %}` yang jalan dan nampilin pesan kalau belum ada project.

Kurang lebih alurnya browser → urls utama → urls main → view → ambil model/database → masuk context → template → HTML balik ke browser.

### 2. Mengapa data Project sebaiknya disimpan pada model dan tidak ditulis langsung di template?

Menurut saya lebih enak disimpan di model karena data sama tampilannya jadi dipisah. Kalau semua data project ditulis langsung di HTML, nanti setiap mau nambah project harus edit HTML lagi dan mungkin copy card yang sama terus.

Kalau pakai model tinggal tambah data aja ke database. Template-nya bisa tetap sama karena tinggal melakukan perulangan buat nampilin semua data.

Terus menurut saya juga lebih gampang kalau nanti mau nambah fitur. Misalnya mau bikin form buat nambah project, filter kategori, atau halaman detail. Jadi lebih rapi dibanding semua data langsung ditulis di template.

### 3. Apa perbedaan `makemigrations` dan `migrate` pada Django?

`makemigrations` itu buat bikin file migration berdasarkan perubahan yang kita lakukan di model. Jadi misalnya kita bikin model `Project`, Django bakal tahu ada perubahan dan bikin semacam file yang isinya perubahan database yang perlu dilakukan.

Tapi `makemigrations` belum langsung mengubah database.

Nah kalau `migrate`, itu baru menjalankan migration tadi supaya perubahan modelnya benar-benar diterapkan ke database.

Di tugas ini setelah bikin model `Project`, saya menjalankan `python manage.py makemigrations`. Setelah itu dibuat migration `0002_project.py`. Terus saya menjalankan `python manage.py migrate` supaya tabel Project benar-benar dibuat di database.

Kalau cuma nambah data project lewat Django shell, tidak perlu migration lagi karena struktur tabelnya sebenarnya tidak berubah. Migration diperlukan kalau model atau struktur databasenya berubah, misalnya nambah field.

#### Penggunaan AI pada Tugas 2

Pada Tugas 2, saya menggunakan ChatGPT dan Codex sebagai alat bantu dalam proses brainstorming, implementasi, dan review. ChatGPT membantu saya menguraikan requirement tugas, menentukan struktur halaman Projects, dan memahami kembali alur MVT. Codex digunakan untuk membantu mencari error pada view, routing, template, styling, migration, dan unit test berdasarkan struktur repository yang sudah ada.

Saya tetap menentukan konsep halaman, isi project, dan tema glassmorphism yang digunakan. Setelah implementasi, saya memasukkan data melalui Django shell, memeriksa tampilan setiap halaman, serta menjalankan migration check, system check, dan seluruh unit test secara mandiri. Hasil akhir menunjukkan bahwa migration telah diterapkan dan seluruh 13 test berhasil dijalankan.

Log percakapan:

- https://chatgpt.com/c/6aa819fb-49e0-83ec-9520-f4592e92385f

## Menjalankan Proyek Secara Lokal

Proyek ini menggunakan Django dan dikembangkan dengan virtual environment
`env` pada Windows. Langkah setup dari PowerShell:

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PRODUCTION = 'False'  # gunakan SQLite development lokal
python manage.py migrate
python manage.py test
python manage.py runserver
```

Setelah server berjalan, buka `http://127.0.0.1:8000/`. File `.env`, database
`db.sqlite3`, folder `env`, dan kredensial tidak boleh dimasukkan ke Git.
Migration `0003_align_experience_categories` mempertahankan record Experience lama
sambil memetakan kategori teknis lama ke enam kategori portofolio yang dipakai
oleh desain saat ini.

Migration `0004_experience_optional_start_date` membuat `started_at` opsional
dan dapat diisi di form. Sebelumnya `auto_now_add` mencatat waktu penambahan
record, sehingga pengalaman yang selesai sebelum dicatat dapat memiliki urutan
tanggal yang salah. Semua nilai tanggal lama tetap disimpan persis seperti
sebelumnya; tanggal sebenarnya tidak ditebak atau diisi ulang. Pemilik data dapat
mengoreksi tanggal lama lewat Edit jika diperlukan. Tanggal kosong berarti belum
diketahui; waktu pada form mengikuti konfigurasi proyek, yaitu UTC. Jika kedua
tanggal diisi, tanggal selesai harus sama atau setelah tanggal mulai.

Pemetaan kategori pada migration `0003` menggabungkan beberapa kategori lama.
Rollback migration itu tidak mengembalikan subkategori awal secara persis
(misalnya internship dan freelance sama-sama menjadi career); simpan backup
database sebelum melakukan rollback. Migration yang sudah diterapkan tidak
ditulis ulang dalam audit lanjutan.

## Fitur Experience Management

Halaman Experience mempertahankan enam kelompok desain: Career,
Organizations, Community, Competition, Personal Project, dan Certification.
Data di halaman tersebut berasal dari endpoint JSON, dideserialisasi kembali
menjadi objek Django, lalu dikelompokkan untuk ditampilkan pada card yang
sesuai. Fitur yang tersedia meliputi:

- melihat daftar dan empty state di `/experience/`;
- menambah pengalaman di `/experience/add/`;
- mengubah pengalaman di `/experience/<uuid>/edit/`;
- menghapus pengalaman melalui form POST di `/experience/<uuid>/delete/`;
- mengambil data JSON di `/api/experiences/`.

Untuk memeriksa perubahan sebelum menjalankan server:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

### Tugas 3

1. **Penggunaan Django ModelForm dan CSRF**

   Django `ModelForm` digunakan untuk membantu membuat form berdasarkan model yang sudah ada. Jadi, aturan seperti field wajib atau opsional, pilihan kategori, tipe data, dan validasi bisa mengikuti aturan yang ada di model. Dengan cara ini, kita tidak perlu menulis semua aturan secara manual di HTML, sehingga kode lebih rapi dan mengurangi kemungkinan adanya perbedaan antara form dan database.

   Pada form yang menggunakan metode POST, `{% csrf_token %}` wajib ditambahkan untuk membantu melindungi aplikasi dari serangan Cross-Site Request Forgery (CSRF). Serangan ini terjadi ketika website lain mencoba mengirimkan request yang mengubah data menggunakan sesi pengguna tanpa sepengetahuan pengguna tersebut.

   Django juga melakukan pemeriksaan keamanan tambahan melalui middleware, termasuk pemeriksaan Origin atau Referer dalam kondisi tertentu.

2. **Perbandingan JSON dan XML**

   JSON lebih sering digunakan dalam aplikasi web modern karena sintaksnya sederhana, mudah dibaca, dan biasanya memiliki ukuran data yang lebih ringkas. JSON juga mudah digunakan dalam JavaScript karena mendukung struktur object dan array.

   Sementara itu, XML masih digunakan pada sistem tertentu yang membutuhkan namespace, schema, atau struktur dokumen yang lebih ketat. Namun, XML biasanya membutuhkan tag pembuka dan penutup, sehingga penulisannya bisa lebih panjang dibandingkan JSON.

3. **Proses Serialization dan Deserialization**

   Ketika URL `/api/experiences/` dipanggil, view mengambil data Experience dari database menggunakan queryset. Kemudian, `serializers.serialize("json", queryset)` digunakan untuk mengubah data tersebut menjadi format JSON yang bisa dikirim melalui HTTP response.

   Serialization diperlukan karena object Django dan queryset Python tidak bisa langsung dikirim sebagai data HTTP dalam bentuk aslinya. Data tersebut perlu diubah terlebih dahulu ke format yang dapat dipertukarkan.

   Pada halaman `/experience/`, data JSON dibaca dan diproses menggunakan `serializers.deserialize`. Hasilnya kemudian dikelompokkan berdasarkan kategori dan dikirim ke template untuk ditampilkan.

   Jadi, alurnya adalah data diubah dari object Django menjadi JSON, kemudian diproses kembali agar bisa digunakan oleh kode Python dan ditampilkan di halaman web.

#### Penggunaan AI pada Tugas 3

Pada Tugas 3, saya menggunakan ChatGPT sebagai alat bantu selama proses pengerjaan dan pengecekan project. Saya memanfaatkan AI untuk membantu memahami instruksi Tugas 3 dan Tutorial 3, mencari penyebab error, serta memeriksa apakah implementasi yang saya buat sudah sesuai dengan ketentuan tugas.

Saya juga menggunakan AI untuk berdiskusi mengenai beberapa bagian implementasi, seperti `ExperienceForm`, CRUD Experience, endpoint JSON, routing UUID, migration, template, styling, dan unit test. Ketika menemukan error atau hasil yang belum sesuai, saya meminta bantuan AI untuk memahami masalahnya dan mencari solusi yang tepat.

AI saya gunakan sebagai pendamping dalam proses pengerjaan, bukan sebagai pengganti pemahaman dan keputusan saya sendiri. Saya tetap perlu memahami kode yang digunakan, memeriksa hasil perubahan, dan memastikan implementasinya sesuai dengan kebutuhan project.

Selama proses audit, saya meminta bantuan AI untuk mengidentifikasi beberapa masalah, seperti POST kosong yang tidak menampilkan error, validasi urutan tanggal, serta perilaku popover konfirmasi penghapusan pada tampilan browser. Dari proses tersebut, saya mendapatkan saran perbaikan yang kemudian saya periksa kembali melalui pengujian dan pengecekan secara langsung.

Saya melakukan verifikasi menggunakan Django system check, migration dry-run, test suite, dan pemeriksaan tampilan melalui browser lokal. Dengan begitu, saya tidak hanya mengandalkan hasil dari AI, tetapi juga memastikan bahwa perubahan yang dilakukan benar-benar sesuai dengan project saya.

Penggunaan AI dalam tugas ini membantu saya memahami langkah-langkah pengerjaan dan menemukan kesalahan selama proses pengembangan. Saya tetap bertanggung jawab untuk memahami, memeriksa, dan memastikan hasil akhir implementasi.