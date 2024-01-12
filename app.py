from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from pymongo import MongoClient,DESCENDING
from google.cloud import storage
from datetime import datetime

app = Flask(__name__)

mongo_client = MongoClient(
    'mongodb+srv://amedikusettor:Skaq0084@myflixproject.soxjrzv.mongodb.net/?retryWrites=true&w=majority')
db = mongo_client['movieInfo']  # Change to your actual database name
metadata_collection = db['metadata']

# Google Cloud Storage Configuration
BUCKET_NAME = 'my-flix-videos'
client = storage.Client()
bucket = client.get_bucket(BUCKET_NAME)

# # Check if the index exists, and create it if it doesn't
# if 'timestamp' not in metadata_collection.index_information():
#     metadata_collection.create_index([('timestamp', DESCENDING)])

@app.route ('/')
def home():
    return render_template('movieUpload.html')


@app.route('/success')
def success():
    return render_template('uploadSuccess.html')

    
@app.route('/upload-movie', methods=['POST','GET'])
def upload_movie():
    if request.method == 'POST':
        # Get file from the form
        movie_file = request.files['movieFile']
        title = request.form['title']
        release_year = request.form['releaseYear']
        plot = request.form['plot']
        genres = request.form['genres'].split(',') if 'genres' in request.form else []

        # Additional Information
        mpaa_rating = request.form['mpaaRating']
        cast = request.form['cast'].split(',') if 'cast' in request.form else []
        languages = request.form['languages'].split(',') if 'languages' in request.form else []
        directors = request.form['directors'].split(',') if 'directors' in request.form else []
        writers = request.form['writers'].split(',') if 'writers' in request.form else []
        countries = request.form['countries'].split(',') if 'countries' in request.form else []

        # Choose Tier
        tier = request.form['tier']


        # Check if the file is selected
        if movie_file and allowed_file(movie_file.filename):
            filename = secure_filename(movie_file.filename)
            # Assuming tier is either 'ad-tier' or 'paid-tier'
            movie_file_path = f'{tier}/{filename}'

            # Upload the file to GCP bucket
            upload_movie_to_bucket(movie_file, movie_file_path)

            # Prepare data for MongoDB
            timestamp = datetime.now()
            update_count = get_update_count(title,release_year,filename)
            print("the update count is: ")
            print(update_count)
            movie_data = {
                'filename':filename,
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


def allowed_file(filename):
    # Add more allowed file types if needed
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp4'}


def upload_movie_to_bucket(movie_file, movie_file_path):
    blob = bucket.blob(movie_file_path)
    blob.upload_from_file(movie_file)


def get_update_count(title, release_year,filename):
    # Check if the movie already exists in the metadata collection
    existing_movie = metadata_collection.find(
        {'title': title, 'release_year':release_year, 'filename':filename}).sort('timestamp', DESCENDING).limit(1)
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
    app.run(debug=True,port = 6001)
