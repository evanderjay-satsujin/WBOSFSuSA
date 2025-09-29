from flask import Blueprint, render_template, request, redirect, url_for
import mysql.connector
import hashlib

# Create the blueprint object
admin_login = Blueprint('admin_login', __name__)

# Database connection configuration
db_config = {
    'host': '192.185.48.158',
    'user': 'bisublar_bisux',
    'password': 'bisublar_bisux',
    'database': 'bisublar_bisux',
    'port': '3306'
}

# Route for admin login page
@admin_login.route('/admin_login', methods=['GET', 'POST'])
def admin_login_route():
    if request.method == 'POST':
        # Fetch username and password from form
        username = request.form['username']
        password = request.form['password']

        # Connect to the database
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)

            # Fetch the hashed password for the given username
            query = "SELECT password FROM admin WHERE username = %s"
            cursor.execute(query, (username,))
            admin = cursor.fetchone()

            # Consume all rows in the result set
            for _ in cursor:
                pass

            if admin:
                # Check if the entered password matches the hashed password
                if hashlib.md5(password.encode()).hexdigest() == admin['password']:
                    # Password is correct, redirect to server.html
                    return redirect(url_for('render_server_page'))
                else:
                    # Password is incorrect
                    return "Invalid username or password"
            else:
                # Username not found
                return "Invalid username or password"

        except mysql.connector.Error as err:
            return f"Error: {err}"

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    return render_template('admin_login.html')