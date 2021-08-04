function getUsers() {
    var query = `query getUsers {
                            users {
                                username
                                email
                                roles
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
        function (object) {
            var users = object['data']['users']
            for (var i = 0; i < users.length; i++) {
                var user = users[i];
                var username = user.username
                var email = user.email
                var roles = user.roles

                $("#users_list tbody").append(
                    `<tr>
                        <th scope="row">${i}</th>
                        <td>${username}</td>
                        <td>${email}</td>
                        <td>${roles}</td>
                    </tr>`
                )
            }

            return pastes

        }
    );
}


window.onload = function () {
    var url = window.location.pathname
    if (url.match('/users')) {
        getUsers()
    }
}