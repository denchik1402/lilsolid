(function () {
    function csrf() {
        var m = document.querySelector('meta[name="csrf-token"]');
        return m ? m.getAttribute('content') : '';
    }

    document.addEventListener('click', function (e) {
        var btn = e.target.closest('.quick-view-btn');
        if (!btn) return;
        e.preventDefault();
        e.stopPropagation();
        var id = btn.getAttribute('data-product-id');
        var modalEl = document.getElementById('quickViewModal');
        if (!modalEl || !id) return;
        var body = document.getElementById('quickViewBody');
        var title = document.getElementById('quickViewTitle');
        body.innerHTML = '<div class="text-center p-4">Загрузка…</div>';
        var modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
        fetch('/api/product/' + id)
            .then(function (r) { return r.json(); })
            .then(function (d) {
                if (d.error) throw new Error(d.error);
                title.textContent = d.name;
                var oldP = d.old_price_fmt ? '<span class="text-muted text-decoration-line-through ms-2">' + d.old_price_fmt + ' ₽</span>' : '';
                var disc = d.discount_pct ? '<span class="badge bg-danger ms-2">−' + d.discount_pct + '%</span>' : '';
                body.innerHTML =
                    '<div class="row g-3">' +
                    '<div class="col-md-5 text-center"><img src="' + d.image_url + '" alt="" class="img-fluid" onerror="this.src=\'' + (d.image_fallback || '') + '\'"></div>' +
                    '<div class="col-md-7">' +
                    '<h4>' + d.name + '</h4>' +
                    '<p class="fs-5 fw-bold">' + d.price_fmt + ' ₽' + oldP + disc + '</p>' +
                    '<div class="d-flex flex-wrap gap-2 mt-3">' +
                    '<a href="' + d.url + '" class="btn btn-primary">Подробнее</a>' +
                    '<button type="button" class="btn btn-outline-primary one-click-trigger" data-product-id="' + d.id + '" data-product-name="' + d.name.replace(/"/g, '&quot;') + '">1 клик</button>' +
                    '</div></div></div>';
            })
            .catch(function () {
                body.innerHTML = '<p class="text-danger">Не удалось загрузить товар</p>';
            });
    });

    document.addEventListener('click', function (e) {
        var btn = e.target.closest('.one-click-trigger');
        if (!btn) return;
        e.preventDefault();
        var id = btn.getAttribute('data-product-id');
        var name = btn.getAttribute('data-product-name') || '';
        document.getElementById('oneClickProductId').value = id;
        document.getElementById('oneClickProductName').textContent = name;
        document.getElementById('oneClickError').classList.add('d-none');
        var qv = document.getElementById('quickViewModal');
        if (qv) {
            var inst = bootstrap.Modal.getInstance(qv);
            if (inst) inst.hide();
        }
        bootstrap.Modal.getOrCreateInstance(document.getElementById('oneClickModal')).show();
    });

    var oneClickForm = document.getElementById('oneClickForm');
    if (oneClickForm) {
        oneClickForm.addEventListener('submit', function (e) {
            e.preventDefault();
            var err = document.getElementById('oneClickError');
            err.classList.add('d-none');
            var fd = new FormData(oneClickForm);
            var payload = { product_id: fd.get('product_id'), name: fd.get('name'), phone: fd.get('phone') };
            fetch('/api/one-click-order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() },
                body: JSON.stringify(payload)
            })
                .then(function (r) { return r.json(); })
                .then(function (d) {
                    if (d.success && d.redirect) window.location.href = d.redirect;
                    else throw new Error(d.error || 'Ошибка');
                })
                .catch(function (ex) {
                    err.textContent = ex.message || 'Ошибка отправки';
                    err.classList.remove('d-none');
                });
        });
    }
})();
