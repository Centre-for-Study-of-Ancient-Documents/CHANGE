
hotkeys('shift+l', function (event, handler) {
    switch (handler.key) {
        case "shift+l":
            if(localStorage.getItem('userInfo')){
                localStorage.removeItem('userInfo')
                alert('You are successfully logout!')
                location.reload();
            }
            const myModal = new bootstrap.Modal(document.getElementById('editModal'), [])
            myModal.show();
            break;
    }
});
//////////////////////////
/// Check if is user Login
if(localStorage.getItem('userInfo')){
    $('#btnEdit').removeClass('d-none')
}

///////////////////////////////////////////////////////////////////////////////////////
function login(div) {
    if ($('#txtUserName').val() !== '' && $('#txtPassword').val() !== '') {
        $('#divLoadingEdit').removeClass('d-none')
        var formData = {
            username: $('#txtUserName').val(),
            password: $('#txtPassword').val()
        };

        $.ajax({
            type: 'POST',
            url: '/login',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            dataType: 'json',
            success: function (response) {
                $('#divLoadingEdit').addClass('d-none')

                if (response['status'] === 'success') {
                    localStorage.setItem('userInfo', JSON.stringify({ username: formData.username }))
                    location.reload();
                } else {
                    alert(response['msg'])
                }
            },
            error: function (error) {
                console.log('Error: ' + JSON.stringify(error));
                $('#divLoadingEdit').addClass('d-none')
            }
        });
    }
    else {
        alert('Please enter username and password.')
    }
}
/////////////////////////////////////