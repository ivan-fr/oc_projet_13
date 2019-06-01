jQuery(function ($) {

    // Correctly decide between ws:// and wss://
    let ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";


    let environment = {},
        mode = $('section.whoisonline').attr('data-mode'),
        start_id_selector = null,
        threadsocket;

    if (mode === "thread") {
        let thread_ws_path = ws_scheme + '://' + window.location.host + "/ws/session/thread/" + $.trim($('span#current_username').attr('data-username'));
        console.log("Connecting to " + thread_ws_path);

        threadsocket = new WebSocket(thread_ws_path);

        function thread_form_listener(e) {
            e.preventDefault();
            let formdata = new FormData(e.target),
                data = {};

            for (let [key, value] of formdata.entries()) {
                data[key] = value;
            }

            let errors_form = e.target.querySelectorAll(".list-error");

            Array.prototype.forEach.call(errors_form, function (element) {
                element.parentNode.removeChild(element);
            });
            threadsocket.send(JSON.stringify(data));
            this.reset();
        }

        $("form#thread_form").on("submit", thread_form_listener);

        // Helpful debugging
        threadsocket.onopen = function () {
            console.log("Connected to thread socket");
        };

        threadsocket.onmessage = function (e) {
            console.log("threadsocket", e.data);
            let data = JSON.parse(e.data);
            let user_id;
            if (data.errors_form !== null) {
                data.errors_form.forEach(function (element) {
                    let parent_input = document.getElementById("id_" + element[0]).parentNode;
                    let errors_ul = document.createElement("ul");
                    errors_ul.classList.add("list-error");
                    element[1].forEach(function (sub_element) {
                        let errors_li = document.createElement("li");
                        errors_li.appendChild(document.createTextNode(sub_element));
                        errors_ul.appendChild(errors_li);
                    });
                    parent_input.appendChild(errors_ul);
                });
            } else {
                let id_recipient;
                let regex = new RegExp("user-([\\d])+");
                $('p[id^="user-"]').each(function (i, element) {
                    id_recipient = $(element).attr('id');
                });

                user_id = parseInt(regex.exec(id_recipient)[1]);

                if (data.user_id !== user_id) {
                    $('div#thread-items').append(
                        '<div class="row justify-content-start"> ' +
                        '<div class="col-6 alert alert-success">' +
                        data.message +
                        '</div>' +
                        '</div>'
                    );
                } else {
                    $('div#thread-items').append(
                        '<div class="row justify-content-end"> ' +
                        '<div class="col-6 alert alert-success">' +
                        data.message +
                        '</div>' +
                        '</div>'
                    );
                }
            }
        };

        threadsocket.onerror = function (e) {
            console.log("error", e)
        };

        threadsocket.onclose = function (e) {
            console.log("Disconnected from thread socket");
        };
    }

    // Correctly decide between ws:// and wss://
    let ws_path,
        onlinethreadsocket;

    function initonlinethreadsocket() {
        setTimeout(function () {
            $.each(environment, function (key, element) {
                if (element.online === false && element.timeout === null) {
                    $('#' + key).find('.status').html("<span class=\"badge badge-danger\">||</span> Déconnecté")
                }
            })
        }, 4000);


        // Helpful debugging
        onlinethreadsocket.onopen = function () {
            console.log("Connected to onlinethread socket");
        };

        onlinethreadsocket.onmessage = function (e) {
            let data = JSON.parse(e.data);
            console.log("onlinethreadsocket", data);

            let select_environment = environment[start_id_selector + data.user_id];

            if (select_environment === undefined) {
                return
            }

            if (data['connected'] === true) {
                if (select_environment.online === false || select_environment.timeout == null) {
                    if (select_environment.timeout !== null && select_environment.online === false) {
                        clearTimeout(select_environment.timeout);
                    }
                    select_environment.timeout = setTimeout(function () {
                        let badge = "<span class=\"badge badge-success\">||</span>";
                        let texte = "Connecté";
                        $('#' + start_id_selector + data.user_id).find('.status').html(badge + " " + texte);
                    }, 1000);
                    select_environment.online = true;
                }
            } else if (select_environment.online === true || select_environment.timeout == null) {
                if (select_environment.timeout !== null && select_environment.online === true) {
                    clearTimeout(select_environment.timeout);
                }
                select_environment.timeout = setTimeout(function () {
                    let badge = "<span class=\"badge badge-danger\">||</span>";
                    let texte = "Déconnecté";
                    $('#' + start_id_selector + data.user_id).find('.status').html(badge + " " + texte);
                }, 4000);
                select_environment.online = false;
            }
        };

        onlinethreadsocket.onerror = function (e) {
            console.log("error", e);
            onlinethreadsocket.automaticOpen = false;
        };

        onlinethreadsocket.onclose = function (e) {
            console.log("Disconnected from onlinethread socket");
        };
    }

    ws_path = ws_scheme + '://' + window.location.host + "/ws/session/whoisonlinethread";

    if (mode === "thread") {
        start_id_selector = "user-";
        $('p[id^="' + start_id_selector + '"]').each(function (i, element) {
            environment[$(element).attr('id')] = {"online": false, "timeout": null};
        });

        setTimeout(function () {
            if (threadsocket.readyState === WebSocket.OPEN) {
                console.log("Connecting to " + ws_path);
                onlinethreadsocket = new WebSocket(ws_path + '/1');
                initonlinethreadsocket();
            }

        }, 1000);


    } else {
        console.log("Connecting to " + ws_path);
        onlinethreadsocket = new WebSocket(ws_path + '/0');
        initonlinethreadsocket();
    }
});

