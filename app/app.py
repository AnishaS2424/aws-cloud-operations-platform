from flask import Flask, jsonify, render_template, request
import boto3
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename

from config import Config
from db import check_database, get_connection, get_order_count

app = Flask(__name__)


def check_s3():
    if not Config.S3_BUCKET:
        return False, "S3 bucket is not configured"

    try:
        s3 = boto3.client("s3", region_name=Config.AWS_REGION)
        s3.head_bucket(Bucket=Config.S3_BUCKET)
        return True, "S3 bucket accessible"

    except ClientError as exc:
        return False, str(exc)

    except Exception as exc:
        return False, str(exc)


@app.route("/")
def dashboard():
    db_ok, db_message = check_database()
    s3_ok, s3_message = check_s3()

    return render_template(
        "index.html",
        app_name=Config.APP_NAME,
        db_ok=db_ok,
        db_message=db_message,
        s3_ok=s3_ok,
        s3_message=s3_message,
        order_count=get_order_count(),
    )


@app.route("/health")
def health():
    return jsonify({
        "application": "healthy",
        "service": Config.APP_NAME
    })


@app.route("/health/db")
def database_health():
    healthy, message = check_database()

    return jsonify({
        "database": "healthy" if healthy else "unhealthy",
        "message": message
    }), 200 if healthy else 503


@app.route("/health/s3")
def s3_health():
    healthy, message = check_s3()

    return jsonify({
        "s3": "healthy" if healthy else "unhealthy",
        "message": message
    }), 200 if healthy else 503


@app.route("/orders")
def orders():
    connection = None

    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, customer_name, amount, status
                FROM orders
                ORDER BY id DESC
                LIMIT 20
            """)

            rows = cursor.fetchall()

        return jsonify([
            {
                "id": row[0],
                "customer_name": row[1],
                "amount": float(row[2]),
                "status": row[3]
            }
            for row in rows
        ])

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    finally:
        if connection:
            connection.close()


@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body required"}), 400

    customer_name = data.get("customer_name")
    amount = data.get("amount")
    status = data.get("status", "PENDING")

    if not customer_name or amount is None:
        return jsonify({
            "error": "customer_name and amount are required"
        }), 400

    connection = None

    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO orders (customer_name, amount, status)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (customer_name, amount, status))

            order_id = cursor.fetchone()[0]

        connection.commit()

        return jsonify({
            "message": "Order created",
            "order_id": order_id
        }), 201

    except Exception as exc:
        if connection:
            connection.rollback()

        return jsonify({"error": str(exc)}), 500

    finally:
        if connection:
            connection.close()


@app.route("/upload", methods=["POST"])
def upload_file():
    if not Config.S3_BUCKET:
        return jsonify({"error": "S3 bucket is not configured"}), 503

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({"error": "Filename is empty"}), 400

    filename = secure_filename(file.filename)

    try:
        s3 = boto3.client("s3", region_name=Config.AWS_REGION)

        s3.upload_fileobj(
            file,
            Config.S3_BUCKET,
            filename
        )

        return jsonify({
            "message": "File uploaded successfully",
            "filename": filename
        }), 201

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)