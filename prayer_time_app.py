import sys
import os
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import *
import math
import csv
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QComboBox,
    QSizePolicy,
    QDateEdit,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
)


# Fungsi-fungsi untuk kalkulasi waktu sholat tetap digunakan
def gregorian_to_julian_day(Y, M, D):
    if M == 1 or M == 2:
        M += 12
        Y -= 1

    A = Y // 100
    B = 2 + (A // 4) - A

    JD = 1720994.5 + int(365.25 * Y) + int(30.6001 * (M + 1)) + B + D
    
    return JD

def jd_to_hijri(jd):
    l = jd - 1948440 + 10632
    n = int((l - 1) / 10631)
    l = l - 10631 * n + 354
    j = (int((10985 - l) / 5316)) * (int((50 * l) / 17719)) + (int(l / 5670)) * (int((43 * l) / 15238))
    l = l - (int((30 - j) / 15)) * (int((17719 * j) / 50)) - (int(j / 16)) * (int((15238 * j) / 43)) + 29
    m = int((24 * l) / 709)
    d = int(l - int((709 * m) / 24) + 0.5)
    y = 30 * n + j - 30

    months = {
        1: "Muharram",
        2: "Safar",
        3: "Rabi' al-Awwal",
        4: "Rabi' al-Akhir",
        5: "Jumada al-Awal",
        6: "Jumada al-Akhir",
        7: "Rajab",
        8: "Sha'ban",
        9: "Ramadan",
        10: "Shawwal",
        11: "Dhu al-Qidah",
        12: "Dhu al-Hijjah"
    }

    return y, months[m], d
import math

# konversi kalender ke JD
def gregorian_to_julian_day(Y, M, D):
    if M == 1 or M == 2:
        M += 12
        Y -= 1

    A = Y // 100
    B = 2 + (A // 4) - A

    JD = 1720994.5 + int(365.25 * Y) + int(30.6001 * (M + 1)) + B + D
    
    return JD


def calculate_prayer_times(L, B, Z, H, D, M, Y, altitude_fajr, altitude_isha, KA=1):
    PI = math.pi

    # Step 1: Mengubah kalender Gregorian ke Julian Day
    JD = gregorian_to_julian_day(Y, M, D)
    JD = JD - Z / 24

    # Step 2: Menghitung Sudut Tanggal
    T = 2 * PI * (JD - 2451545) / 365.25

    # Step 3: Menghitung Deklinasi Matahari (Delta)
    Delta = 0.37877 + 23.264 * math.sin(57.297 * T - 79.547) + 0.3812 * math.sin(
        2 * 57.297 * T - 82.682) + 0.17132 * math.sin(
        3 * 57.297 * T - 59.722)

    # Step 4: Menghitung Equation of Time (ET)
    U = (JD - 2451545) / 36525
    L0 = 280.46607 + 36000.7698 * U
    ET = (- (1789 + 237 * U) * math.sin(L0 * PI / 180) - (7146 - 62 * U) * math.cos(
        L0 * PI / 180) + (9934 - 14 * U) * math.sin(2 * L0 * PI / 180) - (29 + 5 * U) * math.cos(
        2 * L0 * PI / 180) + (74 + 10 * U) * math.sin(3 * L0 * PI / 180) + (320 - 4 * U) * math.cos(
        3 * L0 * PI / 180) - 212 * math.sin(4 * L0 * PI / 180)) / 1000

    # Step 5: Menghitung waktu shalat
    Transit = 12 + Z - B / 15 - ET / 60
    ashar_altitude = math.degrees((math.atan(1 / (KA + math.tan(math.radians(abs(Delta - L)))))))
    fajr_altitude = -altitude_fajr
    isha_altitude = -altitude_isha
    maghrib_altitude = (-0.8333 - (0.0347 * math.sqrt(H)))

    hour_angle_fajr = math.degrees(math.acos((math.sin(math.radians(fajr_altitude)) - math.sin(math.radians(L)) * math.sin(math.radians(Delta))) / (math.cos(math.radians(L)) * math.cos(math.radians(Delta)))))
    hour_angle_isha = math.degrees(math.acos((math.sin(math.radians(isha_altitude)) - math.sin(math.radians(L)) * math.sin(math.radians(Delta))) / (math.cos(math.radians(L)) * math.cos(math.radians(Delta)))))
    hour_angle_ashar = math.degrees(math.acos((math.sin(math.radians(ashar_altitude)) - math.sin(math.radians(L)) * math.sin(math.radians(Delta))) / (math.cos(math.radians(L)) * math.cos(math.radians(Delta)))))
    hour_angle_maghrib = math.degrees(math.acos((math.sin(math.radians(maghrib_altitude)) - math.sin(math.radians(L)) * math.sin(math.radians(Delta))) / (math.cos(math.radians(L)) * math.cos(math.radians(Delta)))))

    zhuhur = Transit + 2 / 60  # Koreksi 2 menit
    ashar = Transit + (hour_angle_ashar / 15)
    maghrib = Transit + (hour_angle_maghrib / 15)
    isya = Transit + (hour_angle_isha / 15)
    shubuh = Transit - (hour_angle_fajr / 15)
    sunrise = Transit - (hour_angle_maghrib / 15)

    # Mengubah waktu ke format jam:menit:detik
    def format_time(hour):
        h = int(hour)
        m = int((hour % 1) * 60)
        s = int(((hour % 1) * 60 % 1) * 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    waktu_shalat = {
        "Transit": format_time(Transit),
        "Zhuhur": format_time(zhuhur),
        "Ashar": format_time(ashar),
        "Maghrib": format_time(maghrib),
        "Isya": format_time(isya),
        "Shubuh": format_time(shubuh),
        "Sunrise": format_time(sunrise)
    }

    return waktu_shalat


# Kelas untuk GUI menggunakan PyQt5
class PrayerTimeApp(QMainWindow):
    def __init__(self):
        super().__init__()

        current_date = QDate.currentDate()
        self.date_edit = QDateEdit(current_date)
        self.combo_year = QComboBox()
        self.combo_month = QComboBox()
        self.combo_day = QComboBox()

        self.setWindowTitle('Prayer Time Calculator V1.0')

        self.parent_layout = QVBoxLayout()
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.parent_layout)

        self.city_data = self.load_city_data()

        self._set_window_size()
        self._create_tittle()
        self._create_display()
        self._create_filter_location()
        self._create_info_location_button()
        self._create_filter_time()
        self._create_copyright()
        

    def _set_window_size(self):
        self.setMinimumWidth(600)
    
    def _show_location_info_popup(self):
        selected_country = self.combo_country.currentText()
        selected_city = self.combo_city.currentText()
        
        if selected_country == "Pilih Negara" or selected_city == "Pilih Kota":
            QMessageBox.warning(self, "Input Tidak Lengkap", "Masukkan input negara dan kota terlebih dahulu.")
            return

        # Pastikan selected_country ada di city_data
        if selected_country not in self.city_data:
            QMessageBox.warning(self, "Negara Tidak Ditemukan", f"Negara '{selected_country}' tidak ditemukan.")
            return

        # Pastikan selected_city ada di city_data[selected_country]
        if selected_city not in self.city_data[selected_country]:
            QMessageBox.warning(self, "Kota Tidak Ditemukan", f"Kota '{selected_city}' tidak ditemukan di negara '{selected_country}'.")
            return

        city_info = self.city_data[selected_country].get(selected_city, {})
        latitude = city_info.get('Latitude', 0)
        longitude = city_info.get('Longitude', 0)
        elevation = city_info.get('Elevation', 0)
        timezone = city_info.get('Time_zone', 0)

        info_text = (
            f"Negara: {selected_country}\n"
            f"Kota: {selected_city}\n"
            f"Latitude: {latitude}\n"
            f"Longitude: {longitude}\n"
            f"Elevasi: {elevation} meter\n"
            f"Zona Waktu: {timezone} jam dari UTC"
        )

        popup = QMessageBox(self)
        popup.setWindowTitle("Info Lokasi")
        popup.setText(info_text)
        popup.setFont(QFont("Arial", 8))
        popup.setIcon(QMessageBox.Information)
        popup.exec_()

    def load_city_data(self):
        # Get the path to the CSV file in the executable's directory
        base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        csv_file_path = os.path.join(base_path, "KOTA_DATABASE_COMPLETE.csv")

        # Dictionary to store city data
        city_data = {}

        # Open the CSV file and read its contents
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            # Use csv.DictReader to read the CSV file as a dictionary
            reader = csv.DictReader(file, delimiter=';')

            # Iterate over each row in the CSV file
            for row in reader:
                # Extract information from the row
                country = row.get('Country', '')
                city = row.get('City', '')

                latitude_str = row.get('Latitude', '0.0')
                try:
                    latitude = float(latitude_str.replace(',', '.'))
                except ValueError:
                    latitude = 0.0

                longitude_str = row.get('Longitude', '0.0')
                try:
                    longitude = float(longitude_str.replace(',', '.'))
                except ValueError:
                    longitude = 0.0

                elevation_str = row.get('Elevation', '0.0')
                try:
                    elevation = float(elevation_str.replace(',', '.'))
                except ValueError:
                    elevation = 0.0

                timezone = float(row.get('Time_zone', '0.0'))

                # Populate the city_data dictionary
                if country not in city_data:
                    city_data[country] = {}
                city_data[country][city] = {'Latitude': latitude, 'Longitude': longitude, 'Time_zone': timezone,'Elevation': elevation}

        # Return the populated city_data dictionary
        return city_data



    def _create_tittle(self):
        grid_layout = QGridLayout()

        self.judul = QLabel("Jadwal Sholat")
        self.judul.setStyleSheet("font-size:21px;font-weight:800")
        self.judul.setAlignment(Qt.AlignCenter)
        self.judul.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid_layout.addWidget(self.judul, 0, 0, 1, 2)

        self.tanggal = QLabel("Tanggal")
        self.tanggal.setAlignment(Qt.AlignCenter)
        self.tanggal.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.tanggal.setContentsMargins(0, 0, 0, 20)
        grid_layout.addWidget(self.tanggal, 1, 0, 1, 2)
        grid_layout.addWidget(self.tanggal, 1, 0, 1, 2)

        self.parent_layout.addLayout(grid_layout)


    def _create_display(self):
        grid_layout = QGridLayout()
        labels = ["Shubuh", "Sunrise", "Zhuhur", "Ashar", "Maghrib", "Isya"]
        for i, label_text in enumerate(labels, start=2):
            label_name = QLabel(label_text)
            label_name.setAlignment(Qt.AlignLeft)
            label_name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            label_name.setContentsMargins(100, 0, 0, 0)  # Set margin 20 dari kiri
            label = QLabel("00:00:00", objectName=f"{label_text}_label")
            label.setAlignment(Qt.AlignRight)
            label.setContentsMargins(0, 0, 100, 0)  # Set margin 20 dari kanan
            grid_layout.addWidget(label_name, i, 0)
            grid_layout.addWidget(label, i, 1)

        self.parent_layout.addLayout(grid_layout)

    def _create_info_location_button(self):
        # Tambahkan tombol untuk menampilkan informasi lokasi
        self.location_info_button = QPushButton("Info Lokasi")
        self.location_info_button.clicked.connect(self._show_location_info_popup)
        #self.location_info_button.setFixedWidth(550)

        #container_widget = QWidget()
        #container_layout = QVBoxLayout(container_widget)
        #container_layout.addWidget(self.location_info_button)
        #container_layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Letakkan widget container di bawah judul waktu dan tanggal
        self.parent_layout.addWidget(self.location_info_button)

    def _create_filter_location(self):
        div_layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 50, 0, 0)

        layout_province = QHBoxLayout()
        layout_province.addWidget(QLabel("Pilih Negara"))
        self.combo_country = QComboBox()
        self.combo_country.setEditable(True)
        self.combo_country.addItems(["Pilih Negara"] + list(self.city_data.keys()))
        self.combo_country.currentTextChanged.connect(self.country_changed)  # Fix here
        self.combo_country.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout_province.addWidget(self.combo_country)
        h_layout.addLayout(layout_province)

        layout_city = QHBoxLayout()
        layout_city.addWidget(QLabel("Pilih Kota"))
        self.combo_city = QComboBox()
        self.combo_city.setEditable(True)
        self.combo_city.addItems(["Pilih Kota"])
        self.combo_city.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout_city.addWidget(self.combo_city)
        h_layout.addLayout(layout_city)

        div_layout.addLayout(h_layout)  # Move h_layout into div_layout

        self.parent_layout.addLayout(div_layout)

    def country_changed(self, country):
        if country == "Pilih Negara Dulu" or country == "Pilih Negara":
            return

        cities = list(self.city_data.get(country, {}).keys())
        self.combo_city.clear()
        self.combo_city.addItems(["Pilih Kota"] + cities)


    def _create_filter_time(self):
        div_layout = QVBoxLayout()

        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Pilih Tahun"))
        self.combo_year.addItems(["Pilih Tahun"] + [str(year) for year in range(2000, 2101)])
        self.combo_year.currentTextChanged.connect(self.year_changed)
        h_layout.addWidget(self.combo_year)
        div_layout.addLayout(h_layout)

        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Pilih Bulan"))
        self.combo_month.addItems(["Pilih Bulan"] + ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
                                                      "Agustus", "September", "Oktober", "November", "Desember"])
        self.combo_month.currentTextChanged.connect(self.month_changed)
        h_layout.addWidget(self.combo_month)
        div_layout.addLayout(h_layout)

        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Pilih Tanggal"))
        self.combo_day.addItems(["Pilih Tanggal"])
        h_layout.addWidget(self.combo_day)
        div_layout.addLayout(h_layout)

        btn = QPushButton("Lihat Jadwal")
        btn.setFixedHeight(50)
        btn.clicked.connect(self.get_data)
        div_layout.addWidget(btn)

        self.parent_layout.addLayout(div_layout)


    def _create_copyright(self):
        div_layout = QVBoxLayout()

        label = QLabel()
        label.setAlignment(Qt.AlignCenter)
        label.setText("Program ini dibuat untuk memenuhi tugas akhir \n mata kuliah Astronomi Fisika UB 2023\n \n" +
                      "Dibuat Oleh:\nYu Ridho Maulana \n (215090301111011)\n \n" +
                      "Dosen Pembimbing:\n Dr. rer. nat. Abdurrouf, S.Si., M.Si.\n"
                      )
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        div_layout.addWidget(label)

        self.parent_layout.addLayout(div_layout)

    def country_changed(self, country):
        if country == "Pilih Negara Dulu" or country == "Pilih Negara":
            return

        cities = list(self.city_data.get(country, {}).keys())
        self.combo_city.clear()
        self.combo_city.addItems(["Pilih Kota"] + cities)

    def year_changed(self, year):
        if year == "Pilih Tahun Dulu" or year == "Pilih Tahun":
            return

        selected_month = self.combo_month.currentIndex()
        days = self.days_in_month(int(year), selected_month)
        self.update_day_combobox(days)

    def month_changed(self, month):
        if month == "Pilih Bulan Dulu" or month == "Pilih Bulan":
            return

        selected_year = int(self.combo_year.currentText())
        selected_month = self.combo_month.currentIndex()
        days = self.days_in_month(selected_year, selected_month)
        self.update_day_combobox(days)

    def update_day_combobox(self, days):
        self.combo_day.clear()
        self.combo_day.addItems(["Pilih Tanggal"] + [str(day) for day in range(1, days + 1)])

    def days_in_month(self, year, month):
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif month in [4, 6, 9, 11]:
            return 30
        elif month == 2:
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                return 29
            else:
                return 28
        else:
            return 0

    def get_data(self):
        
        selected_country = self.combo_country.currentText()
        selected_city = self.combo_city.currentText()

        if not selected_country or not selected_city:
            self.judul.setText("Pilih negara dan kota terlebih dahulu.")
            return
        
        self.judul.setText(f"Jadwal Sholat di {selected_city}")

        selected_year = self.combo_year.currentText()
        selected_month = self.combo_month.currentText()
        selected_day = self.combo_day.currentText()

        if selected_year == "Pilih Tahun" or selected_month == "Pilih Bulan" or selected_day == "Pilih Tanggal":
            QMessageBox.warning(self, "Input Tidak Lengkap", "Tolong masukkan input lokasi dan tanggal terlebih dahulu.")
            return

        try:
            selected_year = int(selected_year)
        except ValueError:
            QMessageBox.warning(self, "Input Tidak Valid", "Pilih tahun yang valid.")
            return

        selected_month = self.combo_month.currentIndex()
        selected_day = int(selected_day)

        date = QDate(selected_year, selected_month, selected_day)
        year, month, day = date.year(), date.month(), date.day()

        city_info = self.city_data[selected_country].get(selected_city, {})
        latitude = city_info.get('Latitude', 0)
        longitude = city_info.get('Longitude', 0)
        timezone = city_info.get('Time_zone', 0)
        elevation = city_info.get('Elevation', 0)

        result = calculate_prayer_times(latitude, longitude, timezone, elevation, day, month, year, 20, 18, 1)
        JD = gregorian_to_julian_day(year, month, day)
        hijri_year, hijri_month, hijri_day = jd_to_hijri(JD)

        prayer_times = [result[key] for key in ["Shubuh","Sunrise", "Zhuhur", "Ashar", "Maghrib", "Isya"]]

        self.tanggal.setText(f"tanggal {selected_day} {self.combo_month.currentText()} {selected_year}\n{hijri_day} {hijri_month} {hijri_year}")

        for label_text, prayer_time in zip(["Shubuh","Sunrise", "Zhuhur", "Ashar", "Maghrib", "Isya"], prayer_times):
            label = self.findChild(QLabel, f"{label_text}_label")
            if label:
                label.setText(prayer_time)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = PrayerTimeApp()
    main_window.show()
    sys.exit(app.exec_())
