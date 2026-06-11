(function() {
    var DEBOUNCE_MS = 200;
    var MIN_LENGTH = 2;
    var timer = null;
    var lastQuery = '';
    var lastAbort = null;

    function init() {
        var form = document.getElementById('headerSearchForm');
        if (!form) return;
        var input = form.querySelector('input[name="q"]');
        if (!input) return;

        var wrap = document.createElement('div');
        wrap.className = 'search-suggestions-wrap position-relative d-flex';
        form.parentNode.insertBefore(wrap, form);
        wrap.appendChild(form);

        var dropdown = document.createElement('div');
        dropdown.className = 'search-suggestions-dropdown';
        dropdown.id = 'searchSuggestionsDropdown';
        dropdown.setAttribute('role', 'listbox');
        dropdown.style.display = 'none';
        wrap.appendChild(dropdown);

        input.setAttribute('autocomplete', 'off');
        input.setAttribute('aria-autocomplete', 'list');
        input.setAttribute('aria-controls', 'searchSuggestionsDropdown');
        input.setAttribute('aria-expanded', 'false');

        function hide() {
            dropdown.style.display = 'none';
            dropdown.innerHTML = '';
            input.setAttribute('aria-expanded', 'false');
        }

        function show(items) {
            if (!items || items.length === 0) {
                hide();
                return;
            }
            dropdown.innerHTML = items.map(function(item, i) {
                var price = item.price ? ' — ' + Number(item.price).toLocaleString('ru-RU') + ' ₽' : '';
                return '<a href="' + escapeHtml(item.url) + '" class="search-suggestion-item" role="option" data-index="' + i + '">' +
                    '<span class="suggestion-name">' + escapeHtml(item.name) + '</span>' +
                    (price ? '<span class="suggestion-price text-muted">' + price + '</span>' : '') +
                    '</a>';
            }).join('');
            dropdown.style.display = 'block';
            input.setAttribute('aria-expanded', 'true');
        }

        function escapeHtml(s) {
            var div = document.createElement('div');
            div.textContent = s;
            return div.innerHTML;
        }

        function fetchSuggestions(query, callback) {
            if (lastAbort) lastAbort.abort();
            var controller = new AbortController();
            lastAbort = controller;
            fetch('/api/search-suggestions?q=' + encodeURIComponent(query), { signal: controller.signal })
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    lastAbort = null;
                    callback(data.suggestions || []);
                })
                .catch(function(err) {
                    if (err.name !== 'AbortError') lastAbort = null;
                    callback([]);
                });
        }

        function onInput() {
            var q = (input.value || '').trim();
            if (q.length < MIN_LENGTH) {
                hide();
                return;
            }
            if (q === lastQuery) return;
            lastQuery = q;

            clearTimeout(timer);
            timer = setTimeout(function() {
                fetchSuggestions(q, function(suggestions) {
                    if ((input.value || '').trim() === q) {
                        show(suggestions);
                    }
                });
            }, DEBOUNCE_MS);
        }

        input.addEventListener('input', onInput);
        input.addEventListener('focus', function() {
            if (lastQuery && lastQuery.length >= MIN_LENGTH && dropdown.innerHTML) {
                dropdown.style.display = 'block';
            }
        });
        input.addEventListener('blur', function() {
            setTimeout(hide, 150);
        });
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                hide();
                input.blur();
            }
        });

        dropdown.addEventListener('mousedown', function(e) {
            e.preventDefault();
        });

        document.addEventListener('click', function(e) {
            if (!wrap.contains(e.target)) hide();
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
