import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind, f_oneway, pearsonr

# file sheet yang digunakan (dalam format url csv)
url = "https://docs.google.com/spreadsheets/d/1OMMIxN9VJ5RRyg2pBopFbxU8VnN1mNi_Rh8CeFxddew/gviz/tq?tqx=out:csv&sheet=count%20of%20attacks%20per%20day"
df_attacks_per_day = pd.read_csv(url)

# mengganti nama kolom untuk mempermudah akses
df_attacks_per_day.columns = ['Tanggal', 'jumlah', 'unused1', 'unused2']

# filtering baris yang hanya berisi data serangan harian (abaikan baris ringkasan)
df_attacks_per_day_cleaned = df_attacks_per_day[['Tanggal', 'jumlah']]
df_attacks_per_day_cleaned = df_attacks_per_day_cleaned[df_attacks_per_day_cleaned['jumlah'].notna()]

# konversi kolom jumlah ke format numerik dan kolom Tanggal ke format datetime
df_attacks_per_day_cleaned['jumlah'] = pd.to_numeric(df_attacks_per_day_cleaned['jumlah'], errors='coerce')
df_attacks_per_day_cleaned['Tanggal'] = pd.to_datetime(df_attacks_per_day_cleaned['Tanggal'])

# statistik deskriptif
statistik_deskriptif_jumlah = df_attacks_per_day_cleaned['jumlah'].describe()
print("Statistik Deskriptif untuk Jumlah Serangan Harian:")
print(statistik_deskriptif_jumlah)

# menambahkan kolom untuk hari dalam seminggu
df_attacks_per_day_cleaned['HariDalamMinggu'] = df_attacks_per_day_cleaned['Tanggal'].dt.dayofweek

# memisahkan data menjadi hari kerja (0-4) dan akhir pekan (5-6)
data_hari_kerja = df_attacks_per_day_cleaned[df_attacks_per_day_cleaned['HariDalamMinggu'] < 5]['jumlah']
data_akhir_pekan = df_attacks_per_day_cleaned[df_attacks_per_day_cleaned['HariDalamMinggu'] >= 5]['jumlah']

# melakukan uji-T antara hari kerja dan akhir pekan
t_stat, p_value = ttest_ind(data_hari_kerja, data_akhir_pekan, equal_var=False)
print("\nUji-T antara Hari Kerja dan Akhir Pekan:")
print(f"T-statistik: {t_stat}, P-value: {p_value}")

# ANOVA: membandingkan jumlah serangan di seluruh hari dalam seminggu
grup = [df_attacks_per_day_cleaned[df_attacks_per_day_cleaned['HariDalamMinggu'] == i]['jumlah']
        for i in range(7)]
anova_stat, anova_p_value = f_oneway(*grup)
print("\nANOVA untuk Jumlah Serangan di Seluruh Hari dalam Seminggu:")
print(f"F-statistik: {anova_stat}, P-value: {anova_p_value}")

# interval kepercayaan untuk weekdays vs weekend
z_score = 1.96  # interval kepercayaan 95%
n_hari_kerja = len(data_hari_kerja)
mean_hari_kerja = data_hari_kerja.mean()
std_hari_kerja = data_hari_kerja.std()
margin_error_hari_kerja = z_score * (std_hari_kerja / np.sqrt(n_hari_kerja))
ci_hari_kerja = (mean_hari_kerja - margin_error_hari_kerja, mean_hari_kerja + margin_error_hari_kerja)

n_akhir_pekan = len(data_akhir_pekan)
mean_akhir_pekan = data_akhir_pekan.mean()
std_akhir_pekan = data_akhir_pekan.std()
margin_error_akhir_pekan = z_score * (std_akhir_pekan / np.sqrt(n_akhir_pekan))
ci_akhir_pekan = (mean_akhir_pekan - margin_error_akhir_pekan, mean_akhir_pekan + margin_error_akhir_pekan)

print("\nInterval Kepercayaan untuk Jumlah Serangan:")
print(f"Hari Kerja: {ci_hari_kerja}")
print(f"Akhir Pekan: {ci_akhir_pekan}")
print(f"\n")

plt.figure(figsize=(12, 6))
plt.plot(df_attacks_per_day_cleaned.index, df_attacks_per_day_cleaned['jumlah'], label='Serangan Harian')
plt.axhline(y=df_attacks_per_day_cleaned['jumlah'].median(), color='r', linestyle='--', label=f'Median: {df_attacks_per_day_cleaned["jumlah"].median()}')  # Menambahkan garis median
plt.title("Serangan Harian Seiring Waktu dengan Garis Median")
plt.xlabel("Hari Sejak Awal Pengamatan")
plt.ylabel("Jumlah Serangan")
plt.legend()
plt.show()

# regresi: memeriksa tren seiring waktu
df_attacks_per_day_cleaned['HariNumerik'] = (df_attacks_per_day_cleaned['Tanggal'] -
                                             df_attacks_per_day_cleaned['Tanggal'].min()).dt.days
x = df_attacks_per_day_cleaned['HariNumerik']
y = df_attacks_per_day_cleaned['jumlah']
slope, intercept = np.polyfit(x, y, 1)
korelasi, p_value_korelasi = pearsonr(x, y)
print("\nRegresi dan Korelasi untuk Tren Seiring Waktu:")
print(f"Slope (Kemiringan): {slope}, Intercept: {intercept}")
print(f"Korelasi: {korelasi}, P-value: {p_value_korelasi}")
print(f"\n")

for derajat in range(2, 6):
    # regresi polinomial untuk setiap derajat (2, 3, 4, 5)
    koefisien = np.polyfit(x, y, derajat)
    y_pred = np.polyval(koefisien, x)

    print(f"Koefisien untuk Polinomial Derajat {derajat}: {koefisien}")

    korelasi = np.corrcoef(y, y_pred)[0, 1]
    print(f"Korelasi untuk Polinomial Derajat {derajat}: {korelasi}\n")

plt.figure(figsize=(12, 6))
plt.plot(df_attacks_per_day_cleaned['Tanggal'], df_attacks_per_day_cleaned['jumlah'], label='Observasi', color='black')
plt.plot(df_attacks_per_day_cleaned['Tanggal'], slope * x + intercept,
         label='Garis Tren Linear', color='red', linestyle='--')

for derajat in range(2, 6):
    prediksi_polinomial = np.polyval(np.polyfit(x, y, derajat), x)
    plt.plot(df_attacks_per_day_cleaned['Tanggal'], prediksi_polinomial,
             label=f'Garis Tren Polinomial Derajat {derajat}')
plt.title("Regresi Linear dan Polinomial untuk Serangan Siber Harian Seiring Waktu")
plt.xlabel("Tanggal")
plt.ylabel("Jumlah Serangan")
plt.legend()
plt.show()


# prediksi 30 hari ke depan dengan model polinomial
hari_masa_depan = np.arange(x.max() + 1, x.max() + 31)

plt.figure(figsize=(12, 6))

print(f"\n")
for derajat in range(2, 6):
    prediksi_masa_depan = np.polyval(np.polyfit(x, y, derajat), hari_masa_depan)
    plt.plot(hari_masa_depan, prediksi_masa_depan, label=f'Prediksi Polinomial Derajat {derajat}')
    print(f"Prediksi Polinomial Derajat {derajat} 30 Hari Ke Depan: ")
    print(f"{prediksi_masa_depan} \n")

prediksi_linear = slope * hari_masa_depan + intercept
print(f"Prediksi Linear 30 Hari Ke Depan: \n{prediksi_linear} \n")

plt.plot(hari_masa_depan, prediksi_linear, label='Prediksi Linear', color='red', linestyle='--')
plt.title("Prediksi 30 Hari Serangan Siber (Linear dan Polinomial Derajat 2-5)")
plt.xlabel("Hari Sejak Awal Pengamatan (Mulai dari Hari ke-1381 hingga Hari ke-1410)")
plt.ylabel("Jumlah Serangan yang Diprediksi")
plt.legend()
plt.show()

