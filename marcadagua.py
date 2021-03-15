from PIL import Image
import os
from io import BytesIO
import base64

# resolução do tablet camera frontal 1616x1212
def marcadagua(img):
    basedir = os.getcwd()
    waterpath = os.path.join(basedir, 'static', 'imgs_visita', 'll.png')
    
    buffer = BytesIO()
    im = Image.open(BytesIO(base64.b64decode(img)))
    width, height = im.size
    resized = im.thumbnail( (1616,1212), Image.ANTIALIAS)

    water = Image.open(waterpath)
    resized = water.thumbnail( (500, 500 ), Image.ANTIALIAS )

    o = im.paste(water, (210 , 210), water)
    im.rotate(90)
    im.save(buffer,'jpeg')
    buffer.seek(0)
    width, height = im.size
    print(width, height)
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode()




