import http.server
import socketserver

from http.server import BaseHTTPRequestHandler
from http import HTTPStatus


from PIL import Image

from io import BytesIO

import io

PORT = 8002

from image_preprocessing import DrImageClassifier, get_kaggle_classifier, get_zz_classifier, get_all_classifier

# from utils import mdb

import mdb
import imagehash
import os

import math
from glob import glob

kaggle_classifier = get_kaggle_classifier()
zz_classifier = get_zz_classifier()
all_classifier = get_all_classifier()

db, cursor = mdb.start_db_conn()
cursor.execute('select * from dr_image_tb')
print(cursor.fetchall())

db, cursor = mdb.start_db_conn1()
cursor.execute('select * from dranddme_images_tb')
print(cursor.fetchall())


image_root = './zhizhen'

class ImageHTTPRequestHandler(BaseHTTPRequestHandler):

    """Simple HTTP request handler with GET and HEAD commands.

    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method.

    The GET and HEAD requests are identical except that the HEAD
    request omits the actual contents of the file.

    """

    def __init__(self, request, client_address, server):
        self.root = './kaggle'
        self.num_perfolder = 100
        self.kaggle_train_data_num = 35000
        self.kaggle_test_data_num = 58000
        print('ImageHTTPRequestHandler initialized!')
        super(ImageHTTPRequestHandler, self).__init__(request, client_address, server)

    def do_GET(self):
        print('Content type: {0}'.format(self.headers['Content-type']))
        if self.headers['Content-type'] == 'image/jpeg':
            self._classify()
        elif self.headers['Content-type'] == 'text/plain':
            cmd = self.headers['cmd']
            print('client command: ' + cmd)
            if cmd == 'get_kaggle_train_folder':
                self._get_kaggle_train_folder()
            elif cmd == 'get_kaggle_test_folder':
                self._get_kaggle_test_folder()
            elif cmd == 'get_kaggle_train_image':
                self._get_kaggle_train_image()
            elif cmd == 'get_kaggle_test_image':
                self._get_kaggle_test_image()
            elif cmd == 'store_kaggle_annotation_result':
                self._store_kaggle_annotation_result()
            else:
                self._doctor_confirm()

    def do_POST(self):
        print('Content type: {0}'.format(self.headers['Content-type']))
        if self.headers['Content-type'] == 'image/jpeg':
            self._classify()
        elif self.headers['Content-type'] == 'text/plain':
            cmd = self.headers['cmd']
            print('client command: '+cmd)
            if cmd == 'get_kaggle_train_folder':
                self._get_kaggle_train_folder()
            elif cmd == 'get_kaggle_test_folder':
                self._get_kaggle_test_folder()
            elif cmd == 'get_kaggle_train_image':
                self._get_kaggle_train_image()
            elif cmd == 'get_kaggle_test_image':
                self._get_kaggle_test_image()
            elif cmd == 'store_kaggle_annotation_result':
                self._store_kaggle_annotation_result()
            else:
                self._doctor_confirm()

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type, Accept, Content-Length")
        self.end_headers()

            # def do_POST(self):
    #     data1 = self.rfile.read(int(self.headers['Content-Length']))
    #     # print(self.rfile.read())
    #     # f=open('3.jpg','wb')
    #     # f.write(data1)
    #     stream = BytesIO(data1)
    #     img = Image.open(stream)
    #     # print(img.size())
    #     idx,prop,prop1 = classifier.classifyImage(img)
    #     print('dr image is level: {}'.format(idx))
    #     self.send_response(HTTPStatus.OK)
    #     self.send_header("Content-type", 'text/plain')
    #     self.send_header("idx", str(idx))
    #     self.send_header("prop", str(prop1))
    #     self.end_headers()

    def _classify(self):
        data1 = self.rfile.read(int(self.headers['Content-Length']))
        stream = BytesIO(data1)
        img = Image.open(stream)
        image_id = imagehash.average_hash(img)

        algo = self.headers['algo']
        classifier = kaggle_classifier
        if algo == 'kaggle':
            classifier = kaggle_classifier
        elif algo == 'zz':
            classifier = zz_classifier
        elif algo == 'all':
            classifier = all_classifier

        idx,prop= classifier.classifyImage(img)
        print(prop)

        try:
            cmd_query = """select * from dr_image_tb where id='{0}'""".format(image_id)
            cursor.execute(cmd_query)
            query = cursor.fetchall()
            assert len(query) <= 1
            if len(query) == 0:
                imagepath = os.path.join(image_root, '{}.jpeg'.format(image_id))
                img.save(imagepath)
                cmd_insert = """insert into dr_image_tb (id, imagepath, algolevel) values ('{0}', '{1}', {2})""".format(
                    image_id, imagepath, idx
                )
            else:
                cmd_insert = """update dr_image_tb set algolevel={0} where id='{1}'""".format(
                    idx, image_id
                )
            cursor.execute(cmd_insert)
            cursor.execute('commit')
        except:
            print('database operation error!!!!')


        print('dr image is level: {}'.format(idx))
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Cookie")
        self.send_header("idx", str(idx))
        self.send_header("prop", str(prop))
        self.send_header("image_uid", str(image_id))
        self.end_headers()

    def _doctor_confirm(self):
        doctor_confirm_level = int(self.headers['level'])
        image_uid = self.headers['image_uid']
        cmd_inserttb = """update dr_image_tb set doctorlevel={0} where id='{1}'""".format(doctor_confirm_level, image_uid)
        try:
            cursor.execute(cmd_inserttb)
            cursor.execute('select * from dr_image_tb')
            print(cursor.fetchall())
            cursor.execute('commit')
        except:
            print('except when doctor confirm!')
        print('end inside _doctor_confirm')
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET')
        self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Cookie")
        self.send_header("image_uid", str(image_uid))
        self.end_headers()

    def _get_kaggle_train_folder(self):
        print('begin to get kaggle train folder')
        folder_num = math.ceil(self.kaggle_train_data_num // self.num_perfolder)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET')
        self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Cookie")
        self.send_header("cmd", 'get_kaggle_train_folder')
        self.send_header("folder_num", folder_num)
        self.end_headers()
        print('end to get kaggle train folder')

    def _get_kaggle_test_folder(self):
        print('begin to get kaggle test folder')
        folder_num = math.ceil(self.kaggle_test_data_num // self.num_perfolder)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET')
        self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Cookie")
        self.send_header("cmd", 'get_kaggle_test_folder')
        self.send_header("folder_num", folder_num)
        self.end_headers()
        print('end to get kaggle test folder')

    def _get_kaggle_train_image(self):
        print('begin to get kaggle train image ')
        sub_idx = self.headers['sub_index']
        folder_index = self.headers['folder_index']
        images_path = os.path.join(self.root, 'train/'+str(folder_index))
        print('images path: ' + images_path)
        images_list = glob(os.path.join(images_path, '*.jpeg'))
        image = images_list[int(sub_idx)]
        # image = '/home/weidong/code/dr/DiabeticRetinopathy_solution/data/dme/dme/33_dr_0_dme_0.jpg'
        data = open(image, 'rb').read()
        pil_img = Image.open(image)
        # image_uid = imagehash.average_hash(pil_img)
        image_uid = os.path.basename(image)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", 'image/jpeg')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET')
        self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Cookie")
        self.send_header("cmd", 'get_kaggle_train_image')
        self.send_header("image_uid", str(image_uid))
        self.end_headers()
        self.wfile.write(data)
        print('end to get kaggle train image')


    def _get_kaggle_test_image(self):
        print('begin to get kaggle test image ')
        sub_idx = self.headers['sub_index']
        folder_index = self.headers['folder_index']
        images_path = os.path.join(self.root, 'test/'+str(folder_index))
        print('images path: ' + images_path)
        images_list = glob(os.path.join(images_path, '*.jpeg'))
        image = images_list[int(sub_idx)]
        # image = '/home/weidong/code/dr/DiabeticRetinopathy_solution/data/dme/dme/34_dr_2_dme_1.jpg'
        data = open(image, 'rb').read()
        pil_img = Image.open(image)
        # image_uid = imagehash.average_hash(pil_img)
        image_uid = os.path.basename(image)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", 'image/jpeg')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET')
        self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Cookie")
        self.send_header("cmd", 'get_kaggle_test_image')
        self.send_header("image_uid", str(image_uid))
        self.end_headers()
        self.wfile.write(data)
        print('end to get kaggle test image')

    def _store_kaggle_annotation_result(self):
        dr_level = int(self.headers['dr_level'])
        dme_level = int(self.headers['dme_level'])
        doctor_id = self.headers['doctor_id']
        image_uid = self.headers['image_uid']
        image_path = ''
        cmd_inserttb = """update dranddme_images_tb set doctorid='{0}',drlevel={1},dmelevel={2} where id='{3}'""".format(doctor_id,dr_level, dme_level, image_uid)

        try:
            cmd_query = """select * from dranddme_images_tb where id='{0}'""".format(image_uid)
            cursor.execute(cmd_query)
            query = cursor.fetchall()
            print(query)
            assert len(query) <= 1
            if len(query) == 0:
                # imagepath = os.path.join(image_root, '{}.jpeg'.format(image_id))
                # img.save(imagepath)
                cmd_insert = """insert into dranddme_images_tb (id, doctorid, imagepath, drlevel, dmelevel) values ('{0}', '{1}', '{2}', {3}, {4})""".format(
                    image_uid, doctor_id, image_path, dr_level, dme_level
                )
            else:
                cmd_insert = cmd_inserttb
            print(cmd_inserttb)
            cursor.execute(cmd_insert)
            cursor.execute('commit')
        except:
            print('database operation error!!!!')

        # try:
        #     cursor.execute(cmd_inserttb)
        #     cursor.execute('select * from dr_image_tb')
        #     print(cursor.fetchall())
        #     cursor.execute('commit')
        # except:
        #     print('except when store kaggle annotation result!')

        print('end to store kaggle annotation result')
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET')
        self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Cookie")
        self.send_header("image_uid", str(image_uid))
        self.end_headers()
        return 501

Handler = ImageHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()



# 问题解决：http://stackoverflow.com/questions/20689958/cannot-get-response-body-from-post-request-python
    # def do_POST(self):
    #     content = bytes("TEST RESPONSE", "UTF-8")
    #     self.send_response(200)
    #     self.send_header("Content-type", "text/plain")
    #     self.send_header("Content-Length", len(content))
    #     self.end_headers()
    #     print(self.rfile.read(int(self.headers['Content-Length'])).decode("UTF-8"))
    #     self.wfile.write(content)