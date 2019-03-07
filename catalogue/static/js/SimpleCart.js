jQuery(function ($) {

    /* Default Options */
    let defaults = {
        cart: [],
        addtoCartClass: '.sc-add-to-cart',
        clearCartClass: '.sc-clear-cart'
    };

    class Item {
        constructor(id, name, date, count) {
            this.id = id;
            this.name = name;
            this.date = date;
            this.count = count;
        }
    }

    /*Constructor function*/
    class SimpleCart {

        constructor(domEle, options = {}) {
            /* Merge user settings with default, recursively */
            this.options = $.extend(true, {}, defaults, options);
            //Cart array
            this.cart = [];
            //Dom Element
            this.cart_ele = $(domEle);

            //Initial init function
            this._setEvents();
            this._loadCart();
            this._updateCartDetails();

            this.tbody_item_cart = $('<tbody></tbody>');

            let table_item_cart = $('<table></table>').addClass('table table-bordered mb-0')
                .append(
                    $('<thead></thead>').html(
                        '<tr>\n' +
                        '      <th scope="col">#</th>\n' +
                        '      <th scope="col">Nom</th>\n' +
                        '      <th scope="col">Date</th>\n' +
                        '      <th scope="col">Quantité</th>\n' +
                        '    </tr>')
                ).append(
                    this.tbody_item_cart
                ).append(
                    $('<tbody></tbody>').html(
                        '<th class="text-center" colspan="4"><buttton class="btn btn-warning">Valider le panier</buttton></th>'
                    )
                );

            this.row_col_table_item_cart = $('<div></div>').addClass('row mt-4').append(
                $('<div></div>').addClass('col-12').prepend(table_item_cart)
            );
        }

        _setEvents() {
            let mi = this;

            $(this.options.addtoCartClass).on("click", function (e) {
                e.preventDefault();
                let id = $(this).attr("data-id");
                let name = $(this).attr("data-name");
                let date = $(this).attr("data-date");

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
                    mi._addItemToCart(id, name, date, 1);
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
                }
            })
        }

        _updateCartDetails() {
            let mi = this;
            $(this.cart_ele).text(mi._totalCartCount());
        }

        /* Helper Functions */
        _addItemToCart(id, name, date, count) {
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
                let item = new Item(id, name, date, count);
                this.cart.push(item);
                this._saveCart();
                this._addTableItem(item);
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
                    input_count_of_item.parents('tr').removeClass();
                    input_count_of_item.parents('tr').addClass('color-yellow');
                    input_count_of_item.parents('tr').delay(200)
                        .queue(function (next) {
                            $(this).addClass('transition');
                            next();
                        });
                }
                return;
            }

            let input_count = $('<input />').attr({
                type: 'number',
                min: 0,
                max: 9,
                value: item.count,
                data_for_selector: item.id + item.date,
                class: 'form-control'
            });

            input_count.on('change', function (e) {
                e.preventDefault();
                let count = $(this).val();

                if (count > 9) {
                    $(this).val(9);
                    count = 9
                } else if (!$.isNumeric(count)) {
                    count = '0'
                }
                mi._removeItemfromCart(this, item, count);
                mi._updateCartDetails();
            });

            let tr_tbody_item_cart = $('<tr></tr>').html(
                '<td>' + ($(this.tbody_item_cart).find("tr").length + 1) + '</td>\n' +
                '      <td>' + item.name + '</td>\n' +
                '      <td>' + item.date + '</td>');

            this.tbody_item_cart.prepend(tr_tbody_item_cart);

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
            );

            if (!(from_show)) {
                tr_tbody_item_cart.addClass('color-yellow');
                tr_tbody_item_cart.delay(200)
                    .queue(function (next) {
                        $(this).addClass('transition');
                        next();
                    });
            }
        }

        _removeItemfromCart(input, item, count) {
            for (let i in this.cart) {
                if (this.cart[i].name === item.name && this.cart[i].date === item.date) {
                    this.cart[i].count = count;
                    if (count === '0') {
                        this.cart.splice(i, 1);
                        $(input).parents('tr').remove();

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
    }

    /* Defining the Structure of the plugin 'simpleCart'*/
    $.fn.simpleCart = function () {
        return this.each(function () {
            $(this).data("simpleCart", new SimpleCart(this));
        });
    };
});