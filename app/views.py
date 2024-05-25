from django.shortcuts import render, redirect
import qrcode, os, uuid, re, cv2, numpy as np, time, json


# from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.template import loader
import base64
from .models import QR_list
from .ocrapi import ocr_space_file


# Create your views here.

# reader = easyocr.Reader(['en'])
codes=[]

# print("sample data",result)
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

def generateQR(data):
  qr.add_data(data)
  qr.make(fit=True)
  QrImage = qr.make_image(fill_color="black", back_color="white")
  QrImage.save(f"static/images/QRcodes/{data}.png")
  new_qr = QR_list(labels=data)
  new_qr.save()
  return f"static/images/QRcodes/{data}.png"

# Use examples:


def checkAlreadyGenerated(data):
  # images = [i.split(".")[0] for i in os.listdir(r"static/images/QRcodes/")]
  images = [item.labels for item in QR_list.objects.all()]
  if data not in images:
    return generateQR(data)        
  return f"static/images/QRcodes/{data}.png"

def members(request):
  return render(request,'index.html')

def imshow(request):
  images = [{"code": code, "path": f"/static/images/QRcodes/{code}.png"} for code in codes]
  context = {"images": images}
  return render(request,'data.html',context)


def preprocess_image(image):
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply adaptive thresholding to binarize the image
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    
    # Morphological operations to remove noise and close gaps in between letters
    kernel = np.ones((3, 3), np.uint8)
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    return morph

def base64_to_cv2(image_data):
  # Convert to NumPy array
  np_array = np.frombuffer(image_data, np.uint8)
  
  # Decode image using OpenCV
  cv2_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
  
  return cv2_image

def capture_image(request):
  global codes
  if request.method == 'POST':
    image_data = request.POST.get('image_data')
    # Decode the base64 image data
    image_bytes = base64.b64decode(image_data.split(',')[1])
    image_bytes = base64_to_cv2(image_bytes)
    # Generate a unique filename
    image_bytes=  preprocess_image(image_bytes)
    # result = reader.readtext(image_bytes, detail = 0)
    filename = f"static/images/{int(time.time())}.png"
    cv2.imwrite(filename, image_bytes)
    try:
      result = ocr_space_file(filename=filename, language='pol')
    except Exception as e:print(e)
    parsed_text = json.loads(result)["ParsedResults"][0]['ParsedText']
    lines = parsed_text.split('\r\n')
    result = [line for line in lines if line.strip()]
   
    print(result)
    pattern = r'^[A-Z]+_[A-Z]+\d+$'
    for code in result:
      if re.match(pattern, code):
        codes.append(code)
        checkAlreadyGenerated(code)
    os.remove(filename)
    return redirect("imshow")
  else:
    return JsonResponse({'error': 'Invalid request method'}, status=400)
