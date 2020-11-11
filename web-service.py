import json
import logging
import numpy as np
import pandas as pd
import gen_th
import base64
import os
from IPython.core.debugger import Pdb
from http.server import BaseHTTPRequestHandler, HTTPServer
ipdb = Pdb()

# python3 -m http.server 8086 to run other server to open pdf

# function that receives parameters from the HTML webpage and returns a corresponding response in the form of a dictionary of data
def obtain_response(request_params):
    # parameters that were selected in the HTML webpage
    input_file_path = request_params['input_file_path']
    input_file_contents = request_params['input_file_contents']
    num_images = request_params['num_images']

    if not os.path.exists('tempfiles/'):
        os.mkdir('tempfiles')
    else:
        for file in os.listdir('tempfiles/'):
            os.remove('tempfiles/' + file)

    for i in range(num_images):
        image_file_path = request_params['image_file_path'+str(i)]
        image_file_contents = request_params['image_file_contents'+str(i)]
        with open('tempfiles/'+image_file_path, "wb") as fh:
            enc = image_file_contents + '=' * (-len(image_file_contents) % 4)
            fh.write(base64.decodebytes(str.encode(enc)))

    quiz_name = request_params['quiz_name']
    mode = request_params['mode']
    crypt = request_params['crypt']
    author_name = request_params['author_name']
    date = request_params['date']
    output_file_path = 'temp_pdfs/' + quiz_name + ".pdf"

    try:
        pdf = gen_th.main(input_file_contents, output_file_path, quiz_name, mode, crypt, author_name, date)
        response = {"pdf_attachment": output_file_path, "exception_message":""}
    except Exception as e:
        response = {"pdf_attachment": "", "exception_message":str(e)}

    if os.path.exists('tempfiles/'):
        for file in os.listdir('tempfiles/'):
            os.remove('tempfiles/' + file)
        os.rmdir('tempfiles')

    return json.dumps(response)

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        html_response = open('web-index.html','r').read()
        self.wfile.write(html_response.encode('utf-8'))

    def _set_json_response(self):
        self.send_response(200)
        self.send_header('Content-type','application/pdf')
        self.end_headers()

    def do_POST(self):
        # ipdb.set_trace()
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        print(content_length)
        # print(post_data)
        # logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
        #         str(self.path), str(self.headers), post_data.decode('utf-8'))
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\n", str(self.path), str(self.headers))
        request_params = json.loads(post_data.decode('utf-8'))
        self._set_json_response()
        obtained_response = obtain_response(request_params) ##This is what would change.
        self.wfile.write(obtained_response.encode('utf-8'))
        return obtained_response

def run(server_class=HTTPServer, handler_class=S, port=8085):
    logging.basicConfig(level=logging.INFO)
    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
