document.addEventListener('DOMContentLoaded', function() {

    const flashMsg = document.querySelectorAll('.error-flash');

    if(flashMsg.length > 0){

        setTimeout(function() {
            flashMsg.forEach(function(msg) {
                msg.style.display = 'none';
            });
        }, 3000); 
    }      
});