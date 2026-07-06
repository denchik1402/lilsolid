(function () {
    function setMainProductImage(src) {
        var main = document.getElementById('productMainImage');
        if (!main || !src) return;
        var picture = main.closest('picture');
        if (picture) {
            picture.querySelectorAll('source').forEach(function (source) {
                source.remove();
            });
        }
        main.removeAttribute('srcset');
        main.removeAttribute('sizes');
        main.src = src;
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('.product-thumb').forEach(function (thumb) {
            thumb.addEventListener('click', function () {
                var src = this.getAttribute('data-src');
                if (!src) return;
                setMainProductImage(src);
                document.querySelectorAll('.product-thumb').forEach(function (t) {
                    t.classList.remove('active');
                });
                this.classList.add('active');
            });
        });
    });
})();
