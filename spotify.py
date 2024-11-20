import requests
import json
import mysql.connector

# Fungsi untuk menghubungkan ke database MySQL
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Sesuaikan password Anda
            database='spotify'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Fungsi untuk membaca file JSON
def read_json_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print("File JSON tidak ditemukan.")
        return None
    except json.JSONDecodeError as e:
        print(f"Kesalahan saat membaca JSON: {e}")
        return None

# Fungsi untuk menyimpan data dari API ke file JSON
def fetch_and_save_data():
    url = "https://spotify-statistics-and-stream-count.p.rapidapi.com/artist/47z98pKd71yIbgXwe9LPVC"
    
    headers = {
        "x-rapidapi-key": "065afcc0camsh8ddd21794759830p109244jsn8afdeb992d97",
        "x-rapidapi-host": "spotify-statistics-and-stream-count.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        with open('data.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print("Data berhasil disimpan ke data.json")
    else:
        print(f"Terjadi kesalahan saat mengambil data: {response.status_code}")

# Fungsi untuk memperbarui atau memasukkan data artis ke tabel artists
def upsert_artist(connection, data):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM artists WHERE id = %s", (data['id'],))
    result = cursor.fetchone()

    if result[0] > 0:  # Jika data sudah ada, lakukan update
        query = """
        UPDATE artists SET name = %s, verified = %s, followers = %s, monthlyListeners = %s, 
        worldRank = %s, biography = %s WHERE id = %s
        """
        artist_data = (
            data['name'],
            data['verified'],
            data['followers'],
            data['monthlyListeners'],
            data['worldRank'],
            data['biography'],
            data['id']
        )
        cursor.execute(query, artist_data)
        print("Data artis berhasil diupdate.")
    else:  # Jika data belum ada, lakukan insert
        query = """
        INSERT INTO artists (id, name, verified, followers, monthlyListeners, worldRank, biography)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        artist_data = (
            data['id'],
            data['name'],
            data['verified'],
            data['followers'],
            data['monthlyListeners'],
            data['worldRank'],
            data['biography']
        )
        cursor.execute(query, artist_data)
        print("Data artis berhasil dimasukkan.")
    connection.commit()


def upsert_top_cities(connection, data):
    cursor = connection.cursor()
    for city in data.get('topCities', []):
        cursor.execute("SELECT COUNT(*) FROM topcities WHERE artist_id = %s AND city = %s", (data['id'], city['city']))
        result = cursor.fetchone()
        if result[0] > 0:  # Jika data sudah ada, lakukan update
            query = """
            UPDATE topcities 
            SET country = %s, numberOfListeners = %s 
            WHERE artist_id = %s AND city = %s
            """
            city_data = (
                city['country'],
                city['numberOfListeners'],
                data['id'],
                city['city']
            )
            cursor.execute(query, city_data)
            print(f"Data kota {city['city']} berhasil diupdate.")
        else:  # Jika data belum ada, lakukan insert
            query = """
            INSERT INTO topcities (artist_id, city, country, numberOfListeners)
            VALUES (%s, %s, %s, %s)
            """
            city_data = (
                data['id'],
                city['city'],
                city['country'],
                city['numberOfListeners']
            )
            cursor.execute(query, city_data)
            print(f"Data kota {city['city']} berhasil dimasukkan.")
    connection.commit()

def upsert_top_tracks(connection, data):
    cursor = connection.cursor()
    for track in data.get('topTracks', []):
        cursor.execute("SELECT COUNT(*) FROM toptracks WHERE id = %s", (track['id'],))
        result = cursor.fetchone()
        if result[0] > 0:  # Jika track sudah ada, lakukan update
            query = """
            UPDATE toptracks 
            SET streamCount = %s, duration = %s, contentRating = %s 
            WHERE id = %s
            """
            track_data = (
                track['streamCount'],
                track['duration'],
                track['contentRating'],
                track['id']
            )
            cursor.execute(query, track_data)
            print(f"Track {track['name']} berhasil diupdate.")
        else:  # Jika track belum ada, lakukan insert
            query = """
            INSERT INTO toptracks (id, artist_id, name, streamCount, duration, contentRating)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            track_data = (
                track['id'],
                data['id'],
                track['name'],
                track['streamCount'],
                track['duration'],
                track['contentRating']
            )
            cursor.execute(query, track_data)
            print(f"Track {track['name']} berhasil dimasukkan.")
    connection.commit()


def main():
    # Langkah 1: Ambil data dari API dan simpan ke file JSON
    fetch_and_save_data()

    # Langkah 2: Koneksi ke database
    connection = connect_to_db()
    if not connection:
        print("Koneksi ke database gagal.")
        return

    # Langkah 3: Baca data dari file JSON
    data = read_json_file('data.json')
    if not data:
        print("Data tidak ditemukan di file JSON.")
        return

    try:
        # Perbarui atau masukkan data ke tabel masing-masing
        upsert_artist(connection, data)
        upsert_top_tracks(connection, data)
        upsert_top_cities(connection,data)
        print("Proses memperbarui/memasukkan data selesai.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
