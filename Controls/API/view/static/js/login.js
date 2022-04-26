
let error_div = document.getElementById('error-message')

function setCookie(name, value, minutes) {
    let expires = "";
    let date = new Date();
    date.setTime(date.getTime() + (minutes * 60 * 1000));
    expires = "; expires=" + date.toUTCString();
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}

function processForm(e) {
    if (e.preventDefault) e.preventDefault();

    const data = Object.fromEntries(new FormData(e.target).entries());

    let urlEncodedData = "";
    let urlEncodedDataPairs = [];
    let name;

    for(name in data) {
      urlEncodedDataPairs.push(encodeURIComponent(name) + '=' + encodeURIComponent(data[name]));
    }

    urlEncodedData = urlEncodedDataPairs.join('&').replace( /%20/g, '+');

    fetch('/api/user/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: urlEncodedData
    }).then(response => {
        response.json().then(data => {
            if (data.access_token) {
                setCookie('access_token', data.access_token, 30)
                window.location.reload();
            } else {
                error_div.innerHTML = data.detail
            }
        });
    });

    return false;
}

let form = document.forms[0];
if (form.attachEvent) {
    form.attachEvent('submit', processForm);
} else {
    form.addEventListener('submit', processForm);
}
