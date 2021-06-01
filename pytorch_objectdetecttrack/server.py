import object_detection
import os
from flask import Flask, request, Response, render_template
import json
import requests
from pager import Pager

app = Flask(__name__)
def getAPI(type):
    if type == 'get_sensor_data':
        return lambda n: "http://127.0.0.1:5000/data/sensors/{}".format(n)
    if type == 'get_sensor_list':
        return lambda n: "http://127.0.0.1:5000/sensors/{}".format(n)

def get_api_return(_api):
    print("try to get API: {}".format(_api))
    resp = requests.get(_api)
    if resp.status_code == 200:        
        contents = str(resp.content)[2:-3]        
        return json.loads(contents)
    return None

get_available_camera_api = getAPI('get_sensor_list')
get_data_api = getAPI('get_sensor_data')

cameras_info = get_api_return(get_available_camera_api('camera'))
cameras_name = []
for camera in cameras_info['data']:
    cameras_name.append(camera['sensor_name'])
print("available sensors", cameras_name)

if len(cameras_name) > 0:
    select_camera = cameras_name[0]
data_list = get_api_return(get_data_api(select_camera))['data']
data_number = len(data_list)
pager = Pager(data_number)

@app.route('/')
def index():
    return Response('Tensor Flow object detection')

@app.route('/<int:ind>/')
def image_view(ind=None):
    if ind >= data_number:
        return render_template("404.html"), 404
    else:
        pager.current = ind
        local_name = data_list[ind]['token'] + '.jpg'
        image_origin_path = data_list[ind]['path']
        PATH_TO_TEST_IMAGES_DIR = 'static/images'  # cwh
        image = os.path.join(PATH_TO_TEST_IMAGES_DIR, local_name)
        print("origin : {}, local : {}".format(image_origin_path, image))
        if local_name not in os.listdir(PATH_TO_TEST_IMAGES_DIR):
            os.system('cp {} {}'.format(image_origin_path, image))
            if image.replace(".jpg", "-det.jpg") not in os.listdir(PATH_TO_TEST_IMAGES_DIR):
                image_path = object_detection.get_objects(image)
            return render_template('imageview.html', index=ind, pager=pager, data={'name':image.replace(".jpg", "-det.jpg")})
        else:
            return render_template('imageview.html', index=ind, pager=pager, data={'name':image.replace(".jpg", "-det.jpg")})
        


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
    app.run(debug=True, host='0.0.0.0', port=5001)
