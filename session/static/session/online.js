jQuery(function ($) {
    // Correctly decide between ws:// and wss://
    let ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    ws_path = ws_scheme + '://' + window.location.host + "/ws/session/whoisonline/0";
    console.log("Connecting to " + ws_path);

    let onlinesocket = new WebSocket(ws_path);

    // Helpful debugging
    onlinesocket.onopen = function () {
        console.log("Connected to online socket");
    };

    onlinesocket.onmessage = function (e) {
        let data = JSON.parse(e.data);

        if (data.check === true) {
            onlinesocket.send(JSON.stringify(data))
        }
    };

    onlinesocket.onerror = function (e) {
        console.log("error", e)
    };

    onlinesocket.onclose = function (e) {
        console.log("Disconnected from online socket");
    }
});