# Restaurant Management System

Python, Tkinter, ttkbootstrap ve SQLite ile masaustu restoran yonetimi uygulamasi (arayuz adi: OPTIMUS POS).

## Ozellikler

- Personel girisi
- 20 masa icin siparis ve hesap takibi
- Gorselli yiyecek, icecek ve tatli menusu
- Stok yonetimi
- Odeme kaydi ve gunluk satis grafigi

## Kurulum (Windows / PowerShell)

Python 3.9 veya uzeri ve Tkinter gereklidir. Windows Python kurulumunda Tcl/Tk secenegi etkin olmalidir.

```powershell
git clone https://github.com/Genkyu9988/restaurant-management-system.git
cd restaurant-management-system
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe restaurant_app.py
```

Komutlari proje klasorunden calistirin. Linux sistemlerde Tkinter ayri bir sistem paketi olarak kurulabilir.

## Giris

Ornek kullanici: `admin`, parola: `1234`.
Bu, eski egitim projesinin ornek girisidir; parolalar mevcut uygulamada duz metin saklanir.

## Dosyalar ve veriler

- `restaurant_app.py`: ana uygulama
- `db_manager.py`: veritabani ve baslangic menusu
- 21 PNG gorseli: menunun kullandigi tum urun gorselleri
- `requirements.txt`: kutuphane surumleri

`restaurant.db` ilk calistirmada otomatik olusturulur; ornek kullanici ve menu eklenir. Onceki satislar ve kullanici kayitlari repoya dahil edilmez. Mevcut verilerle devam etmek icin eski `restaurant.db` dosyanizi uygulama kapaliyken proje klasorune kopyalayabilirsiniz. Veritabani Git tarafindan yok sayilir.

Orijinal kaynak: bilgisayardaki PycharmProjects/PythonProject klasoru. Uygulama kaynak kodu degistirilmeden aktarilmistir.
