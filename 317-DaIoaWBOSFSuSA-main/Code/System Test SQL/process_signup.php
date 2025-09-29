<?php
// Database connection
$host = '192.185.48.158';
$username = 'bisublar_bisux';
$password = 'bisublar_bisux';
$database = 'bisublar_bisux';
$port = 3306;

$conn = new mysqli($host, $username, $password, $database, $port);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Form data
$username = $_POST['username'];
$password = $_POST['password'];

// Hash the password using MD5
$hashed_password = md5($password);

// Insert new admin user into database
$sql = "INSERT INTO admin (username, password) VALUES ('$username', '$hashed_password')";

if ($conn->query($sql) === TRUE) {
    echo "New admin user created successfully";
} else {
    echo "Error: " . $sql . "<br>" . $conn->error;
}

$conn->close();
?>
