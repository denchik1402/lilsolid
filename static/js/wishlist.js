(function() {
    var KEY = 'lil_wishlist';
    function getIds() {
        try {
            var s = localStorage.getItem(KEY);
            return s ? JSON.parse(s) : [];
        } catch (e) { return []; }
    }
    function setIds(ids) {
        localStorage.setItem(KEY, JSON.stringify(ids));
        updateBadge();
    }
    function updateBadge() {
        var n = getIds().length;
        var el = document.getElementById('wishlistCount');
        if (el) {
            el.textContent = n;
            el.style.display = n > 0 ? 'inline' : 'none';
        }
    }
    window.wishlistAdd = function(id) {
        var ids = getIds();
        if (ids.indexOf(id) === -1) {
            ids.push(id);
            setIds(ids);
        }
    };
    window.wishlistRemove = function(id) {
        var numId = Number(id);
        var ids = getIds().filter(function(x) { return Number(x) !== numId; });
        setIds(ids);
    };
    window.wishlistToggle = function(id) {
        var ids = getIds();
        var i = ids.indexOf(id);
        if (i === -1) {
            ids.push(id);
        } else {
            ids.splice(i, 1);
        }
        setIds(ids);
        return ids.indexOf(id) !== -1;
    };
    window.wishlistHas = function(id) {
        return getIds().indexOf(id) !== -1;
    };
    window.wishlistGetIds = getIds;
    function initFavoriteButtons() {
        updateBadge();
        document.querySelectorAll('.favorite-btn').forEach(function(btn) {
            if (btn.classList.contains('favorite-btn-remove')) return;
            var id = parseInt(btn.dataset.productId, 10);
            if (isNaN(id)) return;
            btn.classList.toggle('active', getIds().indexOf(id) !== -1);
            btn.title = btn.classList.contains('active') ? 'Убрать из избранного' : 'Добавить в избранное';
            btn.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                var nowActive = wishlistToggle(id);
                btn.classList.toggle('active', nowActive);
                btn.title = nowActive ? 'Убрать из избранного' : 'Добавить в избранное';
            };
        });
    }
    document.addEventListener('DOMContentLoaded', initFavoriteButtons);
})();
