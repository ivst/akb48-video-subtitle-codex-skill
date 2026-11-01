# Skill Subtitle Video AKB48 untuk Codex

[English](README.md) · [Русский](README.ru.md) · [한국어](README.ko.md) · [Español (LatAm)](README.es-419.md) · [Bahasa Indonesia](README.id.md) · [ไทย](README.th.md) · [简体中文](README.zh-Hans.md) · [繁體中文](README.zh-Hant.md)

**Dokumentasi bahasa Indonesia ini masih berupa draf dan sebaiknya ditinjau penutur asli sebelum dianggap final.**


Alur kerja yang dapat digunakan ulang untuk menerjemahkan dan membuat subtitle video AKB48 dan 48 Group. Skill ini membantu Codex memisahkan dialog, atribusi pembicara, lagu, dan teks di layar; memeriksa ejaan nama; serta meninjau subtitle dan hasil render video.

Repositori ini berisi skill Codex, draf profil bahasa, pemeriksa SRT dasar, panduan pemasangan, dan dua contoh visual dari episode terbaru yang diterjemahkan ke bahasa Rusia. Profil Rusia didasarkan pada alur yang telah digunakan untuk episode penuh. Profil Korea masih berupa draf dan perlu ditinjau penutur asli; profil lainnya adalah titik awal bagi kontributor.

## Pratinjau

**Episode 12 — label pembicara dan panel subtitle ringkas** ([video sumber](https://www.youtube.com/watch?v=aPznmLtjedw))

![Contoh subtitle episode 12](examples/preview-episode-12.jpg)

*Sumber cuplikan: AKB48, **AKB48の全力エンタメ学園**, episode 12 (18 April 2026), [video asli di YouTube](https://www.youtube.com/watch?v=aPznmLtjedw).* Bingkai ini dipakai untuk membahas secara teknis label nama pembicara dan panel subtitle terjemahan yang ringkas. Contohnya membantu menilai pemisahan nama dari dialog tanpa hanya bergantung pada warna.

**Episode 13 — panel ringkas pada adegan jabat tangan terakhir** ([video sumber](https://www.youtube.com/watch?v=mHF3TEk6lwQ))

![Contoh subtitle episode 13](examples/preview-episode-13.jpg)

*Sumber cuplikan: AKB48, **AKB48の全力エンタメ学園**, episode 13 (25 April 2026), [video asli di YouTube](https://www.youtube.com/watch?v=mHF3TEk6lwQ).* Bingkai ini menjelaskan posisi panel subtitle pada adegan jabat tangan. Fokusnya adalah keterbacaan teks dan hubungannya dengan elemen visual asli, bukan menayangkan ulang episode sebagai hiburan.

Kedua gambar tersebut adalah **cuplikan dengan atribusi untuk pembahasan teknis desain subtitle**, bukan materi yang bebas digunakan ulang atau pengganti episode aslinya. Hak atas rekaman, penampilan artis, logo, dan elemen pihak ketiga tetap berada pada pemegang hak masing-masing. Lisensi **MIT tidak mencakup tangkapan layar ini**. Penyebutan sumber tidak otomatis memberikan izin untuk menyebarluaskannya. Lihat [NOTICE](NOTICE) untuk sumber dan catatan mengenai kutipan menurut hukum Jepang. Video sumber dan subtitle lengkap tidak disertakan.

## Menggunakan dengan Codex

Klon repositori ini dan buka foldernya di Codex. Skill berada di `.agents/skills/akb48-video-subtitles/` dan dapat ditemukan sebagai skill proyek. Untuk proyek lain, salin folder tersebut ke direktori skill Codex pengguna (biasanya `%USERPROFILE%\.codex\skills\akb48-video-subtitles` di Windows atau `$CODEX_HOME/skills/akb48-video-subtitles` jika `CODEX_HOME` dikonfigurasi). Mulai sesi Codex baru setelah pemasangan.

Panggil `$akb48-video-subtitles`, atau minta Codex menerjemahkan/meninjau video AKB48 dan sebutkan bahasa target serta berkas yang diperlukan. Sediakan video lokal atau sumber yang boleh digunakan, daftar anggota/nama jika ada, dan format hasil yang diinginkan. Alur yang dijelaskan tidak memerlukan API key.

## Persiapan cepat

Diperlukan Python 3.11+, FFmpeg, dan FFprobe. Untuk merender ASS, gunakan build FFmpeg yang menyertakan libass. Pasang FFmpeg melalui package manager sistem operasi dan pastikan `ffmpeg` serta `ffprobe` tersedia di `PATH`.

```powershell
python .agents/skills/akb48-video-subtitles/scripts/check_environment.py
python .agents/skills/akb48-video-subtitles/scripts/check_srt.py path\to\dialogue.srt
```

Skrip yang disertakan hanya memakai standard library Python; tidak perlu `pip install`. Lihat [kebutuhan sumber daya](.agents/skills/akb48-video-subtitles/references/resources.md).

## Alur kerja

1. Periksa transkrip bahasa Jepang dan catat papan, judul, aturan, serta hasil secara terpisah.
2. Terjemahkan dengan profil bahasa yang dipilih dan glosarium episode yang telah ditinjau.
3. Beri label pembicara hanya jika ada bukti; gunakan label netral untuk reaksi yang meragukan.
4. Buat SRT, ASS bergaya, dan/atau MP4 sesuai permintaan.
5. Tinjau beberapa adegan di sepanjang video dan hasil render akhir. Bila relevan, periksa decode, waktu, arsip, dan keutuhan audio.

Baca [panduan alur kerja](.agents/skills/akb48-video-subtitles/references/workflow.md) dan [profil bahasa](.agents/skills/akb48-video-subtitles/references/languages/README.md).

## Kebutuhan sumber daya

Untuk episode 1080p berdurasi 20–40 menit, RAM 8 GB dan CPU modern 4-core cukup sebagai titik awal. RAM 16 GB dan 6–8 core lebih nyaman untuk ASR lokal. Sediakan sekitar 10 GB ruang kosong untuk sumber, file sementara, render, dan cadangan. GPU bersifat opsional. Video 4K atau bitrate tinggi dapat memerlukan lebih banyak sumber daya. Ini hanya perkiraan; penggunaan aktual bergantung pada codec, model ASR, dan encoder.

## Hak dan privasi

Proses dan publikasikan hanya materi yang boleh Anda gunakan. Jangan masukkan transkrip episode, subtitle lengkap, kredensial, cookie, atau glosarium pribadi ke pull request publik tanpa izin redistribusi. Gambar contoh hanya menunjukkan tata letak subtitle; hak atas program tetap milik pemegang hak.

## Lisensi

Dokumentasi dan skrip orisinal menggunakan lisensi MIT. Gambar contoh dan materi program yang tampak di dalamnya tidak termasuk; lihat [NOTICE](NOTICE) dan [LICENSE](LICENSE).
