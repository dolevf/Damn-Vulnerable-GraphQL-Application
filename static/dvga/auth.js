function parseJwt(token) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    var jsonPayload = decodeURIComponent(atob(base64).split('').map(function (c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    return JSON.parse(jsonPayload);
}

function getCookie(name) {
    var cookieArr = document.cookie.split(";");
    for (var i = 0; i < cookieArr.length; i++) {
        var cookiePair = cookieArr[i].split("=");
        if (name == cookiePair[0].trim()) {
            return decodeURIComponent(cookiePair[1]);
        }
    }
    return null;
}


function getUsernameFromJWT() {
    return JSON.parse(atob(getCookie('dvga_jwt').split('.')[1]))['sub']
}

function getUserRolesFromJWT() {
    return JSON.parse(atob(getCookie('dvga_jwt').split('.')[1]))['prv']
}




window.onload = function () {
    document.getElementById('manage_users').style.display = "none";
    manage_users_option = document.getElementById('manage_users')
    if (getUserRolesFromJWT().indexOf('admin') > -1) {
        document.getElementById('manage_users').style.display = "";
    }
    
}