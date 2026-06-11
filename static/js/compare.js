(function() {
    var KEY = 'lil_compare';
    var MAX = 4;

    function getIds() {
        try {
            var s = localStorage.getItem(KEY);
            return s ? JSON.parse(s) : [];
        } catch (e) { return []; }
    }

    function setIds(ids) {
        ids = ids.slice(0, MAX);
        localStorage.setItem(KEY, JSON.stringify(ids));
        updateBadge();
    }

    function updateBadge() {
        var n = getIds().length;
        var el = document.getElementById('compareCount');
        if (el) {
            el.textContent = n;
            el.style.display = n > 0 ? 'inline' : 'none';
        }
    }

    window.compareAdd = function(id) {
        var ids = getIds();
        var numId = Number(id);
        if (ids.indexOf(numId) === -1) {
            if (ids.length >= MAX) {
                ids.shift();
            }
            ids.push(numId);
            setIds(ids);
        }
    };

    window.compareRemove = function(id) {
        var numId = Number(id);
        var ids = getIds().filter(function(x) { return Number(x) !== numId; });
        setIds(ids);
    };

    window.compareToggle = function(id) {
        var ids = getIds();
        var numId = Number(id);
        var i = ids.indexOf(numId);
        if (i === -1) {
            if (ids.length >= MAX) ids.shift();
            ids.push(numId);
        } else {
            ids.splice(i, 1);
        }
        setIds(ids);
        return ids.indexOf(numId) !== -1;
    };

    window.compareHas = function(id) {
        return getIds().indexOf(Number(id)) !== -1;
    };

    window.compareGetIds = getIds;

    function initCompareButtons() {
        updateBadge();
        document.querySelectorAll('.compare-btn').forEach(function(btn) {
            if (btn.classList.contains('compare-btn-remove')) return;
            var id = parseInt(btn.dataset.productId, 10);
            if (isNaN(id)) return;
            btn.classList.toggle('active', compareHas(id));
            btn.title = btn.classList.contains('active') ? 'Убрать из сравнения' : 'Добавить в сравнение';
            btn.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                var nowActive = compareToggle(id);
                btn.classList.toggle('active', nowActive);
                btn.title = nowActive ? 'Убрать из сравнения' : 'Добавить в сравнение';
            };
        });
    }

    document.addEventListener('DOMContentLoaded', initCompareButtons);
})();
