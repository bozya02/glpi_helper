function menuToggle(event) {
    event.preventDefault();
    const navList = document.getElementById('nav-list');
    navList.classList.toggle('active');
}

function postFile(event, preview, form) {
    event.preventDefault();
    $.ajax({
        url:     '{% url "scanner" %}',
        type:     "POST",
        headers: { 'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest' },
        dataType: "multipart/form-data",
        data: form.serialize(),
        onsuccess: function(response) {
        	result = $.parseJSON(response);
            alert('Данные отправлены!');
        	preview.text('Name: ' + response.name);
    	},
    	onerror: function(response) {
            alert('Error occurred!');
            preview.text('Ошибка. Данные не отправлены.');
    	}
 	});

    return false;
}


  /*$(document).ready(function () {
    $('#qr-form').change(function () {
      var formData = new FormData();
      var fileInput = $('#file-input')[0];
      formData.append('file', fileInput.files[0]);
      console.log(formData)
      $.ajax({
        url: '{% url "scanner" %}',
        type: 'POST',
        data: formData,
        headers: { 'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest' },
        contentType: false,
        processData: false,
        success: function (response) {
          $('#preview').text('Name: ' + response.name);
        },
        error: function (jqXHR, textStatus, errorThrown) {
          alert('Error occurred!\n');
          console.log('AJAX Error: ' + textStatus + ' ' + errorThrown)
        }
      });
    });
  });*/