jQuery(function ($) {
    // Correctly decide between ws:// and wss://
    let ws_scheme = window.location.protocol === "https:" ? "wss" : "ws",
        ws_path;

    ws_path = ws_scheme + '://' + window.location.host + "/ws/session/whoisonlinethread";
    console.log("Connecting to " + ws_path);
    let onlinethreadsocket = new WebSocket(ws_path);

    let environment = {},
        mode = $('section.whoisonline').attr('data-mode'),
        start_id_selector = null;

    if (mode === "thread") {
        start_id_selector = "user-";
        $('p[id^="' + start_id_selector + '"]').each(function (i, element) {
            environment[$(element).attr('id')] = {"online": false, "timeout": null};
        });
    }

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
});