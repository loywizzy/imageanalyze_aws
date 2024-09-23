from flask import Flask, render_template, request, redirect, url_for
import boto3 , os
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
bucket_name = 'imageanalysisy'

# สร้าง client สำหรับ S3 และ Rekognition
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='ap-southeast-2')

# ฟังก์ชันสำหรับวิเคราะห์ label ในภาพ
def detect_labels(photo, bucket):
    response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MaxLabels=10
    )
    return response['Labels']

# ฟังก์ชันสำหรับตรวจจับข้อความและวาด Bounding Box
# def detect_text_and_draw_bounding_box(photo, bucket):
    session = boto3.Session(profile_name='default')
    client = session.client('rekognition')

    response = client.detect_text(Image={'S3Object': {'Bucket': bucket, 'Name': photo}})

    # ดาวน์โหลดภาพจาก S3
    s3.download_file(bucket, photo, photo)

    # เปิดภาพที่ดาวน์โหลดมา
    image = Image.open(photo)
    img_width, img_height = image.size
    draw = ImageDraw.Draw(image)

    # วาด Bounding Box สำหรับข้อความที่ตรวจจับได้
    for text in response['TextDetections']:
        if 'Geometry' in text:
            box = text['Geometry']['BoundingBox']
            left = img_width * box['Left']
            top = img_height * box['Top']
            width = img_width * box['Width']
            height = img_height * box['Height']
            right = left + width
            bottom = top + height

            # วาดกรอบสี่เหลี่ยมรอบข้อความ
            draw.rectangle([left, top, right, bottom], outline="red", width=2)

            # วาดข้อความตรวจจับได้ด้านบนกรอบ
            draw.text((left, top - 20), text['DetectedText'], fill="red")

    # สร้างชื่อไฟล์ที่ไม่ซ้ำกัน
    if not os.path.exists('static'):
        os.makedirs('static')
    
    output_image_path = f'static/output_with_bounding_boxes_{photo}'
    image.save(output_image_path)

    return output_image_path



# ฟังก์ชันสำหรับตรวจจับข้อความและวาด Bounding Box

    session = boto3.Session(profile_name='default')
    client = session.client('rekognition')

    response = client.detect_text(Image={'S3Object': {'Bucket': bucket, 'Name': photo}})

    # ดาวน์โหลดภาพจาก S3
    s3.download_file(bucket, photo, photo)

    # เปิดภาพที่ดาวน์โหลดมา
    image = Image.open(photo)
    img_width, img_height = image.size
    draw = ImageDraw.Draw(image)

    # สร้างรายการเก็บข้อความที่ตรวจจับได้
    detected_texts = []

    # วาด Bounding Box สำหรับข้อความที่ตรวจจับได้
    for text in response['TextDetections']:
        if 'Geometry' in text:
            box = text['Geometry']['BoundingBox']
            left = img_width * box['Left']
            top = img_height * box['Top']
            width = img_width * box['Width']
            height = img_height * box['Height']
            right = left + width
            bottom = top + height

            # วาดกรอบสี่เหลี่ยมรอบข้อความ
            draw.rectangle([left, top, right, bottom], outline="red", width=10)

            # เพิ่มข้อความที่ตรวจจับได้ในรายการ
            detected_texts.append(text['DetectedText'])

            # วาดข้อความตรวจจับได้ด้านบนกรอบ
            draw.text((left, top - 20), text['DetectedText'], fill="red")

    # สร้างชื่อไฟล์ที่ไม่ซ้ำกัน
    if not os.path.exists('static'):
        os.makedirs('static')
    
    output_image_path = f'static/output_with_bounding_boxes_{photo}'
    image.save(output_image_path)

    # ส่งคืนเส้นทางของภาพและข้อความที่ตรวจจับได้
    return output_image_path, detected_texts
# ฟังก์ชันสำหรับวาดข้อความด้วยกรอบ
def draw_text_with_outline(draw, position, text, font, text_color="white", outline_color="black", outline_width=2):
    x, y = position
    # วาดขอบโดยรอบข้อความด้วย outline_color
    draw.text((x - outline_width, y), text, font=font, fill=outline_color)
    draw.text((x + outline_width, y), text, font=font, fill=outline_color)
    draw.text((x, y - outline_width), text, font=font, fill=outline_color)
    draw.text((x, y + outline_width), text, font=font, fill=outline_color)
    draw.text((x - outline_width, y - outline_width), text, font=font, fill=outline_color)
    draw.text((x + outline_width, y - outline_width), text, font=font, fill=outline_color)
    draw.text((x - outline_width, y + outline_width), text, font=font, fill=outline_color)
    draw.text((x + outline_width, y + outline_width), text, font=font, fill=outline_color)
    
    # วาดข้อความข้างในด้วย text_color
    draw.text((x, y), text, font=font, fill=text_color)

# ฟังก์ชันตรวจจับข้อความและวาด Bounding Box
def detect_text_and_draw_bounding_box(photo, bucket):
    session = boto3.Session(profile_name='default')
    client = session.client('rekognition')

    response = client.detect_text(Image={'S3Object': {'Bucket': bucket, 'Name': photo}})

    # ดาวน์โหลดภาพจาก S3
    s3.download_file(bucket, photo, photo)

    # เปิดภาพที่ดาวน์โหลดมา
    image = Image.open(photo)
    img_width, img_height = image.size
    draw = ImageDraw.Draw(image)

    # สร้างรายการเก็บข้อความที่ตรวจจับได้
    detected_texts = []

    # กำหนดฟอนต์และขนาดตัวอักษร
    font_size = 20  # ปรับขนาดตามต้องการ
    font = ImageFont.truetype("arial.ttf", font_size)

    # วาด Bounding Box สำหรับข้อความที่ตรวจจับได้
    for text in response['TextDetections']:
        if 'Geometry' in text:
            box = text['Geometry']['BoundingBox']
            left = img_width * box['Left']
            top = img_height * box['Top']
            width = img_width * box['Width']
            height = img_height * box['Height']
            right = left + width
            bottom = top + height

            # วาดกรอบสี่เหลี่ยมรอบข้อความ
            draw.rectangle([left, top, right, bottom], outline="red", width=1)

            # เพิ่มข้อความที่ตรวจจับได้ในรายการ
            detected_texts.append(text['DetectedText'])

            # วาดข้อความตรวจจับได้ด้วยกรอบตัวอักษรและขนาดที่กำหนด
            draw_text_with_outline(draw, (left, top - font_size - 15), text['DetectedText'], font, text_color="white", outline_color="black", outline_width=2)

    # สร้างชื่อไฟล์ที่ไม่ซ้ำกัน
    if not os.path.exists('static'):
        os.makedirs('static')
    
    output_image_path = f'static/output_with_bounding_boxes_{photo}'
    image.save(output_image_path)

    # ส่งคืนเส้นทางของภาพและข้อความที่ตรวจจับได้
    return output_image_path, detected_texts


# เพิ่มหน้าใหม่สำหรับตรวจจับข้อความ
# @app.route('/detect_text', methods=['POST'])
# def handle_detect_text():
#     if 'file' not in request.files:
#         return 'No file part'
#     file = request.files['file']
#     if file.filename == '':
#         return 'No selected file'

#     # อัปโหลดภาพไปยัง S3
#     bucket_name = 'imageanalysisy'
#     s3.upload_fileobj(file, bucket_name, file.filename)

#     # ตรวจจับข้อความและวาด Bounding Box พร้อมรับข้อความที่ตรวจจับได้
#     output_image_path, detected_texts = detect_text_and_draw_bounding_box(file.filename, bucket_name)

#     # ส่งภาพและข้อความไปยังเทมเพลตเพื่อแสดงผล
#     return render_template('display.html', image_file=os.path.basename(output_image_path), detected_texts=detected_texts)

@app.route('/detect_text', methods=['POST'])
def handle_detect_text():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    # อัปโหลดภาพไปยัง S3
    bucket_name = 'imageanalysisy'
    s3.upload_fileobj(file, bucket_name, file.filename)

    # ตรวจจับข้อความและวาด Bounding Box พร้อมรับข้อความที่ตรวจจับได้
    output_image_path, detected_texts = detect_text_and_draw_bounding_box(file.filename, bucket_name)

    # ส่งข้อมูลข้อความไปยังเทมเพลตเพื่อแสดงผล
    return render_template('display.html', image_file=os.path.basename(output_image_path), labels=None, detected_texts=detected_texts)

# สร้าง Navbar
@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/service')
def services():
    return render_template('service.html')

# @app.route('/', methods=['POST'])
# def upload_image():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    # อัปโหลดภาพไปยัง S3
    bucket_name = 'imageanalysisy'
    s3.upload_fileobj(file, bucket_name, file.filename)

    # วิเคราะห์ Labels
    labels = detect_labels(file.filename, bucket_name)

    # ดาวน์โหลดภาพจาก S3 และเพิ่ม Label ลงบนภาพ
    s3.download_file(bucket_name, file.filename, file.filename)
    image = Image.open(file.filename)
    draw = ImageDraw.Draw(image)

    # ใช้ฟอนต์และขนาด
    font_size = 80
    font = ImageFont.truetype("arial.ttf", font_size)

    # วาด label บนภาพ
    for index, label in enumerate(labels):
        text = f"{label['Name']} ({label['Confidence']:.2f}%)"
        position = (10, 10 + index * (font_size + 10))
        draw.text(position, text, fill="white", font=font)

    # สร้างชื่อไฟล์ที่ไม่ซ้ำกัน
    if not os.path.exists('static'):
        os.makedirs('static')
    output_image_path = f'static/output_with_labels_{file.filename}'
    image.save(output_image_path)

    return redirect(url_for('display_image', image_file=f'output_with_labels_{file.filename}'))

@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    # อัปโหลดภาพไปยัง S3
    bucket_name = 'imageanalysisy'
    s3.upload_fileobj(file, bucket_name, file.filename)

    # วิเคราะห์ Labels
    labels = detect_labels(file.filename, bucket_name)

    # ดาวน์โหลดภาพจาก S3 และเพิ่ม Label ลงบนภาพ
    s3.download_file(bucket_name, file.filename, file.filename)
    image = Image.open(file.filename)
    img_width, img_height = image.size
    draw = ImageDraw.Draw(image)

    # คำนวณขนาดตัวอักษรที่เหมาะสม
    base_font_size = min(img_width, img_height) // 30
    font_size = max(12, min(base_font_size, 60))  # ขนาดตัวอักษรอยู่ระหว่าง 12 ถึง 60
    font = ImageFont.truetype("arial.ttf", font_size)

    # คำนวณพื้นที่สำหรับเขียน label
    max_labels = 10
    label_area_height = min(img_height // 2, max_labels * (font_size + 5))
    label_area_width = img_width // 3

    # วาด label บนภาพ
    for index, label in enumerate(labels[:max_labels]):
        text = f"{label['Name']} ({label['Confidence']:.2f}%)"
        text_width = draw.textlength(text, font=font)
        
        # ปรับตำแหน่งของ label
        x = 10
        y = 10 + index * (font_size + 5)
        
        # เขียน label
        draw.text((x + 5, y), text, fill="white", font=font)

    # สร้างชื่อไฟล์ที่ไม่ซ้ำกัน
    if not os.path.exists('static'):
        os.makedirs('static')
    output_image_path = f'static/output_with_labels_{file.filename}'
    image.save(output_image_path)

    # ส่งข้อมูล label ไปยังเทมเพลตเพื่อแสดงผล
    return render_template('display.html', image_file=f'output_with_labels_{file.filename}', labels=labels, detected_texts=None)


@app.route('/display/<image_file>')
def display_image(image_file):
    return render_template('display.html', image_file=image_file)

# เพิ่มหน้าใหม่สำหรับตรวจจับข้อความ
@app.route('/detect_text')
def detect_text_page():
    
    return render_template('detect_text.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # ใช้พอร์ตที่ Render ให้ หรือพอร์ต 5000 ถ้าไม่ได้กำหนด
    app.run(host='0.0.0.0', port=port)