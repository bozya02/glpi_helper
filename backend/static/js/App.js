function menuToggle(event) {
    event.preventDefault();
    const navList = document.getElementById('nav-list');
    navList.classList.toggle('show');
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

function selectAll(checkboxAll) {
    const checkboxes = document.querySelectorAll('input[type="checkbox"][name="item_check"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = checkboxAll.checked
    })
}

function submitCheckForm(checkbox) {
    const form = checkbox.closest('form');
    const formData = new FormData(form);
    fetch(form.action, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            // Обработка успешного ответа
            console.log(data);
        })
        .catch(error => {
            // Обработка ошибки
            console.error(error);
        });
}

function submitMovement(button) {
    const form = button.closest('form');
    const formData = new FormData(form);
    fetch(form.action, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            // Обработка успешного ответа
            console.log(data);
        })
        .catch(error => {
            // Обработка ошибки
            console.error(error);
        });
}