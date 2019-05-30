jQuery(function ($) {
    // Correctly decide between ws:// and wss://
    let ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    let ws_path = ws_scheme + '://' + window.location.host + "/ws/session/thread/" + $.trim($('span#current_username').attr('data-username'));
    console.log("Connecting to " + ws_path);

    let threadsocket = new WebSocket(ws_path);

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
        let data = JSON.parse(e.data);
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
            $('ul#thread-items').append($('<li></li>').text(data.message + " via " + data.username));
        }
    };

    threadsocket.onerror = function (e) {
        console.log("error", e)
    };

    threadsocket.onclose = function (e) {
        console.log("Disconnected from thread socket");
    }
});