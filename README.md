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
