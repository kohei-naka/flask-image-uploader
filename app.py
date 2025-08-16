from flask import Flask, render_template, request, redirect, url_for
import boto3
from datetime import datetime
import urllib.parse  # ← URLエンコード/デコード
from werkzeug.utils import secure_filename

app = Flask(__name__)

# AWSリソース
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ImageMeta')

s3 = boto3.client('s3')
BUCKET_NAME = 'test-upload-lambda-kohei'  # ← 自分のS3バケット名に置き換える
REGION_NAME = 'ap-northeast-1'    # 東京リージョン

def generate_presigned_url(file_name, expires_in=3600):
    return s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': file_name},
        ExpiresIn=expires_in
    )

@app.route("/images")
def show_images():
    try:
        response = table.scan()
        items = response.get('Items', [])

        image_data = []
        for item in items:
            file_name = item['file_name']
            url = generate_presigned_url(file_name)
            image_data.append({
                'file_name': file_name,
                'uploaded_at': item.get('uploaded_at', 'N/A'),
                'url': url
            })

        return render_template("images.html", images=image_data)

    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/upload", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":
        file = request.files["image"]
        if file:
            file_name = secure_filename(file.filename)
            file_data = file.read()

            # S3にアップロード
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=file_name,
                Body=file_data,
                ContentType=file.content_type
            )

            # DynamoDBにメタデータ保存
            timestamp = datetime.utcnow().isoformat()
            table.put_item(Item={
                'file_name': file_name,
                'uploaded_at': timestamp
            })

            return redirect(url_for('show_images'))

    return render_template("upload.html")

@app.route("/delete/<path:file_name>", methods=["POST"])
def delete_image(file_name):
    # URLデコード（%20 → スペースなど）
    decoded_name = urllib.parse.unquote(file_name)

    # S3から削除
    s3.delete_object(Bucket=BUCKET_NAME, Key=decoded_name)

    # DynamoDBから削除
    table.delete_item(Key={'file_name': decoded_name})

    return redirect(url_for('show_images'))

if __name__ == "__main__":
    app.run(debug=True)
