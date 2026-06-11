(function() {
    var KEY = 'lil_viewed';
    var MAX = 12;

    function getIds() {
        try {
            var s = localStorage.getItem(KEY);
            return s ? JSON.parse(s) : [];
        } catch (e) { return []; }
    }

    function setIds(ids) {
        localStorage.setItem(KEY, JSON.stringify(ids));
    }

    window.viewedAdd = function(productId) {
        var ids = getIds().filter(function(x) { return x !== productId; });
        ids.unshift(productId);
        ids = ids.slice(0, MAX);
        setIds(ids);
    };

    window.viewedGetIds = getIds;

    function renderViewed(containerId, excludeId) {
        var container = document.getElementById(containerId);
        if (!container) return;

        var ids = getIds().filter(function(id) { return id !== excludeId; });
        if (ids.length === 0) {
            container.style.display = 'none';
            return;
        }

        var url = '/api/products-by-ids?ids=' + ids.join(',');
        fetch(url).then(function(r) { return r.json(); }).then(function(data) {
            if (!data.products || data.products.length === 0) {
                container.style.display = 'none';
                return;
            }
            var html = '<div class="row">';
            data.products.forEach(function(p) {
                var imgSrc = p.image ? '/static/images/products/' + p.image : 'https://via.placeholder.com/400';
                var imgAlt = (p.name || '').replace(/"/g, '&quot;');
                var priceHtml = p.price + ' ₽';
                if (p.old_price) {
                    priceHtml = '<span class="product-price">' + p.price + ' ₽</span> <span class="old-price">' + p.old_price + ' ₽</span>';
                } else {
                    priceHtml = '<span class="product-price">' + p.price + ' ₽</span>';
                }
                var hitBadge = p.is_hit ? '<span class="badge bg-danger position-absolute top-0 start-0 m-2 product-badge-hit">Хит</span>' : '';
                html += '<div class="col-6 col-md-3 col-lg-2 mb-3">' +
                    '<div class="product-card position-relative h-100">' +
                    hitBadge +
                    '<a href="' + p.url + '" class="product-card-link text-decoration-none text-dark d-block">' +
                    '<div class="product-card-img-wrap">' +
                    '<img src="' + imgSrc + '" class="img-fluid" alt="' + imgAlt + '" loading="lazy">' +
                    '</div>' +
                    '<h6 class="product-title">' + (p.name || '') + '</h6>' +
                    '<div class="mb-2">' + priceHtml + '</div>' +
                    '</a>' +
                    '<a href="' + p.url + '" class="btn btn-outline-primary btn-sm">Подробнее</a>' +
                    '</div></div>';
            });
            html += '</div>';
            var inner = container.querySelector('.viewed-products-inner');
            if (inner) inner.innerHTML = html;
            container.style.display = 'block';
        }).catch(function() {
            container.style.display = 'none';
        });
    }

    window.viewedRender = renderViewed;
})();
