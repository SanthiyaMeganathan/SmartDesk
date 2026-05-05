document.addEventListener('DOMContentLoaded', function() {

    const moveToAdminLogin = document.getElementById('moveToAdminLogin');

    if (moveToAdminLogin) {
        moveToAdminLogin.addEventListener('click', function() {
            window.location.href = '/admin-login'; 
        });
    }


    const flashMsg = document.querySelectorAll('.error-flash');
    if(flashMsg.length > 0){
        setTimeout(function() {
            flashMsg.forEach(function(msg) {
                msg.style.display = 'none';
            });
        }, 3000); 
    }      
});