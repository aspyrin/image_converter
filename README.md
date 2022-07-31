# flask app image_converter on pillow and io lib
# implemented two options:

# 1. upload file from html-form ("multipart/form-data") and download edited file with file-dialog-box
    /convert_from_html_form

# 2. PUT file with curl and response file (save at local dir)
    /convert_from_curl/<filename>
    curl formate:
        curl -T '/home/user/dir/source_image.jpg' -o '/home/user/dir/edited_image.jpg' 
        http://localhost:8000/convert_from_curl/source_image.jpg

# 3. Function for testing curl, build curl from html-form and save edited file from response  
    /test_curl

# implemented file name secure validation
# implemented file extension validation (svg, png, jpg, jpeg, gif)
