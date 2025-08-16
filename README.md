# Flask Image Uploader

画像をS3にアップロードし、DynamoDBにメタデータを保存。
一覧表示や削除も可能なサーバーレス構成のFlaskアプリです。

## 使用技術
- Flask
- AWS S3
- AWS DynamoDB
- boto3

## 機能
- 画像アップロード
- 一覧表示（署名付きURL）
- 削除（S3 + DynamoDB）

## 起動方法
```bash
pip install -r requirements.txt
python app.py
