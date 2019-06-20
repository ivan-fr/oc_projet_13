jQuery(function ($) {
    // Correctly decide between ws:// and wss://
    let ws_scheme = window.location.protocol === "https:" ? "wss" : "ws",
        ws_path;

    let environment = {},
        mode = $('section.whoisonline').attr('data-mode'),
        start_id_selector = null;

    if (mode === "superuser_list") {
        ws_path = ws_scheme + '://' + window.location.host + "/ws/session/whoisonline/1";
        start_id_selector = "superuser-";
        $('tr[id^="' + start_id_selector + '"]').each(function (i, element) {
            environment[$(element).attr('id')] = {"online": false, "timeout": null};
        });
    } else {
        ws_path = ws_scheme + '://' + window.location.host + "/ws/session/whoisonline/0";
    }

    console.log("Connecting to " + ws_path);
    let onlinesocket = new WebSocket(ws_path);

    setTimeout(function () {
        $.each(environment, function (key, element) {
            if (element.online === false && element.timeout === null) {
                $('#' + key).find('.status').html("<span class=\"badge badge-danger\">||</span> Déconnecté")
            }
        })
    }, 4000);

    onlinesocket.onopen = function () {
        console.log("Connected to online socket");
    };

    onlinesocket.onmessage = function (e) {
        let data = JSON.parse(e.data);
        console.log("whoisonline", data);

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

    onlinesocket.onerror = function (e) {
        console.log("error", e)
    };

    onlinesocket.onclose = function (e) {
        console.log("Disconnected from online socket");
    };
});
