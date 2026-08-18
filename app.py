from flask import Flask, render_template, request, redirect, session, jsonify
import os
import re
import json
from datetime import timedelta

from dotenv import load_dotenv

import requests
import tensorflow as tf
import numpy as np
from PIL import Image

from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import get_connection

load_dotenv()


# =====================================================
# FLASK APP
# =====================================================

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")


# =====================================================
# AI MODEL
# =====================================================

MODEL_PATH = os.path.join(
    app.root_path,
    "ai_model",
    "best_agriguard_model.keras"
)

LABELS_PATH = os.path.join(
    app.root_path,
    "ai_model",
    "labels.txt"
)


print("========================================")
print("Loading AgriGuard AI model...")
print("========================================")

try:

    model = tf.keras.models.load_model(MODEL_PATH)

    with open(
        LABELS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        CLASS_NAMES = [
            line.strip()
            for line in file
            if line.strip()
        ]

    print("AI model loaded successfully.")
    print("Number of classes:", len(CLASS_NAMES))
    print("Model path:", MODEL_PATH)

except Exception as e:

    print("ERROR: Could not load AI model.")
    print("Reason:", repr(e))

    model = None
    CLASS_NAMES = []


# =====================================================
# UPLOAD CONFIGURATION
# =====================================================

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# =====================================================
# SESSION
# =====================================================

# Keep user logged in for 7 days

app.permanent_session_lifetime = timedelta(
    days=7
)


# =====================================================
# LANGUAGE SYSTEM
# =====================================================

def load_language():

    lang = session.get(
        "language",
        "en"
    )

    # Only allow supported languages

    if lang not in ["en", "mm"]:
        lang = "en"

    language_path = os.path.join(
        app.root_path,
        "languages",
        f"{lang}.json"
    )

    try:

        with open(
            language_path,
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        # Your JSON files contain
        # one dictionary inside a list

        if isinstance(data, list):

            return data[0]

        return data

    except Exception as e:

        print(
            "Language loading error:",
            repr(e)
        )

        return {}


@app.context_processor
def inject_language():

    return dict(
        lang=load_language()
    )


# =====================================================
# CHANGE LANGUAGE
# =====================================================

@app.route("/language/<lang>")
def change_language(lang):

    if lang in ["en", "mm"]:

        session["language"] = lang

    return redirect(
        request.referrer or "/"
    )


@app.route("/service-worker.js")
def service_worker():
    return app.send_static_file("js/service-worker.js")
# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return render_template(
        "home.html"
    )


# =====================================================
# WEATHER
# =====================================================
WEATHER_CITIES = {

    # =====================================================
    # YANGON REGION
    # =====================================================

    "yangon": {
    "name": "Yangon",
    "my_name": "ရန်ကုန်",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 16.8409,
    "longitude": 96.1735
   },

    "bago": {
    "name": "Bago",
    "my_name": "ပဲခူး",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 17.3367,
    "longitude": 96.4797
   },

    "pyay": {
    "name": "Pyay",
    "my_name": "ပြည်",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 18.8246,
    "longitude": 95.2221
   },


    # =====================================================
    # MANDALAY REGION
    # =====================================================

    "mandalay": {
    "name": "Mandalay",
    "my_name": "မန္တလေး",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 21.9588,
    "longitude": 96.0891
   },

    "meiktila": {
    "name": "Meiktila",
    "my_name": "မိတ္ထီလာ",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 20.8770,
    "longitude": 95.8584
   },

    "mahlaing": {
    "name": "Ma Hlaing",
    "my_name": "မလှိုင်",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 20.8867,
    "longitude": 95.6167
   },

    "pakokku": {
    "name": "Pakokku",
    "my_name": "ပခုက္ကူ",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 21.3349,
    "longitude": 95.0844
   },


    # =====================================================
    # NAYPYIDAW
    # =====================================================

    "naypyidaw": {
    "name": "Naypyidaw",
    "my_name": "နေပြည်တော်",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 19.7633,
    "longitude": 96.0785
   },


    # =====================================================
    # MAGWAY REGION
    # =====================================================

    "magway": {
    "name": "Magway",
    "my_name": "မကွေး",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 20.1496,
    "longitude": 94.9325
   },



    # =====================================================
    # SAGAING REGION
    # =====================================================

    "monywa": {
    "name": "Monywa",
    "my_name": "မုံရွာ",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 22.1086,
    "longitude": 95.1358
   },

    "sagaing": {
    "name": "Sagaing",
    "my_name": "စစ်ကိုင်း",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 21.8787,
    "longitude": 95.9797
   },

    "kalay": {
    "name": "Kalay",
    "my_name": "ကလေး",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 23.1889,
    "longitude": 94.0519
   },


    # =====================================================
    # SHAN STATE
    # =====================================================

    "taunggyi": {
    "name": "Taunggyi",
    "my_name": "တောင်ကြီး",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 20.7892,
    "longitude": 97.0378
   },
    "lashio": {
    "name": "Lashio",
    "my_name": "လားရှိုး",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 22.9350,
    "longitude": 97.7498
   },


    # =====================================================
    # MON STATE
    # =====================================================

    "mawlamyine": {
    "name": "Mawlamyine",
    "my_name": "မော်လမြိုင်",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 16.4905,
    "longitude": 97.6283
   },


    # =====================================================
    # KAYIN STATE
    # =====================================================

    "hpa_an": {
    "name": "Hpa-An",
    "my_name": "ဘားအံ",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 16.8895,
    "longitude": 97.6348
   },


    # =====================================================
    # AYeyARWADY REGION
    # =====================================================

    "pathein": {
    "name": "Pathein",
    "my_name": "ပုသိမ်",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 16.7792,
    "longitude": 94.7321
   },


    # =====================================================
    # TANINTHARYI REGION
    # =====================================================

    "dawei": {
    "name": "Dawei",
    "my_name": "ထားဝယ်",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 14.0823,
    "longitude": 98.1950
   },

    "myeik": {
    "name": "Myeik",
    "my_name": "မြိတ်",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 12.4398,
    "longitude": 98.6003
   },


    # =====================================================
    # RAKHINE STATE
    # =====================================================

    "sittwe": {
    "name": "Sittwe",
    "my_name": "စစ်တွေ",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 20.1462,
    "longitude": 92.8984
   },


    # =====================================================
    # KACHIN STATE
    # =====================================================

    "myitkyina": {
    "name": "Myitkyina",
    "my_name": "မြစ်ကြီးနား",
    "country": "Myanmar",
    "my_country": "မြန်မာ",
    "latitude": 25.3833,
    "longitude": 97.4000
   }

}
# =====================================================
@app.route("/weather")
def weather():

     # Require user to be logged in
    if "user_id" not in session:
        return render_template(
            "error.html",
            title="Login Required",
            message="Please log in or create an account to use the Weather feature.",
            retry_url="/login"
        )

    selected_city = request.args.get("city", "meiktila").lower()

    # If someone enters an invalid city, use Meiktila
    if selected_city not in WEATHER_CITIES:
        selected_city = "meiktila"

    city_data = WEATHER_CITIES[selected_city]

    latitude = city_data["latitude"]
    longitude = city_data["longitude"]

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "weather_code",
            "wind_speed_10m"
        ],

        "hourly": [
            "precipitation_probability"
        ],

        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max"
        ],

        "timezone": "Asia/Yangon",
        "forecast_days": 7
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        return render_template(
            "weather.html",
            weather=data,
            city=city_data["name"],
            country=city_data["country"],
            selected_city=selected_city,
            cities=WEATHER_CITIES
        )

    except requests.RequestException as e:

        print("Weather API error:", e)

        return render_template(
            "weather.html",
            weather=None,
            city=city_data["name"],
            country=city_data["country"],
            selected_city=selected_city,
            cities=WEATHER_CITIES
        )
# =====================================================
# REGISTER
# =====================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")

        # -------------------------------------------------
        # Email validation
        # -------------------------------------------------

        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if not re.match(email_pattern, email):

            return render_template(
                "error.html",
                title="Invalid Email",
                message="Please enter a valid email address.",
                retry_url="/register"
            )


        # -------------------------------------------------
        # Phone validation
        # -------------------------------------------------

        if not phone.isdigit():

            return render_template(
                "error.html",
                title="Invalid Phone Number",
                message="Please enter a valid phone number.",
                retry_url="/register"
            )


        if not re.fullmatch(r"09\d{9}", phone):

            return render_template(
                "error.html",
                title="Invalid Phone Number",
                message="Phone number must contain exactly 11 digits and start with 09.",
                retry_url="/register"
            )


        # -------------------------------------------------
        # Password validation
        # -------------------------------------------------

        if len(password) < 6:

            return render_template(
                "error.html",
                title="Weak Password",
                message="Your password must contain at least 6 characters.",
                retry_url="/register"
            )


        # -------------------------------------------------
        # Database connection
        # -------------------------------------------------

        db = None
        cursor = None

        try:

            db = get_connection()

            # buffered=True prevents unread-result problems
            cursor = db.cursor(
                buffered=True
            )


            # -------------------------------------------------
            # Check existing EMAIL
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT user_id
                FROM users
                WHERE email=%s
                LIMIT 1
                """,
                (email,)
            )

            email_exists = cursor.fetchone()


            # -------------------------------------------------
            # Check existing PHONE
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT user_id
                FROM users
                WHERE phone=%s
                LIMIT 1
                """,
                (phone,)
            )

            phone_exists = cursor.fetchone()


            # -------------------------------------------------
            # Both already exist
            # -------------------------------------------------

            if email_exists and phone_exists:

                return render_template(
                    "error.html",
                    title="Account Already Exists",
                    message="Both the email address and phone number are already registered.",
                    retry_url="/register"
                )


            # -------------------------------------------------
            # Email already exists
            # -------------------------------------------------

            if email_exists:

                return render_template(
                    "error.html",
                    title="Email Already Registered",
                    message="This email address is already registered. Please use a different email address.",
                    retry_url="/register"
                )


            # -------------------------------------------------
            # Phone already exists
            # -------------------------------------------------

            if phone_exists:

                return render_template(
                    "error.html",
                    title="Phone Number Already Registered",
                    message="This phone number is already registered. Please use a different phone number.",
                    retry_url="/register"
                )


            # -------------------------------------------------
            # Hash password
            # -------------------------------------------------

            hashed = generate_password_hash(
                password
            )


            # -------------------------------------------------
            # Create account
            # -------------------------------------------------

            cursor.execute(
                """
                INSERT INTO users
                (
                    name,
                    email,
                    phone,
                    password
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    name,
                    email,
                    phone,
                    hashed
                )
            )

            db.commit()


            # -------------------------------------------------
            # Get newly created user
            # -------------------------------------------------

            user_id = cursor.lastrowid


            # -------------------------------------------------
            # Automatically login
            # -------------------------------------------------

            session.permanent = True

            session["user_id"] = user_id
            session["user_name"] = name


            return redirect(
                "/dashboard"
            )


        except mysql.connector.IntegrityError as e:

            # This catches MySQL UNIQUE constraint errors
            # in case two registration requests happen
            # at almost the same time.

            print(
                "Registration database error:",
                repr(e)
            )

            if db:
                db.rollback()


            return render_template(
                "error.html",
                title="Account Already Exists",
                message="The email address or phone number is already registered.",
                retry_url="/register"
            )


        except mysql.connector.Error as e:

            print(
                "MySQL registration error:",
                repr(e)
            )

            if db:
                db.rollback()


            return render_template(
                "error.html",
                title="Registration Error",
                message="Something went wrong while creating your account. Please try again.",
                retry_url="/register"
            )


        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()


    return render_template(
        "register.html"
    )
# =====================================================
# LOGIN
# =====================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        login_input = request.form.get(
            "login"
        )

        password = request.form.get(
            "password"
        )

        db = get_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email=%s OR phone=%s
            """,
            (
                login_input,
                login_input
            )
        )

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user and check_password_hash(
            user[4],
            password
        ):

            session.permanent = True

            session["user_id"] = user[0]
            session["user_name"] = user[1]

            return redirect(
                "/dashboard"
            )

        return render_template(
            "error.html",
            title="Login Failed",
            message=(
                "The email/phone or password "
                "you entered is incorrect."
            ),
            retry_url="/login"
        )

    return render_template(
        "login.html"
    )


# =====================================================
# DASHBOARD
# =====================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            "/login"
        )

    db = get_connection()
    cursor = db.cursor()

    # Total crops

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM crops
        WHERE user_id=%s
        """,
        (session["user_id"],)
    )

    total_crops = cursor.fetchone()[0]

    # Healthy crops

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM crops
        WHERE user_id=%s
        AND status='Healthy'
        """,
        (session["user_id"],)
    )

    healthy = cursor.fetchone()[0]

    # Crops needing attention

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM crops
        WHERE user_id=%s
        AND status!='Healthy'
        """,
        (session["user_id"],)
    )

    attention = cursor.fetchone()[0]

    cursor.close()
    db.close()

    return render_template(
        "dashboard.html",
        name=session.get("user_name"),
        total_crops=total_crops,
        healthy=healthy,
        attention=attention
    )


# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():

    language = session.get("language", "en")

    session.clear()
    session["language"] = language

    return redirect("/")


# =====================================================
# CROPS
# =====================================================

@app.route("/crops")
def crops():

    if "user_id" not in session:

        return redirect(
            "/login"
        )

    db = get_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT *
        FROM crops
        WHERE user_id=%s
        """,
        (session["user_id"],)
    )

    data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "crops.html",
        crops=data
    )


# =====================================================
# ADD CROP
# =====================================================

@app.route(
    "/add_crop",
    methods=["GET", "POST"]
)
def add_crop():

    if "user_id" not in session:

        return redirect(
            "/login"
        )

    if request.method == "POST":

        crop_name = request.form[
            "crop_name"
        ]

        date = request.form[
            "date"
        ]

        stage = request.form[
            "stage"
        ]

        status = request.form[
            "status"
        ]

        db = get_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO crops
            (
                user_id,
                crop_name,
                planting_date,
                growth_stage,
                status
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                session["user_id"],
                crop_name,
                date,
                stage,
                status
            )
        )

        db.commit()

        cursor.close()
        db.close()

        return redirect(
            "/crops"
        )

    return render_template(
        "add_crop.html"
    )


# =====================================================
# DELETE CROP
# =====================================================

@app.route(
    "/delete_crop/<int:crop_id>"
)
def delete_crop(crop_id):

    if "user_id" not in session:

        return redirect(
            "/login"
        )

    db = get_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        DELETE FROM crops
        WHERE crop_id=%s
        AND user_id=%s
        """,
        (
            crop_id,
            session["user_id"]
        )
    )

    db.commit()

    cursor.close()
    db.close()

    return redirect(
        "/crops"
    )


# =====================================================
# EDIT CROP
# =====================================================

@app.route(
    "/edit_crop/<int:crop_id>",
    methods=["GET", "POST"]
)
def edit_crop(crop_id):

    if "user_id" not in session:

        return redirect(
            "/login"
        )

    db = get_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT *
        FROM crops
        WHERE crop_id=%s
        AND user_id=%s
        """,
        (
            crop_id,
            session["user_id"]
        )
    )

    crop = cursor.fetchone()

    if not crop:

        cursor.close()
        db.close()

        return "Crop not found"

    if request.method == "POST":

        crop_name = request.form[
            "crop_name"
        ]

        planting_date = request.form[
            "planting_date"
        ]

        growth_stage = request.form[
            "growth_stage"
        ]

        status = request.form[
            "status"
        ]

        cursor.execute(
            """
            UPDATE crops

            SET
                crop_name=%s,
                planting_date=%s,
                growth_stage=%s,
                status=%s

            WHERE crop_id=%s
            AND user_id=%s
            """,
            (
                crop_name,
                planting_date,
                growth_stage,
                status,
                crop_id,
                session["user_id"]
            )
        )

        db.commit()

        cursor.close()
        db.close()

        return redirect(
            "/crops"
        )

    cursor.close()
    db.close()

    return render_template(
        "edit_crop.html",
        crop=crop
    )


# =====================================================
# PROFILE
# =====================================================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    if "user_id" not in session:

        return redirect(
            "/login"
        )

    db = get_connection()
    cursor = db.cursor()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]

        image = request.files.get(
            "profile_image"
        )

        # User uploaded an image

        if image and image.filename != "":

            filename = secure_filename(
                image.filename
            )

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

            cursor.execute(
                """
                UPDATE users

                SET
                    name=%s,
                    email=%s,
                    phone=%s,
                    profile_image=%s

                WHERE user_id=%s
                """,
                (
                    name,
                    email,
                    phone,
                    filename,
                    session["user_id"]
                )
            )

        else:

            cursor.execute(
                """
                UPDATE users

                SET
                    name=%s,
                    email=%s,
                    phone=%s

                WHERE user_id=%s
                """,
                (
                    name,
                    email,
                    phone,
                    session["user_id"]
                )
            )

        db.commit()

        # Update navbar username

        session["user_name"] = name

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE user_id=%s
        """,
        (session["user_id"],)
    )

    user = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template(
        "profile.html",
        user=user
    )


# =====================================================
# FORGOT PASSWORD
# =====================================================

@app.route(
    "/forgot_password",
    methods=["GET", "POST"]
)
def forgot_password():

    if request.method == "POST":

        login_input = request.form[
            "login"
        ]

        db = get_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email=%s OR phone=%s
            """,
            (
                login_input,
                login_input
            )
        )

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user:

            session[
                "reset_user_id"
            ] = user[0]

            return redirect(
                "/reset_password"
            )

        return render_template(
    "error.html",
    title="User Not Found",
    message="We could not find an account with that email address or phone number. Please check your information and try again.",
    retry_url="/forgot_password"
)

    return render_template(
        "forgot_password.html"
    )


# =====================================================
# RESET PASSWORD
# =====================================================

@app.route(
    "/reset_password",
    methods=["GET", "POST"]
)
def reset_password():

    if "reset_user_id" not in session:

        return redirect(
            "/login"
        )

    if request.method == "POST":

        password = request.form[
            "password"
        ]

        hashed = generate_password_hash(
            password
        )

        db = get_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            UPDATE users

            SET password=%s

            WHERE user_id=%s
            """,
            (
                hashed,
                session["reset_user_id"]
            )
        )

        db.commit()

        # Get user before closing connection

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE user_id=%s
            """,
            (
                session["reset_user_id"],
            )
        )

        user = cursor.fetchone()

        cursor.close()
        db.close()

        # Automatically login

        session.permanent = True

        session["user_id"] = user[0]
        session["user_name"] = user[1]

        session.pop(
            "reset_user_id",
            None
        )

        return redirect("/")

    return render_template(
        "reset_password.html"
    )

# =====================================================
# AI DISEASE DETECTION
# =====================================================

@app.route("/ai-detection", methods=["GET"])
def ai_detection():

    return render_template(
        "ai_detection.html",
        prediction=None,
        confidence=None,
        image_filename=None,
        error=None
    )

# =====================================================
# AI PREDICTION
# =====================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        # ---------------------------------------------
        # Check uploaded file
        # ---------------------------------------------

        if "image" not in request.files:

            return jsonify({
                "success": False,
                "error": "No image was uploaded."
            }), 400


        image_file = request.files["image"]


        if image_file.filename == "":

            return jsonify({
                "success": False,
                "error": "No image was selected."
            }), 400


        # ---------------------------------------------
        # Open image
        # ---------------------------------------------

        image = Image.open(
            image_file
        ).convert("RGB")


        # ---------------------------------------------
        # Resize to model input size
        # ---------------------------------------------

        image = image.resize(
            (224, 224)
        )


        # ---------------------------------------------
        # Convert image to NumPy
        # ---------------------------------------------

        image_array = np.array(
            image,
            dtype=np.float32
        )


        image_array = np.expand_dims(
            image_array,
            axis=0
        )


        # ---------------------------------------------
        # AI Prediction
        # ---------------------------------------------

        predictions = model.predict(
            image_array,
            verbose=0
        )


        probabilities = predictions[0]


        predicted_index = int(
            np.argmax(probabilities)
        )


        predicted_label = CLASS_NAMES[
            predicted_index
        ]


        predicted_confidence = float(
            probabilities[predicted_index] * 100
        )


        # ---------------------------------------------
        # Load disease information
        # ---------------------------------------------

        disease_info_path = os.path.join(
            app.root_path,
            "data",
            "disease_info.json"
        )


        disease_info = {}


        try:

            with open(
                disease_info_path,
                "r",
                encoding="utf-8"
            ) as file:

                disease_database = json.load(file)


            disease_info = disease_database.get(
                predicted_label,
                {}
            )


        except Exception as e:

            print(
                "Disease information loading error:",
                repr(e)
            )


        # ---------------------------------------------
        # Determine result type
        # ---------------------------------------------

        result_type = disease_info.get(
            "type",
            "healthy"
            if "healthy" in predicted_label.lower()
            else "disease"
        )


        # ---------------------------------------------
        # Determine healthy status
        # ---------------------------------------------

        is_healthy = (
            result_type == "healthy"
        )


        # ---------------------------------------------
        # Return prediction
        # ---------------------------------------------

        return jsonify({

            "success": True,

            "prediction": predicted_label,

            "confidence": predicted_confidence,

            "is_healthy": is_healthy,

            "disease_info": {

                "type": result_type,

                "plant":
                    disease_info.get(
                        "plant",
                        ""
                    ),

                "disease":
                    disease_info.get(
                        "disease",
                        ""
                    ),

                "icon":
                    disease_info.get(
                        "icon",
                        "🌱"
                    ),

                "treatment":
                    disease_info.get(
                        "treatment",
                        ""
                    ),

                "treatment_mm":
                    disease_info.get(
                        "treatment_mm",
                        ""
                    ),

                "care":
                    disease_info.get(
                        "care",
                        ""
                    ),

                "care_mm":
                    disease_info.get(
                        "care_mm",
                        ""
                    )

            }

        })


    except Exception as e:

        print(
            "AI prediction error:",
            repr(e)
        )


        return jsonify({

            "success": False,

            "error":
                str(e)

        }), 500

# =====================================================
# RUN APP
# =====================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )