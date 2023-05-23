function menuToggle(event) {
    event.preventDefault();
    const navList = document.getElementById('nav-list');
    navList.classList.toggle('active');
}


function switchVisible(event) {
    let anonymousCheckbox = event.target;
    let loginFields = document.getElementById('auth-fields');

    if (anonymousCheckbox.checked) {
        loginFields.style.display = 'none';
    } else {
        loginFields.style.display = 'block';
    }
}