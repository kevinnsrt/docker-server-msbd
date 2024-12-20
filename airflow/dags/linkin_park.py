from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime
import requests
import json
import mysql.connector
from pymongo import MongoClient
import time


dag = DAG(
    'linkin_park',
    default_args={'start_date': days_ago(1)},
    schedule_interval='0 */3 * * *',
    catchup=False
)


def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='mysql',
            user='root',
            password='', 
            database='spotify'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


def fetch_and_save_spotify_data():
    url = "https://spotify-statistics-and-stream-count.p.rapidapi.com/artist/6XyY86QOPPrYVGvF9ch6wz"
    headers = {
        "x-rapidapi-key": "9e8147b7fdmshfbe0fcce048273dp150bb6jsn3d64515ad611",
        "x-rapidapi-host": "spotify-statistics-and-stream-count.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        with open('/opt/airflow/linkin_park_spotify.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print("Spotify data saved to linkin_park_spotify.json successfully.")
    else:
        print(f"Error fetching data: {response.status_code}")


def upsert_artist(connection, data):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM artists WHERE id = %s", (data['id'],))
    result = cursor.fetchone()

    if result[0] > 0:  
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
    else:  
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
        if result[0] > 0:  
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
        else:  
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
        if result[0] > 0: 
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
        else:  
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


from pymongo import MongoClient
import time

def connect_to_mongo():
    retries = 5
    for _ in range(retries):
        try:

            client = MongoClient('mongodb://root:123@mongo:27017/', serverSelectionTimeoutMS=5000)

            client.admin.command('ping')
            db = client['youtube']  
            print("Successfully connected to MongoDB.")
            return db
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)
    print("Failed to connect to MongoDB after multiple attempts.")
    return None




def fetch_and_save_youtube_data():
    url = "https://yt-api.p.rapidapi.com/channel/videos"
    querystring = {"id": "UCZU9T1ceaOgwfLRq7OKFU4Q",}

    headers = {
        "x-rapidapi-key": "9e8147b7fdmshfbe0fcce048273dp150bb6jsn3d64515ad611",
        "x-rapidapi-host": "yt-api.p.rapidapi.com"
    }

    print("Fetching YouTube data...")
    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code != 200:
        print(f"Error: API request failed with status code {response.status_code}")
        return None

    try:
        data = response.json()
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

    print("API response successfully fetched.")

    if "data" in data and isinstance(data["data"], list):
        videos = data["data"]

        # Menyaring dan menyusun informasi video
        channel_statistics = []
        for video in videos:
            video_name = video.get("title", "Unknown Title")
            video_id = video.get("videoId", "Unknown ID")
            publish_date = video.get("publishDate", "Unknown Date")
            views = video.get("viewCount", "Unknown Views")
            timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            channel_statistics.append({
                "title": video_name,
                "videoId": video_id,
                "views": views,
                "publishDate": publish_date,
                "timestamp": timestamp_now
            })

        with open('/opt/airflow/linkin_park_youtube.json', 'w') as json_file:
            json.dump(channel_statistics, json_file, indent=4)

        print("Channel statistics saved to linkin_park_youtube.json")
        return channel_statistics
    else:
        print("No videos found or an error occurred.")
        return None


def save_to_mongo(db, data):
    if data:
        collection = db['channel_statistics_linkin_park']
        
        existing_data = collection.find({})
        if collection.count_documents({}) > 0:  
            print("Existing data found, moving to historical collection...")
            historical_collection = db['historical_channel_statistics_linkin_park']
            historical_collection.insert_many(existing_data)
            print("Existing data moved to historical collection.")

        collection.delete_many({})  
        collection.insert_many(data)
        print("New data for channel statistics successfully saved to MongoDB.")
    else:
        print("No data to save to MongoDB.")


def fetch_spotify_data():
    fetch_and_save_spotify_data()

def upsert_spotify_data():
    connection = connect_to_db()
    if not connection:
        print("Failed to connect to MySQL.")
        return

    with open('/opt/airflow/linkin_park_spotify.json', 'r') as json_file:
        data = json.load(json_file)

    upsert_artist(connection, data)
    upsert_top_cities(connection, data)
    upsert_top_tracks(connection, data)

    connection.close()


def fetch_youtube_data():
    return fetch_and_save_youtube_data()

def save_youtube_data():
    db = connect_to_mongo()
    if db is None:
        print("Failed to connect to MongoDB.")
        return

    with open('/opt/airflow/linkin_park_youtube.json', 'r') as json_file:
        data = json.load(json_file)

    save_to_mongo(db, data)


fetch_spotify_task = PythonOperator(
    task_id='fetch_spotify_data',
    python_callable=fetch_spotify_data,
    dag=dag
)

upsert_spotify_task = PythonOperator(
    task_id='upsert_spotify_data',
    python_callable=upsert_spotify_data,
    dag=dag
)

fetch_youtube_task = PythonOperator(
    task_id='fetch_youtube_data',
    python_callable=fetch_youtube_data,
    dag=dag
)

save_youtube_task = PythonOperator(
    task_id='save_youtube_data',
    python_callable=save_youtube_data,
    dag=dag
)

# Task dependencies
fetch_spotify_task >> upsert_spotify_task
fetch_youtube_task >> save_youtube_task
