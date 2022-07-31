import requests
from flask import Flask, request, make_response
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'svg', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SAVE_FILE_IN_UPLOAD_FOLDER'] = False


def allowed_file(filename: str) -> bool:
    """
    function check allowed extensions
    :param filename:
    :return: bool
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/convert_from_html_form', methods=['POST', 'GET'])
def convert_from_html_form():
    """
    function for
    -on GET create form ("multipart/form-data") for upload file
    -on POST function upload the source local file, perform the conversion
    :return: download the modified file at local (open file dialog)
    """

    if request.method == 'POST':
        file = request.files['data_file']

        # file is exist validation
        if not file:
            return """
                        <html>
                            <body>
                                <p>No file!</p>
                                <a href='/'>Try again>>> </a>
                            </body>
                        </html>
                    """
        else:
            # file name secure validation
            file_name = secure_filename(file.filename)

            # file extension validation
            if not allowed_file(file_name):
                return f"""
                            <html>
                                <body>
                                    <p>This file extension is not supported: {file_name}</p>
                                    <p>Use extension: {ALLOWED_EXTENSIONS}</p>
                                    <a href='/'>Try again>>> </a>
                                </body>
                            </html>
                        """
            else:
                # create PIL object and define it format
                image_source = Image.open(file.stream)
                file_format = image_source.format

                # convert image greyscale
                image_edited = image_source.convert("L")

                # if you need to save edited image to static dir - change config on True
                if app.config['SAVE_FILE_IN_UPLOAD_FOLDER']:
                    edited_file_name = app.config['UPLOAD_FOLDER'] + '/' + file_name
                    image_edited.save(edited_file_name, file_format, optimize=True, quality=100)

                with BytesIO() as output:
                    image_edited.save(output, format=file_format)
                    img_byte_arr = output.getvalue()

                response = make_response(img_byte_arr)
                response.headers["Content-Disposition"] = f"attachment; filename={file_name};"
                return response

    if request.method == 'GET':
        return """
            <html>
                <body>
                    <h1>Convert a image to grayscale demo</h1>
                    <br>
                    <form action="/convert_from_html_form" method="POST" enctype="multipart/form-data">
                        <input type="file" id="ctrl_1" name="data_file" />
                        <input type="submit" value="Convert"/>
                    </form>
                </body>
            </html>
        """


@app.route('/convert_from_curl/<filename>', methods=['PUT'])
def convert_from_curl(filename):
    if request.method == 'PUT':
        # file name secure validation
        file_name = secure_filename(filename)
        # file extension validation
        if not allowed_file(file_name):
            message = f"This file extension is not supported. Use extension: {ALLOWED_EXTENSIONS}"
            return message, 415

        # file size validation
        if int(request.headers.get('Content-Length')) > 0:
            # create binary object from request data
            binary_source = BytesIO(request.get_data())

            # create PIL object and define it format
            image_source = Image.open(binary_source)
            image_format = image_source.format

            # convert image greyscale
            image_edited = image_source.convert("L")

            # if you need to save edited image to static dir - change config on True
            if app.config['SAVE_FILE_IN_UPLOAD_FOLDER']:
                edited_file_name = app.config['UPLOAD_FOLDER'] + '/' + file_name
                image_edited.save(edited_file_name, image_format, optimize=True, quality=100)

            # create binary object from edited image
            with BytesIO() as output:
                image_edited.save(output, format=image_format)
                img_byte_arr = output.getvalue()

                # create response
                response = make_response(img_byte_arr)
                response.headers["Content-Disposition"] = f"attachment; filename={file_name};"

                return response


@app.route('/test_curl', methods=['GET', 'POST'])
def test_curl():
    """
    function for testing 'def convert_from_curl'
    -on GET create form with params
    -on POST function upload the source local file, perform the conversion and save the modified file at local,
    The PUT query equivalent to the curl
        curl -T '/home/user/dir/source_image.jpg' -o '/home/user/dir/edited_image.jpg'
                                    http://localhost:8000/convert_from_curl/source_image.jpg
    :return: response code 'def convert_from_curl' and link on the modified file at local
    """

    source_url = request.host_url + 'convert_from_curl/'

    if request.method == 'POST':
        source_file_path = request.form.get('source_file_path')
        source_file_name = secure_filename(request.form.get('source_file_name'))
        output_file_path = request.form.get('output_file_path')
        output_file_name = secure_filename(request.form.get('output_file_name'))
        source_full_file_name = source_file_path + source_file_name
        source_url_with_param = source_url + source_file_name
        output_full_file_name = output_file_path + output_file_name

        with open(source_full_file_name, 'rb') as f:
            data = f.read()

        response = requests.put(source_url_with_param, data=data)
        if response.status_code == 200:
            with open(output_full_file_name, 'wb') as f:
                f.write(response.content)

            return f"""
                        <html>
                            <body>
                                <p>This is response from <strong>{source_url}</strong></p>
                                <p>Response code: <strong>{response.status_code}</strong></p>
                                <p>Original file location: <strong>{output_full_file_name}</strong></p>
                                <p>Converted file location: <strong>{output_full_file_name}</strong></p>
                            </body>
                        </html>
                    """
        else:
            return f"Test failed. Response status code:{response.status_code}."

    if request.method == 'GET':
        return f"""
            <html>
                <body>
                    <h1>
                    Test convert with curl
                    </h1>
                    <p>
                    The following extensions are available: {ALLOWED_EXTENSIONS}.
                    </p>
                    <p>Fill in the fields on the form and click the button 'Go test'</p>
                    <br>
                    <form method="POST">
                        <label for="input_1">Enter the path to the source file</label><br>
                        <input type="text" name="source_file_path" id="input_1"
                            placeholder="/home/user/dir/" required/><br>
                        <br>
                        <label for="input_2">Enter the name of source file</label><br>
                        <input type="text" name="source_file_name" id="input_2"
                            placeholder="source_image.jpg" required/><br>
                        <br>
                        <label for="input_3">Enter the path to save the edited file</label><br>
                        <input type="text" name="output_file_path" id="input_3"
                            placeholder="/home/user/dir/" required/><br>
                        <br>
                        <label for="input_4">Enter the name of edited file</label><br>
                        <input type="text" name="output_file_name" id="input_4"
                            placeholder="edited_image.jpg" required/><br>
                        <br>
                        <input type="submit" value="Go test"/>
                    </form>
                </body>
            </html>
        """


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
