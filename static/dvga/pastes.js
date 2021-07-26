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

function burnSelect() {
    var isChecked = document.getElementById("burn").checked;
    document.getElementById("visibility").disabled = isChecked;
}

function getPastesByUsername(username) {
    var query = `query getPastesByUsername {
                            pastes(username:"${username}") {
                                id
                                title
                                content
                                ipAddr
                                userAgent
                                user {
                                    username
                                }
                            }
                }`

    fetch('/graphql', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        body: JSON.stringify({
            query
        })
    }).then(
        r => r.json()
    ).then(
        (object) => {
            for (var i = 0; i < object['data']['pastes'].length; i++) {
                var obj = object.data.pastes[i];
                var id = atob(obj.id).split(':')[1]
                var title = obj.title
                var content = obj.content
                var user = obj.user.username
                var ip_addr = obj.ipAddr
                var uas = obj.userAgent

                $("#gallery").append(
                    `<div class="card-header">
                        <i class="fa fa-paste"></i> &nbsp; ${title}
                        <button id="paste-${id}" class="btn btn-primary btn-sm float-right" title="Moderators click here to make the paste private" onclick="demoderatePaste('${id}')">DeModerate</button>
                    </div>
                    <div class="card-body">
                        <p class="card-text">
                            <pre>${content}</pre>
                            <br><hr />
                            <i class="fa fa-user"></i>
                            <i><small><b>${user}</b><br>- ${ip_addr}<br>- (${uas})</small></i>
                        </p>
                    </div>`
                )
            }
        }
    );
}

function getPublicPastes() {
    var query = `query getPublicPastes {
                            publicPastes {
                                id
                                title
                                content
                                ipAddr
                                userAgent
                                user {
                                    username
                                }
                            }
                }`

    fetch('/graphql', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        body: JSON.stringify({
            query
        })
    }).then(
        r => r.json()
    ).then(
        (object) => {
            for (var i = 0; i < object['data']['publicPastes'].length; i++) {
                var obj = object.data.publicPastes[i];
                var id =        atob(obj.id).split(':')[1]
                var title =     obj.title
                var content =   obj.content
                var user =      obj.user.username
                var ip_addr =   obj.ipAddr
                var uas =       obj.userAgent

                var moderation = ""
                if (getUserRolesFromJWT().indexOf('moderator') > -1) {
                    moderation = `<button id="paste-${id}" class="btn btn-primary btn-sm float-right" title="Moderators click here to make the paste private" onclick="moderatePaste('${id}')">Moderate</button>`
                }
                    

                $("#gallery").append(
                    `<div class="card-header">
                        <i class="fa fa-paste"></i> &nbsp; ${title}
                        ${moderation}
                    </div>
                    <div class="card-body">
                        <p class="card-text">
                            <pre>${content}</pre>
                            <br><hr />
                            <i class="fa fa-user"></i>
                            <i><small><b>${user}</b><br>- ${ip_addr}<br>- (${uas})</small></i>
                        </p>
                    </div>`
                )
            }
        }
    );
}
function moderatePaste(id) {
    var query = `mutation ModeratePaste {
	                 moderatePaste(id:${id}, visibility:false) {
  	                     ok
                     }
                 }`

    fetch('/graphql', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        body: JSON.stringify({
            query,
        })
    })
    
}

function demoderatePaste(id) {
    var query = `mutation ModeratePaste {
	                 moderatePaste(id:${id}, visibility:true) {
  	                     ok
                     }
                 }`

    fetch('/graphql', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        body: JSON.stringify({
            query,
        })
    })
    
}

function parseJwt(token) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    var jsonPayload = decodeURIComponent(atob(base64).split('').map(function (c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    return JSON.parse(jsonPayload);
};


function create_paste() {
    var title = document.getElementById('title').value
    var content = document.getElementById('content').value
    var visibility = document.getElementById('visibility').value
    var public = false
    var burn = document.getElementById('burn').checked
    var username = parseJwt(document.cookie.split('=')[1]).sub

    if (visibility == "Public") {
        public = true;
    }

    var query = `mutation CreatePaste ($title: String!, $content: String!, $public: Boolean!, $burn: Boolean!, $username: String!) {
                            createPaste(title:$title, content:$content, public:$public, burn: $burn, username: $username) {
                                paste {
                                    pId
                                    content
                                    title
                                    burn
                                }
                            }
                        }`

    fetch('/graphql', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        body: JSON.stringify({
            query,
            variables: { title, content, public, burn, username },
        })
    }).then(
        r => r.json()
    ).then(
        (data => {
            if (data.data.createPaste.paste.burn == true) {
                var host = window.location.protocol + "//" + window.location.host;
                var p_id = parseInt(data.data.createPaste.paste.pId)
                url = host + `/graphql?query=query%20readAndBurn%20%7B%0A%20%20readAndBurn(pId%3A${p_id})%7B%0A%20%20%20%20title%0A%20%20%20%20content%0A%20%20%20%20burn%0A%20%20%7D%0A%7D%0A`
                $("#result").append(
                    `<div class="alert alert-success">
                        <br>
                        <h4 class="alert-heading">Well done!</h4>
                        <p>Paste was created successfully</p>
                        <p>Here is your paste <a href="${url}">link</a></p>
                    </div>`
                )
            }
            else {
                $("#result").append(
                    `<div class="alert alert-success">
                        <h4 class="alert-heading">Well done!</h4>
                        <p>Paste was created successfully</p>
                    </div>`
                )
            }
        }
        )
    )
}

function importPaste() {
    const url = document.getElementById('url').value;
    const u = new URL(url);
    const host = u.hostname;
    const path = u.pathname;
    const scheme = u.protocol.replace(':', '');
    var port = u.port;

    if (!port) {
        if (scheme == 'http') {
            port = 80
        }
        else if (scheme == 'https') {
            port = 443
        }
        else {
            port = 80
        }
    }

    var query = `mutation ImportPaste ($host: String!, $port: Int!, $path: String!, $scheme: String!) {
                    importPaste(host: $host, port: $port, path: $path, scheme: $scheme) {
                        result
                    }
                }`

    fetch('/graphql', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        body: JSON.stringify({
            query,
            variables: { host, port, path, scheme }
        })
    }).then(
        r => r.json()
    ).then(
        (data => {
            if (data.data.importPaste != "error") {
                $("#result").append(
                    `<div class="alert alert-success">
                        <h4 class="alert-heading">Success!</h4>
                        <p>Paste was imported successfully</p>
                    </div>`
                )
            } else {
                $("#result").append(
                    `<div class="alert alert-danger">
                        <h4 class="alert-heading">Error!</h4>
                        <p>Paste failed to import.</p>
                    </div>`
                )
            }
        })
    )
}

function uploadPaste() {
    var reader = new FileReader();
    var f = document.getElementById("pastefile").files;
    var content = ''

    reader.readAsText(f[0])

    reader.onloadend = function () {
        var filename = document.getElementById("pastefile").files[0].name
        content = reader.result
        var query = `mutation UploadPaste ($filename: String!, $content: String!) {
                        uploadPaste(filename: $filename, content:$content){
                            result
                        }
                    }`

        fetch('/graphql', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            body: JSON.stringify({
                query,
                variables: { content, filename }
            })
        }).then(
            r => r.json()
        ).then(
            (data => {
                if (!data.hasOwnProperty('errors')) {
                    $("#result").append(
                        `<div class="alert alert-success">
                            <h4 class="alert-heading">Success!</h4>
                            <p>File was uploaded successfully</p>
                        </div>`
                    )
                } else {
                    $("#result").append(
                        `<div class="alert alert-danger">
                            <h4 class="alert-heading">Error!</h4>
                            <p>Paste failed to import.</p>
                        </div>`
                    )
                }
            })
        )
    }
}

window.onload = function () {
    var url = window.location.pathname
    if (url.match('/my_pastes')) {
        getPastesByUsername(getUsernameFromJWT())
    }
    else if (url.match('/public_pastes')) {
        getPublicPastes()
    }
}
