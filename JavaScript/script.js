function signup() {
    const username = document.getElementById("signupUsername").value;
    const password = document.getElementById("signupPassword").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    const storedUsername = localStorage.getItem("username");

    if (!username || !password || !confirmPassword) {
        alert("Please fill all fields");
        return;
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match");
        return;
    }

    if (storedUsername === username) {
        alert("Account already exists! Please login.");
        window.location.href = "index.html";
        return;
    }

    localStorage.setItem("username", username);
    localStorage.setItem("password", password);
    localStorage.setItem("loggedIn", "true");

    alert("Signup Successful!");
    window.location.href = "dashboard.html";
}

function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const storedUsername = localStorage.getItem("username");
    const storedPassword = localStorage.getItem("password");

    if (!username || !password) {
        alert("Please enter username and password");
        return;
    }

    if (username === storedUsername && password === storedPassword) {
        localStorage.setItem("loggedIn", "true");
        alert("Login Successful!");
        window.location.href = "dashboard.html";
    } else {
        alert("Invalid Credentials");
    }
}

function logout() {
    localStorage.removeItem("loggedIn");
    alert("Logged out successfully");
    window.location.href = "index.html";
}

function goTo(page) {
    window.location.href = page;
}

function toggleDarkMode() {
    document.body.classList.toggle("dark-mode");
}

function togglePassword() {
    const password = document.getElementById("password");

    if (password.type === "password") {
        password.type = "text";
    } else {
        password.type = "password";
    }
}

function resetPassword() {
    const username = document.getElementById("resetUsername").value;
    const newPassword = document.getElementById("newPassword").value;
    const confirmNewPassword = document.getElementById("confirmNewPassword").value;

    const storedUsername = localStorage.getItem("username");

    if (!username || !newPassword || !confirmNewPassword) {
        alert("Please fill all fields");
        return;
    }

    if (username !== storedUsername) {
        alert("Username not found");
        return;
    }

    if (newPassword !== confirmNewPassword) {
        alert("Passwords do not match");
        return;
    }

    localStorage.setItem("password", newPassword);

    alert("Password updated successfully!");
    window.location.href = "index.html";
}

function showNotifications() {
    alert("No new notifications");
}

function uploadDataset() {
    alert("Dataset uploaded successfully!");
}

function savePatient() {
    alert("Patient saved successfully!");
}

function generateReport() {
    alert("Report generated successfully!");
}