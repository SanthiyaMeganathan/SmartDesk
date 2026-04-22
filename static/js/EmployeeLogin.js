const loginForm = document.querySelector('.login-container form');
loginForm.addEventListener('submit', function(event) {
    event.preventDefault(); 
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (username === 'employee' && password === 'password') {
        alert('Login successful!');
      
    } else {
        alert('Invalid username or password. Please try again.');
    }
});


const moveToAdminLogin = document.getElementById('moveToAdminLogin');
moveToAdminLogin.addEventListener('click', function() {
    window.location.href = 'AdminLogin.html'; // Redirect to Admin Login page
});
