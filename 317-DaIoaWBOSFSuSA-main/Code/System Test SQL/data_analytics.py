from flask import Blueprint, render_template
import mysql.connector

feedback_data_bp = Blueprint('feedback_data', __name__)

# Function to calculate the percentage of negative and positive feedback
def calculate_feedback_percentages(feedback_data):
    total_feedback = len(feedback_data)
    negative_feedback = sum(1 for feedback in feedback_data if feedback['rating'] <= 3)  # Assuming ratings <= 3 are negative
    positive_feedback = total_feedback - negative_feedback
    negative_percentage = (negative_feedback / total_feedback) * 100 if total_feedback > 0 else 0
    positive_percentage = (positive_feedback / total_feedback) * 100 if total_feedback > 0 else 0
    return negative_percentage, positive_percentage

# Route to display the feedback data and analytics
@feedback_data_bp.route('/feedback_data')
def display_feedback_data():
    # Connect to MySQL database
    connection = mysql.connector.connect(
        host="192.185.48.158",
        user="bisublar_bisux",
        password="bisublar_bisux",
        database="bisublar_bisux",
        port="3306",
    )
    cursor = connection.cursor(dictionary=True)

    # Fetch feedback data from the database
    cursor.execute("SELECT * FROM feedback")
    feedback_data = cursor.fetchall()

    # Calculate feedback percentages
    negative_percentage, positive_percentage = calculate_feedback_percentages(feedback_data)

    # Close database connection
    cursor.close()
    connection.close()

    # Render the template with feedback data and analytics
    return render_template('server.html', feedback_data=feedback_data, negative_percentage=negative_percentage, positive_percentage=positive_percentage)
