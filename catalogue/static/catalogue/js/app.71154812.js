(function(t){function e(e){for(var a,o,d=e[0],u=e[1],c=e[2],p=0,l=[];p<d.length;p++)o=d[p],n[o]&&l.push(n[o][0]),n[o]=0;for(a in u)Object.prototype.hasOwnProperty.call(u,a)&&(t[a]=u[a]);s&&s(e);while(l.length)l.shift()();return i.push.apply(i,c||[]),r()}function r(){for(var t,e=0;e<i.length;e++){for(var r=i[e],a=!0,d=1;d<r.length;d++){var u=r[d];0!==n[u]&&(a=!1)}a&&(i.splice(e--,1),t=o(o.s=r[0]))}return t}var a={},n={app:0},i=[];function o(e){if(a[e])return a[e].exports;var r=a[e]={i:e,l:!1,exports:{}};return t[e].call(r.exports,r,r.exports,o),r.l=!0,r.exports}o.m=t,o.c=a,o.d=function(t,e,r){o.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:r})},o.r=function(t){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},o.t=function(t,e){if(1&e&&(t=o(t)),8&e)return t;if(4&e&&"object"===typeof t&&t&&t.__esModule)return t;var r=Object.create(null);if(o.r(r),Object.defineProperty(r,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var a in t)o.d(r,a,function(e){return t[e]}.bind(null,a));return r},o.n=function(t){var e=t&&t.__esModule?function(){return t["default"]}:function(){return t};return o.d(e,"a",e),e},o.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},o.p="/";var d=window["webpackJsonp"]=window["webpackJsonp"]||[],u=d.push.bind(d);d.push=e,d=d.slice();for(var c=0;c<d.length;c++)e(d[c]);var s=u;i.push([0,"chunk-vendors"]),r()})({0:function(t,e,r){t.exports=r("56d7")},"56d7":function(t,e,r){"use strict";r.r(e);r("cadf"),r("551c"),r("f751"),r("097d");var a=r("a026"),n=r("2f62"),i=(r("7514"),r("ac6a"),{items:[],showCart:!1}),o={cartProducts:function(t){return t.items.map(function(t){var e=t.id,r=t.date,a=t.title,n=t.price,i=t.base_inventory,o=t.quantity;return{id:e,title:a,date:r,price:n,base_inventory:i,quantity:o}})},cartTotalPrice:function(t,e){return e.cartProducts.reduce(function(t,e){return t+e.price*e.quantity},0)},getShowCart:function(t){return t.showCart&&t.items.length>0}},d={cleanCart:function(t){var e=t.state,r=t.dispatch;e.items.forEach(function(t){r("deleteProductFromCart",t)})},toggleShowCart:function(t){var e=t.commit;e("toggleShowCart")},saveCart:function(t){var e=t.state;localStorage.setItem("V3simpleCart",JSON.stringify(e.items))},loadCart:function(t){var e=t.commit,r=t.state;e("loadCart"),e("products/syncInventoryWithCart",{productsFromCart:r.items},{root:!0})},addProductToCart:function(t,e){var r=t.state,a=t.commit,n=t.dispatch;if(n("loadCart"),e.inventory>0){var i=!0,o=r.items.find(function(t){return t.id===e.id&&t.date===e.date});o?o.quantity<=8?a("incrementItemQuantity",{id:o.id,date:o.date}):i=!1:a("pushProductToCart",{product:e}),i&&(n("saveCart"),a("products/decrementProductInventory",{id:e.id,date:e.date},{root:!0}))}r.items.length>0&&a("setShowCart",{value:!0})},deleteProductFromCart:function(t,e){var r=t.commit,a=t.dispatch,n=t.state;a("loadCart");var i=n.items.find(function(t){return t.id===e.id&&t.date===e.date});void 0!==i&&(r("products/addProductInventory",{id:i.id,date:i.date,quantity:i.quantity},{root:!0}),r("deleteProductFromCart",{id:i.id,date:i.date}),a("saveCart"))},setQuantityToProductCart:function(t,e){var r=t.commit,a=t.rootState,n=t.state,i=t.dispatch,o=e.productFromCart,d=e.quantity,u=d;if(isNaN(d)?d=0:d>9?d=9:d<=0&&(d=0),0===d)i("deleteProductFromCart",o);else{i("loadCart");var c=a.products.all.find(function(t){return t.id===o.id&&t.date===o.date}),s=n.items.find(function(t){return t.id===o.id&&t.date===o.date}),p=s.quantity;if(r("setQuantityToProductCart",{id:o.id,date:o.date,quantity:9===d?u:d}),c){var l=d-p;if(c.inventory-l>=0)r("products/addProductInventory",{id:c.id,date:c.date,quantity:-l},{root:!0}),r("setQuantityToProductCart",{id:o.id,date:o.date,quantity:d});else{var v=p+c.inventory;r("products/addProductInventory",{id:c.id,date:c.date,quantity:-c.inventory},{root:!0}),r("setQuantityToProductCart",{id:o.id,date:o.date,quantity:v})}}else d>=s.base_inventory?r("setQuantityToProductCart",{id:o.id,date:o.date,quantity:s.base_inventory>9?9:s.base_inventory}):9===d&&r("setQuantityToProductCart",{id:o.id,date:o.date,quantity:d});i("saveCart")}}},u={setShowCart:function(t,e){var r=e.value;t.showCart=r},toggleShowCart:function(t){t.items.length>0?t.showCart=!t.showCart:!0===t.showCart&&(t.showCart=!1)},loadCart:function(t){t.items=[];var e=localStorage.getItem("V3simpleCart");null!==e&&JSON.parse(e).forEach(function(e){t.items.push({id:e.id,title:e.title,date:e.date,base_inventory:e.base_inventory,price:e.price,quantity:e.quantity})})},pushProductToCart:function(t,e){var r=e.product;t.items.push({id:r.id,title:r.title,date:r.date,base_inventory:r.base_inventory,price:r.price,quantity:1})},setQuantityToProductCart:function(t,e){var r=e.id,a=e.date,n=e.quantity,i=t.items.find(function(t){return t.id===r&&t.date===a});i.quantity=n},deleteProductFromCart:function(t,e){var r=e.id,a=e.date;t.items=t.items.filter(function(t){return String(t.id)+t.date!==String(r)+a})},incrementItemQuantity:function(t,e){var r=e.id,a=e.date,n=t.items.find(function(t){return t.id===r&&t.date===a});n.quantity++}},c={namespaced:!0,state:i,getters:o,actions:d,mutations:u},s={all:[]},p={},l={addProduct:function(t,e){var r=t.commit,a=t.rootState,n=e.id,i=e.price,o=e.inventory,d=e.date,u=e.title;r("addProduct",{id:n,price:i,inventory:o,date:d,title:u}),r("syncInventoryWithCart",{productsFromCart:a.cart.items})}},v={addProduct:function(t,e){var r=e.id,a=e.price,n=e.inventory,i=e.date,o=e.title;t.all.push({id:r,price:a,inventory:n,date:i,title:o,base_inventory:n})},decrementProductInventory:function(t,e){var r=e.id,a=e.date,n=t.all.find(function(t){return t.id===r&&t.date===a});n&&n.inventory--},addProductInventory:function(t,e){var r=e.id,a=e.date,n=e.quantity,i=t.all.find(function(t){return t.id===r&&t.date===a});i&&(i.inventory+=n)},setProductInventory:function(t,e){var r=e.id,a=e.date,n=e.quantity,i=t.all.find(function(t){return t.id===r&&t.date===a});i&&(i.inventory=n)},syncInventoryWithCart:function(t,e){var r=e.productsFromCart;t.all.forEach(function(t){var e=r.find(function(e){return t.id===e.id&&t.date===e.date}),a=0;void 0!==e&&(e.base_inventory=t.base_inventory,e.quantity>=e.base_inventory&&(e.quantity=e.base_inventory>9?9:e.base_inventory),a=e.quantity),t.inventory=t.base_inventory-a})}},f={namespaced:!0,state:s,getters:p,actions:l,mutations:v};a["a"].use(n["a"]);var y=new n["a"].Store({modules:{cart:c,products:f},strict:!0}),m=(r("a481"),/(\d{3})(?=\d)/g);function h(t,e,r){if(t=parseFloat(t),!isFinite(t)||!t&&0!==t)return"";e=null!=e?e:"$",r=null!=r?r:2;var a=Math.abs(t).toFixed(r),n=r?a.slice(0,-1-r):a,i=n.length%3,o=i>0?n.slice(0,i)+(n.length>3?" ":""):"",d=r?a.slice(-1-r):"",u=t<0?"-":"";return u+e+o+n.slice(i).replace(m,"$1,")+d}var C=function(){var t=this,e=t.$createElement,r=t._self._c||e;return r("a",{staticClass:"btn",class:{"btn-warning":void 0===t.cartProduct,"btn-info":void 0!==t.cartProduct},attrs:{tabindex:"-1",href:""},on:{click:function(e){return e.preventDefault(),t.addProductToCart(e)}}},[t._t("default"),t._v("\n    - "+t._s(t.product.inventory)+" places\n")],2)},b=[],g=(r("c5f6"),{name:"ButtonCart",props:{id:{required:!0,type:Number},price:{required:!0,type:Number},inventory:{required:!0,type:Number},date:{required:!0,type:String},title:{required:!0,type:String}},computed:{product:function(){var t=this;return this.$store.state.products.all.find(function(e){return e.id===t.id&&e.date===t.date})},cartProduct:function(){var t=this;return this.$store.state.cart.items.find(function(e){return e.id===t.id&&e.date===t.date})}},methods:{addProductToCart:function(t){var e=t.target,r=!1,a="";this.product.inventory<=0?(r=!0,a='Vous ne pouvez plus ajouter "'+this.product.title+"\" dans le panier car il n'y plus de place disponible."):this.$store.state.cart.items.length>=3?(r=!0,a="Vous avez dépassé le nombre d'événements par panier."):void 0!==this.cartProduct&&this.cartProduct.quantity>=9&&(r=!0,a="Vous avez atteint le nombre maximun d'événements pour \""+this.product.title+'".'),r?jQuery(function(t){!1!==t(e).data("popover")&&void 0!==t(e).data("popover")||(t(e).popover({content:a,trigger:"focus",placement:"top"}),t(e).popover("toggle"),t(e).data("popover",!0))}):(jQuery(function(t){!0===t(e).data("popover")&&(t(e).popover("dispose"),t(e).data("popover",!1))}),this.$store.dispatch("cart/addProductToCart",this.product),window.scrollTo(0,0))}},created:function(){this.$store.dispatch("products/addProduct",{id:this.id,price:this.price,inventory:this.inventory,date:this.date,title:this.title})}}),_=g,P=r("2877"),q=Object(P["a"])(_,C,b,!1,null,null,null),w=q.exports,S=function(){var t=this,e=t.$createElement,r=t._self._c||e;return r("table",{staticClass:"table panier table-bordered mt-3"},[r("caption",[t._v("Votre panier")]),t._m(0),r("transition-group",{attrs:{name:"trbody",tag:"tbody"}},t._l(t.products,function(e,a){return r("tr",{key:e.id+e.date},[r("td",[t._v(t._s(a+1))]),r("td",[t._v(t._s(e.title))]),r("td",[t._v(t._s(e.date))]),r("transition",{attrs:{name:"tdcount",mode:"out-in"}},[r("td",{key:e.quantity},[r("div",{staticClass:"input-group"},[r("div",{staticClass:"input-group-prepend"},[r("span",{staticClass:"input-group-text"},[r("i",{staticClass:"fas fa-sort-amount-up"})])]),r("input",{attrs:{type:"number",min:"0",max:"9"},domProps:{value:e.quantity},on:{blur:function(r){return t.updateQuantity(r,e)}}})])])]),r("td",[r("span",{staticClass:"price"},[t._v(t._s(t._f("currency")(e.price*e.quantity,"€")))])]),r("td",[r("a",{attrs:{href:"#"},on:{click:function(r){return r.preventDefault(),t.deleteProductFromCart(e)}}},[r("i",{staticClass:"far fa-trash-alt"})])])],1)}),0),r("tfoot",[r("th",{staticClass:"text-center",attrs:{colspan:"4"}},[r("a",{staticClass:"btn btn-warning",attrs:{href:t.submit_url}},[t._v("Valider le panier")]),r("a",{staticClass:"btn btn-danger ml-2",attrs:{href:"#"},on:{click:function(e){return t.cleanCart()}}},[t._v("Supprimer mon panier")])]),r("th",[t._v("\n        Total : "+t._s(t._f("currency")(t.total,"€"))+"\n        "),r("i",{staticClass:"fas fa-euro-sign"})])])],1)},T=[function(){var t=this,e=t.$createElement,r=t._self._c||e;return r("thead",[r("tr",[r("th",{attrs:{scope:"col"}},[t._v("#")]),r("th",{attrs:{scope:"col"}},[t._v("Événement")]),r("th",{attrs:{scope:"col"}},[t._v("Date")]),r("th",{attrs:{scope:"col"}},[t._v("Quantité")]),r("th",{attrs:{scope:"col"}},[t._v("Prix")]),r("th",{attrs:{scope:"col"}},[t._v("Supprimer ?")])])])}],j=r("cebc"),O={name:"ShoppingCart",props:{submit_url:{required:!0,type:String}},computed:Object(j["a"])({},Object(n["c"])("cart",{products:"cartProducts",total:"cartTotalPrice"})),methods:Object(j["a"])({updateQuantity:function(t,e){this.setQuantityToProductCart({productFromCart:e,quantity:parseInt(t.target.value)})}},Object(n["b"])("cart",["deleteProductFromCart","setQuantityToProductCart","cleanCart"])),created:function(){this.$store.dispatch("cart/loadCart",{})}},Q=O,x=(r("5fb3"),Object(P["a"])(Q,S,T,!1,null,null,null)),F=x.exports;a["a"].filter("currency",h),a["a"].config.productionTip=!0,new a["a"]({el:"#app",store:y,methods:{toggleShowCart:function(t){var e=t.target;this.$store.dispatch("cart/toggleShowCart"),0===this.$store.state.cart.items.length?jQuery(function(t){!1!==t(e).data("popover")&&void 0!==t(e).data("popover")||(t(e).popover({content:"Votre panier est vide",trigger:"focus",placement:"bottom"}),t(e).popover("toggle"),t(e).data("popover",!0))}):jQuery(function(t){!0===t(e).data("popover")&&(t(e).popover("dispose"),t(e).data("popover",!1))})}},components:{buttonCart:w,shoppingCart:F},computed:Object(n["c"])("cart",{showCart:"getShowCart"})})},"5fb3":function(t,e,r){"use strict";var a=r("ac9f"),n=r.n(a);n.a},ac9f:function(t,e,r){}});