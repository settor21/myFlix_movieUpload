from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from pymongo import MongoClient, DESCENDING
from google.cloud import storage
from datetime import datetime
from urllib.parse import quote_plus
import cv2
import os


app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize MongoDB client
username = 'amedikusettor'
password = 'Praisehim69%'

# Escape the username and password
escaped_username = quote_plus(username)
escaped_password = quote_plus(password)

# Construct the MongoDB URI with escaped username and password
mongo_uri = f'mongodb://{escaped_username}:{escaped_password}@35.239.170.49:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.1.1'

# Create the MongoClient
mongo_client = MongoClient(mongo_uri)


db = mongo_client['movieInfo']  # Change to your actual database name
metadata_collection = db['metadata']

# Google Cloud Storage Configuration
BUCKET_NAME = 'my-flix-videos'
client = storage.Client()
bucket = client.get_bucket(BUCKET_NAME)

# # Check if the index exists, and create it if it doesn't
# if 'timestamp' not in metadata_collection.index_information():
#     metadata_collection.create_index([('timestamp', DESCENDING)])


@app.route('/')
def home():
    return render_template('movieUpload.html')


@app.route('/success')
def success():
    return render_template('uploadSuccess.html')


@app.route('/upload-movie', methods=['POST', 'GET'])
def upload_movie():
    if request.method == 'POST':
        # Get file from the form
        movie_file = request.files['movieFile']
        title = request.form['title']
        release_year = request.form['releaseYear']
        plot = request.form['plot']
        genres = request.form['genres'].split(
            ',') if 'genres' in request.form else []

        # Additional Information
        mpaa_rating = request.form['mpaaRating']
        cast = request.form['cast'].split(
            ',') if 'cast' in request.form else []
        languages = request.form['languages'].split(
            ',') if 'languages' in request.form else []
        directors = request.form['directors'].split(
            ',') if 'directors' in request.form else []
        writers = request.form['writers'].split(
            ',') if 'writers' in request.form else []
        countries = request.form['countries'].split(
            ',') if 'countries' in request.form else []

        # Choose Tier
        tier = request.form['tier']

        # Check if the file is selected
        if movie_file and allowed_file(movie_file.filename):
            filename = secure_filename(movie_file.filename)
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp.mp4')
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            i=0
            # Stream the movie file to the temporary location and break after capturing the first frame
            with open(video_path, 'wb') as temp_file:
                while i<5:
                    chunk = movie_file.stream.read(8192)
                    if not chunk:
                        break
                    temp_file.write(chunk)

                    # Open the temporary video file to check if the first frame is captured
                    cap = cv2.VideoCapture(video_path)
                    success, _ = cap.read()
                    cap.release()

                    if success:
                        break
                    i+=1

            # Reset the stream to the beginning
            movie_file.seek(0)
            # Generate thumbnail
            thumbnail_filename = os.path.splitext(
                os.path.basename(filename))[0] + '.png'

            thumbnail_path = os.path.join(
                app.config['UPLOAD_FOLDER'], thumbnail_filename)
            generate_thumbnail(video_path, thumbnail_path)

            # Specify the thumbnail file path in the bucket
            thumbnail_file_path = f'thumbnail/{thumbnail_filename}'

            # Upload the thumbnail to the bucket
            upload_thumbnail_to_bucket(thumbnail_path, thumbnail_file_path)

            # Remove the temporary video file and thumbnail
            os.remove(video_path)
            os.remove(thumbnail_path)

            # upload_thumbnail_to_bucket('myflix-staticfiles',thumbnail_path,f'thumbnail/{thumbnail_name}')

            # Assuming tier is either 'ad-tier' or 'paid-tier'
            movie_file_path = f'{tier}/{filename}'

            # Upload the file to GCP bucket
            upload_movie_to_bucket(movie_file, movie_file_path)

            # Prepare data for MongoDB
            timestamp = datetime.now()
            update_count = get_update_count(title, release_year, filename)
            print("the update count is: ")
            print(update_count)
            movie_data = {
                'filename': filename,
                'title': title,
                'release_year': release_year,
                'plot': plot,
                'genres': genres,
                'mpaa_rating': mpaa_rating,
                'cast': cast,
                'languages': languages,
                'directors': directors,
                'writers': writers,
                'countries': countries,
                'tier': tier,
                'timestamp': timestamp,
                'update_count': update_count
            }

            # Upload data to MongoDB
            metadata_collection.insert_one(movie_data)

            return redirect(url_for('success'))  # Redirect to a success page

    elif request.method == 'GET':
        # Redirect to the home page for GET requests
        return redirect(url_for('home'))

    # Render the form again if not successful
    return render_template('movieUpload.html')


def generate_thumbnail(video_path, thumbnail_path):
    cap = cv2.VideoCapture(video_path)
    success, image = cap.read()
    if success:
        cv2.imwrite(thumbnail_path, image)
    cap.release()


def upload_thumbnail_to_bucket(thumbnail_path, thumbnail_file_path):
    # Get the bucket
    bucket = client.get_bucket("myflix-staticfiles")

    # Create a blob with the thumbnail file path
    blob = bucket.blob(thumbnail_file_path)

    # Upload the thumbnail to the bucket
    blob.upload_from_filename(thumbnail_path)


def allowed_file(filename):
    # Add more allowed file types if needed
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp4'}


def upload_movie_to_bucket(movie_file, movie_file_path):
    blob = bucket.blob(movie_file_path)
    blob.upload_from_file(movie_file)


def get_update_count(title, release_year, filename):
    # Check if the movie already exists in the metadata collection
    existing_movie = metadata_collection.find(
        {'title': title, 'release_year': release_year, 'filename': filename}).sort('timestamp', DESCENDING).limit(1)
    print(existing_movie)
    update_count = 0

    for doc in existing_movie:
        print(doc)
        if doc:
         # Movie exists, get the latest update_count and increment by 1
            update_count = doc['update_count'] + 1
        else:
            # Movie does not exist, set update_count to 0
            update_count = 0
    return update_count


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=6001)
