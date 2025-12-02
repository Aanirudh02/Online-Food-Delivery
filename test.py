from flask import Flask, render_template, request, redirect, url_for, flash,session,jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import webbrowser  # Added import
import threading   # To avoid blocking the Flask server
import random
import smtplib
from email.message import EmailMessage
import base64
import json 
import random
from geopy.geocoders import Nominatim
import os
from mysql.connector import Error
import time 


from nbformat import from_dict


app = Flask(__name__)
app.secret_key = 'your_secret_key'


# Database connection configuration
db_config = {
    'user': 'root',
    'password': 'aanirudh_02',
    'host': 'localhost',
    'database': 'aani'
}

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn


def generateCoupon():
    # Generate a random 8-digit coupon code
    return ''.join(random.choices('0123456789', k=8))


@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/chkk')
def chkk():
    return render_template('chkk.html')


@app.route('/add_restaurant', methods=['POST'])
def add_restaurant():
    name = request.form['name']
    place = request.form['place']
    district = request.form['district']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    rating = int(request.form['rating'])

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO restaurants (name, place, district, latitude, longitude, rating)
                      VALUES (%s, %s, %s, %s, %s, %s)''',
                   (name, place, district, latitude, longitude, rating))
    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('view_restaurants'))


@app.route('/view_restaurants')
def view_restaurants():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM restaurants")
    restaurants = cursor.fetchall()
    cursor.close()
    connection.close()

    n = 5  # Set this to the actual number of images you have

    return render_template("view_restaurants.html", restaurants=restaurants, n=n)




@app.route('/delivery_signin')
def delivery_signin():
    return render_template('delivery_signin.html')  # Ensure this template is named correctly

@app.route('/registe', methods=['POST'])
def register_driver():
    # Retrieve form data
    full_name = request.form['name']
    phone_number = request.form['phone']
    address = request.form['address']
    
    # Retrieve and read the file data
    user_photo = request.files['userPhoto'].read()
    aadhaar = request.files['aadhaar'].read()
    driving_license = request.files['license'].read()
    voter_id = request.files['voterId'].read()

    try:
        # Connect to the database and insert data
        connection = get_db_connection()
        cursor = connection.cursor()
        query = """
        INSERT INTO drivers (full_name, phone_number, address, user_photo, aadhaar, driving_license, voter_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (full_name, phone_number, address, user_photo, aadhaar, driving_license, voter_id))
        connection.commit()
        print("Driver data successfully stored in database.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    # Redirect to the form page or a success page
    return redirect(url_for('ok'))



def get_drivers():
    """Retrieve driver data from the database."""
    try:
        connection = get_db_connection()
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM drivers")
            drivers = cursor.fetchall()
            return drivers
    except Error as e:
        print(f"Error retrieving data: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Register the custom b64encode filter
@app.template_filter('b64encode')
def b64encode_filter(data):
    """Encode binary data to base64 for embedding in HTML."""
    if data:
        return base64.b64encode(data).decode('utf-8')
    return ''

@app.route('/delivery_dashboard')
def delivery_dashboard():
    drivers = get_drivers()
    return render_template('delivery_dashboard.html', drivers=drivers)


@app.route('/delete_driver/<int:driver_id>', methods=['POST'])
def delete_driver(driver_id):
    """Delete a driver by ID."""
    try:
        connection = get_db_connection()
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("DELETE FROM drivers WHERE id = %s", (driver_id,))
            connection.commit()
            print(f"Driver with ID {driver_id} deleted successfully.")
    except Error as e:
        print(f"Error deleting driver: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    return redirect(url_for('delivery_dashboard'))



@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot.html')  # Render the forgot password page

@app.route('/adan')
def adan():
    return render_template('admin.html')


@app.route('/new')
def new():
    return render_template('new.html')

@app.route('/driver')
def driver():
    return render_template('driver.html')


@app.route('/ad')
def ad():
    return render_template('ad.html')

@app.route('/facebook')
def facebook():
    return render_template('facebook.html')

from flask import request, redirect, url_for, flash
from werkzeug.security import check_password_hash
import re


@app.route('/googl', methods=['GET', 'POST'])
def googl():
    if request.method == 'GET':
        return render_template('googl.html')  # Render googl.html template

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Simple regex for email validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email format')
            return redirect(url_for('index'))

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                flash('Login successful!')
                return redirect(url_for('cook'))
            else:
                flash('Invalid User ID or Password')
                return redirect(url_for('index'))
        except Exception as e:
            flash('Error: {}'.format(e))
            return redirect(url_for('index'))





@app.route('/display_food', methods=['GET', 'POST'])
def display_food():
    # Establish a connection to the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Get data from the POST request
        posted_data = request.form  # or request.json for JSON data
        # You can process posted_data here if needed

        # Optionally, you can pass the posted data to the template
        return render_template('display.html', food_items=[], posted_data=posted_data)

    # If the method is GET, retrieve food items from the database
    cursor.execute("SELECT name, price, discount, discounted_price, rating, image FROM food_items")
    food_items = cursor.fetchall()

    # Convert image to base64 format for HTML display
    for item in food_items:
        item['image'] = base64.b64encode(item['image']).decode('utf-8')

    cursor.close()
    conn.close()

    # Render the template with the food items
    return render_template('display.html', food_items=food_items)


@app.route('/goin', methods=['POST'])
def goin():
    user_input = request.form['email']  # This will capture the input from the form
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Sanitize user input: remove non-digit characters for phone number validation
        sanitized_input = ''.join(filter(str.isdigit, user_input))
        print(f"Sanitized User Input: {sanitized_input}")  # Debugging: Check user input

        # Check the type of input
        if sanitized_input.isdigit() and len(sanitized_input) == 10:  # Assuming phone number has 10 digits
            query = "SELECT * FROM user WHERE contact = %s"
            table = "phone number"
            print("Querying by phone number")  # Debugging: Log query type
        elif '@' in user_input:
            query = "SELECT * FROM user WHERE email = %s"
            table = "email ID"
            print("Querying by email")  # Debugging: Log query type
        else:
            query = "SELECT * FROM details WHERE username = %s"
            table = "username"
            print("Querying by username")  # Debugging: Log query type

        # Execute the query
        cursor.execute(query, (user_input,))
        user = cursor.fetchone()
        print(f"User found: {user}")  # Debugging: Check if a user is found

        if user:
            # User found, redirect or perform the next steps
            flash('Login successful!', 'success')
            return redirect(url_for('cook'))  # Redirect to a success page or dashboard
        else:
            flash(f'Login failed. Please check your {table}.', 'danger')
            return redirect(url_for('login_page'))  # Redirect to the login page

    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('login_page'))  # Redirect to the login page on error

    finally:
        cursor.close()
        connection.close()  # Ensure the connection is closed



@app.route('/twitter')
def twitter():
    return render_template('twitter.html')






@app.route('/')
def index():
    # Render the loading page first
    return render_template('loading.html')

@app.route('/login_page')
def login_page():
    return render_template('login.html')




@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        # Check if the necessary keys are present in the form data
        if 'u_id' not in request.form or 'pasw' not in request.form or 'confm' not in request.form:
            flash("Missing form data.")
            return redirect(url_for('forgot'))

        u_id = request.form['u_id']
        pasw = request.form['pasw']
        confm = request.form['confm']

        if pasw != confm:
            flash("Passwords do not match!")
            return redirect(url_for('forgot'))  # Redirect back to forgot password page

        # Check if the user exists
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM details WHERE username = %s", (u_id,))
        user = cursor.fetchone()

        if user:
            # User exists, proceed to update password
            hashed_password = generate_password_hash(pasw)

            cursor.execute("UPDATE details SET password = %s WHERE username = %s", (hashed_password, u_id))
            conn.commit()
            flash("Password has been reset successfully. You can now log in.")
            return redirect(url_for('login_page'))  # Redirect to login page after successful reset
        else:
            flash("User ID does not exist.")
            return redirect(url_for('forgot'))  # Redirect back if user ID is not found

        # Clean up
        cursor.close()
        conn.close()

    return render_template('reset.html')  # Render reset password page if not POST



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['name']
        last_name = request.form['lname']
        contact = request.form['contact']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Insert into the user table
            cursor.execute(
                "INSERT INTO user (first_name, last_name, contact, email, password, address) VALUES (%s, %s, %s, %s, %s, %s)",
                (first_name, last_name, contact, email, hashed_password, address)
            )
            conn.commit()
            flash('Registration successful! You can now log in.')
            return redirect(url_for('index'))
        except mysql.connector.IntegrityError:
            flash('Email already exists. Please choose a different one.')
        finally:
            cursor.close()
            conn.close()
 
    else: 
        return render_template('signup.html')  # Return the signup page if not POST



# Function to convert image from binary to base64
def convert_image_to_base64(image_blob):
    return base64.b64encode(image_blob).decode('utf-8')


@app.route('/bill')
def bill():
    # Get cart data from the query string
    cart_data = request.args.get('cart')
    
    # Parse the JSON data if it's present
    if cart_data:
        cart_items = json.loads(cart_data)  # Convert JSON string back to a Python object
    else:
        cart_items = []

    # Calculate total amount
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)

    # Generate a coupon code
    coupon_code = generateCoupon()

    return render_template('bill.html', cart_items=cart_items, total_amount=total_amount, coupon_code=coupon_code)




@app.route('/indix')
def indix():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM food_items")
    food_items = cursor.fetchall()

    # Convert image BLOB to base64
    for item in food_items:
        item['image'] = base64.b64encode(item['image']).decode('utf-8') if item['image'] else None

    conn.close()
    return render_template('indix.html', food_items=food_items)

# Route to handle deleting food items
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM food_items WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    flash('Food item deleted successfully!', 'success')
    return redirect(url_for('indix'))

@app.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    name = request.form['name']
    price = float(request.form['price'])  # Ensure price is a float
    discount = float(request.form['discount'])  # Ensure discount is a float
    rating = request.form['rating']
    image_url = request.form['image_url']
    
    # Check if a new image is uploaded
    image = request.files['image']
    
    # Fetch existing image from the database
    cursor.execute("SELECT image FROM food_items WHERE id = %s", (id,))
    existing_image_row = cursor.fetchone()
    existing_image = existing_image_row['image'] if existing_image_row else None
    
    if image and image.filename:  # If a new image is provided
        image_data = image.read()
    else:  # If no new image is provided, retain the existing image
        image_data = existing_image

    # Calculate discounted price in the SQL query itself
    cursor.execute("""
        UPDATE food_items
        SET name = %s, price = %s, discount = %s,
            rating = %s, image_url = %s, image = %s,
            discounted_price = price - (price * discount / 100)
        WHERE id = %s
    """, (name, price, discount, rating, image_url, image_data, id))
    
    conn.commit()
    conn.close()
    flash('Food item updated successfully!', 'success')
    return redirect(url_for('indix'))







@app.route('/register', methods=['POST'])
def register():
    uid = request.form['uid']
    passw = request.form['passw']
    confirm_pass = request.form['confirm_pass']

    if passw != confirm_pass:
        flash('Passwords do not match!')
        return redirect(url_for('index'))  # Redirect to index if passwords don't match

    hashed_password = generate_password_hash(passw)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO details (username, password) VALUES (%s, %s)", (uid, hashed_password))
        conn.commit()
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login_page'))  # Redirect to login page after successful registration
    except mysql.connector.IntegrityError:
        flash('User  ID already exists. Please choose a different one.')
        return redirect(url_for('index'))  # Redirect back if user ID already exists
    finally:
        cursor.close()
        conn.close()

@app.route('/tryotp')
def tryotp():
    return render_template('tryotp.html')

@app.route('/ok')
def ok():
    return render_template('ok.html')




@app.route('/choose_driver', methods=['POST'])
def choose_driver():
    driver_name = request.form.get('driver_name')
    driver_phone = request.form.get('driver_phone')
    return render_template('another.html', driver_name=driver_name, driver_phone=driver_phone)

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/otp', methods=['POST'])
def otp():
    email = request.form.get('email')
    
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to check if the email exists in the database
    query = "SELECT email FROM user WHERE email = %s"
    cursor.execute(query, (email,))
    result = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    if result:
        # Email exists, proceed with OTP sending
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])  # Generate a 6-digit OTP
        session['otp'] = otp  # Store OTP in session

        # Sending OTP via email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        from_mail = 'ungaarusuvai1709@gmail.com'
        server.login(from_mail, 'oeeb bwzd soeu afxz')
        msg = EmailMessage()
        msg['Subject'] = "OTP Verification"
        msg['From'] = from_mail
        msg['To'] = email
        msg.set_content("Your OTP is: " + otp)

        server.send_message(msg)
        server.quit()

        flash('OTP has been sent to your email!', 'success')
        return redirect(url_for('tryotp', otp_sent=True))  # Redirect back to tryotp
    else:
        flash('Email not found. Please sign up first.', 'error')
        return redirect('/signup')

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    entered_otp = request.form.get('otpInput')
    stored_otp = session.get('otp')

    if entered_otp == stored_otp:
        return redirect(url_for('forgot_password'))  # Redirect to forgot.html on successful OTP verification
    else:
        flash('Invalid OTP. Please try again.', 'error')
        return redirect(url_for('tryotp'))  # Redirect back to tryotp
# Add this route to run browse.py functionality directly

@app.route('/faechok', methods=['POST'])
def faechok():
    contact_email = request.form['contact_email']
    password = request.form['password']

    # Get a database connection
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if input is a phone number or email
    if '@' in contact_email:  # Assuming email contains '@'
        query = "SELECT * FROM user WHERE email = %s"
        cursor.execute(query, (contact_email,))
    else:
        query = "SELECT * FROM user WHERE contact = %s"
        cursor.execute(query, (contact_email,))

    user = cursor.fetchone()

    if user and check_password_hash(user['password'], password):  # If user exists and password matches
        return redirect(url_for('cook'))
    else:
        flash('Invalid email/phone number or password. Please try again.')
        return redirect(url_for('login_page'))


@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['user_id']
    login_password = request.form['password']  # Store the entered password

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Query to check if user exists and password matches
    cursor.execute("SELECT * FROM details WHERE username = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()  # Close the cursor
    conn.close()    # Close the connection

    if user and check_password_hash(user['password'], login_password):
        flash('Login successful!')
        session['user_id'] = user_id  # Store user_id in session
        return redirect(url_for('cook'))  # Redirect to the '/cook' route
    else:
        flash('Invalid User ID or Password')
        return redirect(url_for('login_page'))  # Redirect to the login page

@app.route('/cook')
def cook():
    user_id = session.get('user_id')  # Retrieve user_id from the session
    return render_template('cook.html', user_id=user_id)  # Pass user_id to the template



@app.route('/action_taker', methods=['POST'])
def action_taker():
    food_name = request.form['food']
    price = float(request.form['price'])
    discount = int(request.form['discount'])
    rating = float(request.form['rating'])
    
    discounted_price = price - (price * (discount / 100))
    
    # Handle file upload
    file = request.files['img']
    image_data = file.read()
    image_url = file.filename

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Inserting a new item
        sql = """INSERT INTO food_items (name, price, discount, discounted_price, rating, image_url, image) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (food_name, price, discount, discounted_price, rating, image_url, image_data))
        conn.commit()
        return jsonify({'message': 'Food item added successfully'}), 200
    finally:
        cursor.close()
        conn.close()


def get_drivers_summary():
    """Retrieve only full name, phone number, and user photo for each driver."""
    try:
        connection = get_db_connection()
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id, full_name, phone_number, user_photo FROM drivers")
            drivers = cursor.fetchall()
            return drivers
    except Error as e:
        print(f"Error retrieving data: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/shoo')
def shoo():
    drivers = get_drivers_summary()
    return render_template('shoo.html', drivers=drivers)



@app.route('/for_otp', methods=['POST'])
def send_OTP():
    data = request.json
    user_email = data.get('email')

    # Generate a 6-digit OTP
    otp = "".join(str(random.randint(0, 9)) for _ in range(6))
    session['otp'] = otp  # Store OTP in the session

    # Set up the email server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    # Login credentials
    from_mail = 'ungaarusuvai1709@gmail.com'
    server.login(from_mail, 'oeeb bwzd soeu afxz')

    # Create the email message
    msg = EmailMessage()
    msg['Subject'] = "OTP Verification"
    msg['From'] = from_mail
    msg['To'] = f"{user_email}, aanirudhch@gmail.com"
    msg.set_content(f"Your OTP is: {otp}")

    try:
        server.send_message(msg)
        print(f"Email sent successfully to: {user_email} and aanirudhch@gmail.com.")
        return jsonify({'status': 'success', 'message': 'OTP sent successfully.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        server.quit()

@app.route('/gravity')
def gravity():
    return render_template('gravity.html')

@app.route('/veri_otp', methods=['POST'])
def ver_Otp():
    data = request.json
    user_otp = data.get('otp')
    stored_otp = session.get('otp')  # Get OTP from the session

    if stored_otp and user_otp == stored_otp:
        return jsonify({'status': 'success', 'message': 'OTP verified successfully!'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid OTP.'})

@app.errorhandler(404)
def page_not_found(error):
    # Render a custom 404 page with a meaningful message
    return render_template('404error.html'), 404

@app.route('/p5')
def p5():
   return render_template('p5.js')

@app.route('/sketch')
def sketch():
   return render_template('sketch.js')

@app.route('/box')
def box():
   return render_template('box.js')


@app.route('/matter')
def matter():
   return render_template('matter.js')



# Route to get coordinates
@app.route('/get_coordinates', methods=['GET'])
def get_coordinates():
    city = request.args.get('city')
    district = request.args.get('district')
    
    geolocator = Nominatim(user_agent="restaurant_locator", timeout=10)
    location_name = f"{city}, {district}"

    try:
        location = geolocator.geocode(location_name)
        if location:
            coordinates = {"latitude": location.latitude, "longitude": location.longitude}
            return jsonify(coordinates)
        else:
            return jsonify({'error': 'Location not found. Please check your input.'})
    except Exception as e:
        return jsonify({'error': f'An error occurred: {e}'})

# Route for image upload
@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        image = request.files['image']
        hotel_name = request.form['hotel_name']
        district = request.form['district']
        city = request.form['city']
        rating = int(request.form['rating'])
        timing = request.form['timing']
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        if image:
            image_url = f"image_{int(time.time())}.jpg"
            image_data = base64.b64encode(image.read())

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO images (image_url, image_data, hotel_name, district, city, rating, timing, latitude, longitude) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (image_url, image_data, hotel_name, district, city, rating, timing, latitude, longitude)
            )
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('view_images'))

    return render_template('upload.html')

@app.route('/images')
def view_images():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, image_data, hotel_name, district, city, rating, timing, latitude, longitude FROM images")
    images = cursor.fetchall()
    cursor.close()
    connection.close()

    image_list = []
    for image in images:
        img_id, img_data, hotel_name, district, city, rating, timing, latitude, longitude = image
        # Decode the image data from base64
        img_base64 = base64.b64encode(base64.b64decode(img_data)).decode('utf-8')
        img_src = f"data:image/jpeg;base64,{img_base64}"
        
        image_list.append({
            'id': img_id,
            'img_src': img_src,
            'hotel_name': hotel_name,
            'district': district,
            'city': city,
            'rating': rating,
            'timing': timing,
            'latitude': latitude,
            'longitude': longitude
        })

    return render_template('view_images.html', images=image_list)

@app.route('/edit_image/<int:image_id>', methods=['POST'])
def edit_image(image_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    hotel_name = request.form['hotel_name']
    district = request.form['district']
    city = request.form['city']
    rating = request.form['rating']
    timing = request.form['timing']
    latitude = request.form['latitude']
    longitude = request.form['longitude']

    # Update the image record in the database
    cursor.execute("""
        UPDATE images
        SET hotel_name = %s, district = %s, city = %s, rating = %s,
            timing = %s, latitude = %s, longitude = %s
        WHERE id = %s
    """, (hotel_name, district, city, rating, timing, latitude, longitude, image_id))

    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('view_images'))

@app.route('/remove_image/<int:image_id>')
def remove_image(image_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Remove the image record from the database
    cursor.execute("DELETE FROM images WHERE id = %s", (image_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('view_images'))


# Function to open the browser
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == '__main__':
    # Use threading to prevent blocking the Flask app
    threading.Timer(1, open_browser).start()
    app.run()





