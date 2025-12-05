from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

# -------------------------------
# DATABASE CONFIGURATION
# -------------------------------
db_config = {
    'user': 'root',                  # replace if your Railway username is different
    'password': 'ElqhWjfUvehDAAWLnKPTwgRcRxzSTOzf',  # replace with your Railway password
    'host': 'shinkansen.proxy.rlwy.net',
    'port': 48290,
    'database': 'aani'
}

# -------------------------------
# ROUTES
# -------------------------------
@app.route('/')
def index():
    try:
        # Connect to Railway MySQL
        db = mysql.connector.connect(
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database']
        )

        cursor = db.cursor()
        cursor.execute("SHOW TABLES;")
        tables = [table[0] for table in cursor.fetchall()]

        db.close()

        return jsonify({
            'status': 'success',
            'tables': tables
        })

    except mysql.connector.Error as err:
        return jsonify({
            'status': 'error',
            'message': str(err)
        })


# -------------------------------
# RUN THE APP
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
