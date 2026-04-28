document.addEventListener('DOMContentLoaded', function() {
    
    // 1. The Button Redirect Logic
    const moveToAdminLogin = document.getElementById('moveToAdminLogin');
    // We add an 'if' check just to make sure the button actually exists on the page
    if (moveToAdminLogin) {
        moveToAdminLogin.addEventListener('click', function() {
            window.location.href = '/admin-login'; 
        });
    }

    // 2. The Error Vanishing Spell
    const flashMsg = document.querySelectorAll('.error-flash');
    if(flashMsg.length > 0){
        setTimeout(function() {
            flashMsg.forEach(function(msg) {
                msg.style.display = 'none';
            });
        }, 3000); 
    }      
});