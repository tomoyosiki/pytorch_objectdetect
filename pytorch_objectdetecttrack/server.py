import object_detection
import os
from flask import Flask, request, Response, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return Response('Tensor Flow object detection')

@app.route('/test')
def test():

    PATH_TO_TEST_IMAGES_DIR = 'images'  # cwh
    TEST_IMAGE_PATHS = [os.path.join(PATH_TO_TEST_IMAGES_DIR, fileName) for fileName in os.listdir(PATH_TO_TEST_IMAGES_DIR)]

    image = TEST_IMAGE_PATHS[0]
    objects = object_detection.get_objects(image)

    return objects

@app.route('/image')
def image():
    try:
        #image_file = request.files['image']
        image_file = request.args.get('image')
        PATH_TO_TEST_IMAGES_DIR = 'images'  # cwh
        image = os.path.join(PATH_TO_TEST_IMAGES_DIR, image_file) 
        objects = object_detection.get_objects(image)
        return objects
    except Exception as e:
        print('POST /image error: %e' % e)
        return e

@app.route('/local')
def local():
    try:
        image_file = request.args.get('image')
        PATH_TO_TEST_IMAGES_DIR = 'static/images'  # cwh
        image = os.path.join(PATH_TO_TEST_IMAGES_DIR, image_file)
        if image.replace(".jpg", "-det.jpg") in os.listdir(PATH_TO_TEST_IMAGES_DIR):
            return render_template("simple.html", image_path=image.replace(".jpg", "-det.jpg"))
        image_path = object_detection.get_objects(image)
        return render_template("simple.html", image_path=image_path)
    except Exception as e:
        return str(e)

# for CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST') # Put any other methods you need here
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')