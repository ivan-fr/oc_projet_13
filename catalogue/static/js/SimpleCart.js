jQuery(function ($) {

    /* Default Options */
    let defaults = {
        cart: [],
        addtoCartClass: '.sc-add-to-cart',
    };

    class Item {
        constructor(id, name, date, count, price) {
            this.id = id;
            this.name = name;
            this.date = date;
            this.count = count;
            this.price = parseFloat(price)
        }
    }

    class SimpleCart {

        constructor(domEle, options = {}) {
            /* Merge user settings with default, recursively */
            this.options = $.extend(true, {}, defaults, options);
            //Cart array
            this.cart = [];
            //Dom Element
            this.cart_ele = $(domEle);

            //Initial init function
            this._loadCart();
            this._markAddItemButton();
            this._setEvents();

            this.tbody_item_cart = $('<tbody></tbody>');
            this._updateCartDetails();

            this.total_price = $('<th></th>');

            let table_item_cart = $('<table></table>').addClass('table panier table-bordered mb-0')
                .prepend($('<caption></caption>').text('Votre panier'))
                .append(
                    $('<thead></thead>').html(
                        '<tr>\n' +
                        '      <th scope="col">#</th>\n' +
                        '      <th scope="col">Événement</th>\n' +
                        '      <th scope="col">Date</th>\n' +
                        '      <th scope="col">Quantité</th>\n' +
                        '      <th scope="col">Prix</th>\n' +
                        '    </tr>')
                ).append(
                    this.tbody_item_cart
                ).append(
                    $('<tfoot></tfoot>').html(
                        '<th class="text-center" colspan="4"><a href="' + this.cart_ele.attr('data-url-submit-button') + '" class="btn btn-warning">' +
                        'Valider mon panier</a></th>'
                    ).append(this.total_price)
                );

            this.row_col_table_item_cart = $('<div></div>').addClass('row mt-4').append(
                $('<div></div>').addClass('col-12').prepend(table_item_cart)
            );

        }

        _markAddItemButton() {

            $('a[class*="sc-add-to-cart"][data-id][data-date]')
                .removeClass('btn-warning')
                .removeClass('btn-primary')
                .addClass('btn-warning')
                .each(function () {
                    $(this).popover('dispose');
                    $(this).data('popover', false);
                });

            for (let i in this.cart) {
                if (this.cart.hasOwnProperty(i)) {
                    $('a[class*="sc-add-to-cart"][data-id="' + this.cart[i].id + '"][data-date="' + this.cart[i].date + '"]')
                        .removeClass('btn-warning').addClass('btn-primary');
                }
            }
        }

        _disableEvents() {
            $(this.options.addtoCartClass).off();
            this.cart_ele.parent().off();
        }

        _setEvents() {
            let mi = this;

            $(this.options.addtoCartClass).on("click", function (e) {
                e.preventDefault();
                let id = $(this).attr("data-id");
                let name = $(this).attr("data-name");
                let date = $(this).attr("data-date");
                let price = $(this).attr('data-price');

                if (id !== undefined && name !== undefined && date !== undefined) {
                    if (!(mi.cart_ele.parent().hasClass('active'))) {
                        if (mi._totalCartCount() <= 2) {
                            mi.showTableItem();
                        } else {
                            for (let i in mi.cart) {
                                if (mi.cart.hasOwnProperty(i) && mi.cart[i].id === id && mi.cart[i].date === date) {
                                    mi.showTableItem();
                                    break;
                                }
                            }
                        }
                    }
                    mi._addItemToCart(id, name, date, 1, price, this);
                    mi._updateCartDetails();
                }
            });

            this.cart_ele.parent().on('click', function (e) {
                e.preventDefault();
                if (mi.cart_ele.parent().hasClass('active')) {
                    mi.cart_ele.parent().removeClass('active');
                    mi.row_col_table_item_cart.hide();
                } else {
                    mi.showTableItem();
                    mi._updateCartDetails();
                }
            })
        }

        _updateCartDetails() {
            let mi = this;
            $(this.cart_ele).text(mi._totalCartCount());
            $(this.tbody_item_cart).find("td.counter").each(
                function (index) {
                    $(this).text(index + 1);
                }
            );

            let total_price = 0;
            $(this.tbody_item_cart).find("td span.price").each(
                function () {
                    total_price += parseFloat($(this).text());
                }
            );

            $(this.total_price).html(total_price.toFixed(2) + ' <i class="fas fa-euro-sign"></i>')
        }

        /* Helper Functions */
        _addItemToCart(id, name, date, count, price, button) {
            for (let i in this.cart) {
                if (this.cart.hasOwnProperty(i) && this.cart[i].id === id && this.cart[i].date === date) {
                    if (this.cart[i].count <= 8) {
                        this.cart[i].count++;
                        this._saveCart();
                    }
                    this._addTableItem(this.cart[i]);
                    return;
                }
            }

            if (this._totalCartCount() <= 2) {
                let item = new Item(id, name, date, count, price);
                this.cart.push(item);
                this._saveCart();
                this._addTableItem(item);
                this._markAddItemButton();
            } else {
                if ($(button).data("popover") === false) {
                    $(button).popover({
                        content: 'Vous avez dépassé le nombre d\'événements par panier.',
                        trigger: 'focus'
                    });
                    $(button).popover('show');
                    $(button).data('popover', true)
                }
            }
        }

        showTableItem() {
            for (let i in this.cart) {
                this._addTableItem(this.cart[i], true)
            }
        }

        _addTableItem(item, from_show = false) {
            window.scrollTo(0, 0);

            if (!(this.cart_ele.parent().hasClass('active'))) {
                this.cart_ele.parent().addClass('active');
            }

            if (this.row_col_table_item_cart.is(":hidden")) {
                this.row_col_table_item_cart.show();
            }

            if ($(this.tbody_item_cart).html() === '') {
                $('body > .container').prepend(this.row_col_table_item_cart);
            }

            let mi = this;
            let input_count_of_item = this.tbody_item_cart.find('input[data_for_selector="' + item.id + item.date + '"]');

            if (input_count_of_item.length === 1) {
                if (!from_show) {
                    input_count_of_item.val(item.count);
                    let principale_tr = input_count_of_item.parents('tr');
                    principale_tr.find('.price').text((item.count * item.price).toFixed(2));
                    principale_tr.removeClass();
                    principale_tr.addClass('color-yellow');
                    principale_tr.delay(200)
                        .queue(function (next) {
                            $(this).addClass('transition');
                            next();
                        });
                }
                return;
            }

            let price_count = $('<td></td>').html('<span class="price">' + (item.price * item.count).toFixed(2) + '</span> <i class="fas fa-euro-sign"></i>');

            let input_count = $('<input />').attr({
                type: 'number',
                min: 0,
                max: 9,
                value: item.count,
                data_for_selector: item.id + item.date,
                class: 'form-control input_count'
            });

            input_count.on('change', function (e) {
                e.preventDefault();
                let count = $(this).val();

                if (count > 9) {
                    $(this).val(9);
                    count = 9
                } else if (count <= 0) {
                    $(this).val(0);
                    count = '0'
                } else if (!$.isNumeric(count)) {
                    count = '0'
                }
                price_count.find('span').text((parseFloat(count) * item.price).toFixed(2));
                mi._removeItemFromCart(this, item, count);
                mi._updateCartDetails();
            });

            let tr_tbody_item_cart = $('<tr></tr>').html(
                '<td class="counter"></td>\n' +
                '      <td>' + item.name + '</td>\n' +
                '      <td>' + item.date + '</td>');

            this.tbody_item_cart.append(tr_tbody_item_cart);

            tr_tbody_item_cart.append(
                $('<td></td>').append(
                    $('<div></div>').addClass('input-group')
                        .append(
                            $('<div></div>').addClass('input-group-prepend')
                                .append(
                                    $('<span></span>').addClass('input-group-text').html('<i class="fas fa-sort-amount-up"></i>')
                                )
                        ).append(input_count)
                )
            ).append(price_count);

            if (!(from_show)) {
                tr_tbody_item_cart.addClass('color-yellow');
                tr_tbody_item_cart.delay(200)
                    .queue(function (next) {
                        $(this).addClass('transition');
                        next();
                    });
            }
        }

        _removeItemFromCart(input_count, item, count) {
            for (let i in this.cart) {
                if (this.cart[i].name === item.name && this.cart[i].date === item.date) {
                    this.cart[i].count = count;
                    if (count === '0') {
                        this.cart.splice(i, 1);
                        $(input_count).parents('tr').remove();
                        this._markAddItemButton();

                        if ($(this.tbody_item_cart).find("tr").length === 0) {
                            this.row_col_table_item_cart.hide();
                            this.cart_ele.parent().removeClass('active');
                        }
                    }
                    break;
                }
            }
            this._saveCart();
        }

        _totalCartCount() {
            return this.cart.length;
        }

        _saveCart() {
            localStorage.setItem("shoppingCart", JSON.stringify(this.cart));
        }

        _loadCart() {
            this.cart = JSON.parse(localStorage.getItem("shoppingCart"));
            if (this.cart === null) {
                this.cart = [];
            }
        }

        _clearCart() {
            this.cart = [];
            this._saveCart();
            this.tbody_item_cart.html('');
            this.row_col_table_item_cart.hide();
            this.cart_ele.parent().removeClass('active');
            this._updateCartDetails();
        }
    }

    /* Defining the Structure of the plugin 'simpleCart'*/
    $.fn.simpleCart = function () {
        return this.data("simpleCart", new SimpleCart(this));
    };
});