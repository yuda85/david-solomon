/* ==========================================================================
   דוד סולומון — התנהגות האתר
   ========================================================================== */
(function () {
  'use strict';

  var CFG = window.SITE_CONFIG || {};
  var PHONE_INTL = '972523931661';
  var FORM_ENDPOINT = 'https://formsubmit.co/ajax/david.solo0050@gmail.com';

  var TOPICS = {
    trauma: 'טראומה ופוסט־טראומה',
    reserves: 'חזרה ממילואים',
    couples: 'זוגיות ומשפחה',
    parenting: 'הורות',
    organizations: 'ארגונים וחוסן',
    general: 'כללי'
  };

  var ICON_PLAY = '<svg class="icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.14v13.72a1 1 0 0 0 1.5.86l11-6.86a1 1 0 0 0 0-1.72l-11-6.86A1 1 0 0 0 8 5.14Z"/></svg>';

  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function waLink(text) {
    return 'https://wa.me/' + PHONE_INTL + (text ? '?text=' + encodeURIComponent(text) : '');
  }
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  window.__siteReady = true;

  /* ---------- Header state ---------- */
  var header = $('.site-header');
  function onScroll() { if (header) header.classList.toggle('is-scrolled', window.scrollY > 8); }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---------- Mobile navigation ---------- */
  var toggle = $('.menu-toggle');
  var nav = $('#site-nav');
  if (toggle && nav) {
    var setOpen = function (open) {
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'סגירת התפריט' : 'פתיחת התפריט');
      nav.classList.toggle('is-open', open);
      document.body.classList.toggle('nav-open', open);
    };
    toggle.addEventListener('click', function () {
      setOpen(toggle.getAttribute('aria-expanded') !== 'true');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) { setOpen(false); toggle.focus(); }
    });
    $$('a', nav).forEach(function (a) { a.addEventListener('click', function () { setOpen(false); }); });
    var mq = window.matchMedia('(min-width: 1180px)');
    var onMq = function (e) { if (e.matches) setOpen(false); };
    if (mq.addEventListener) mq.addEventListener('change', onMq); else if (mq.addListener) mq.addListener(onMq);
  }

  /* ---------- Reveal on scroll ---------- */
  var revealEls = $$('.reveal');
  if (revealEls.length) {
    // ?static — show everything immediately, without animation (useful for screenshots / printing)
    var isStatic = /[?&]static\b/.test(window.location.search);
    if (isStatic) document.documentElement.classList.add('no-reveal');
    if (!('IntersectionObserver' in window) || reduceMotion || isStatic) {
      revealEls.forEach(function (el) { el.classList.add('is-visible'); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) { entry.target.classList.add('is-visible'); io.unobserve(entry.target); }
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
      revealEls.forEach(function (el) { io.observe(el); });
    }
  }

  /* ---------- Year ---------- */
  $$('[data-year]').forEach(function (el) { el.textContent = String(new Date().getFullYear()); });

  /* ---------- Social links (from site-config.js) ---------- */
  var social = CFG.social || {};
  $$('[data-social]').forEach(function (a) {
    var url = social[a.getAttribute('data-social')];
    if (url) { a.href = url; a.hidden = false; }
  });
  $$('[data-social-group]').forEach(function (group) {
    var any = $$('[data-social]', group).some(function (a) { return !a.hidden; });
    group.hidden = !any;
  });
  var anySocial = Object.keys(social).some(function (k) { return !!social[k]; });
  $$('[data-social-empty]').forEach(function (el) { el.hidden = anySocial; });

  /* ---------- Videos (lite YouTube embeds) ---------- */
  var videos = (CFG.videos || []).filter(function (v) { return v && v.id; });

  function videoCard(v) {
    var art = document.createElement('article');
    art.className = 'video-card';
    art.setAttribute('data-topics', (v.topics || []).join(' '));
    var topicNames = (v.topics || []).map(function (t) { return TOPICS[t] || t; }).join(' · ');
    var meta = [v.kind, topicNames].filter(Boolean).join(' · ');
    art.innerHTML =
      '<div class="yt">' +
        '<button class="yt__btn" type="button" aria-label="ניגון: ' + esc(v.title) + '">' +
          '<img src="https://i.ytimg.com/vi/' + encodeURIComponent(v.id) + '/hqdefault.jpg" alt="" loading="lazy" width="480" height="360">' +
          '<span class="yt__play">' + ICON_PLAY + '</span>' +
        '</button>' +
      '</div>' +
      '<h3 class="video-card__title">' + esc(v.title) + '</h3>' +
      (meta ? '<p class="video-card__meta">' + esc(meta) + '</p>' : '');
    $('.yt__btn', art).addEventListener('click', function () {
      var frame = document.createElement('iframe');
      frame.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(v.id) + '?autoplay=1&rel=0';
      frame.title = v.title || 'סרטון';
      frame.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
      frame.allowFullscreen = true;
      var box = $('.yt', art);
      box.innerHTML = '';
      box.appendChild(frame);
      frame.focus();
    });
    return art;
  }

  $$('[data-videos]').forEach(function (wrap) {
    var want = (wrap.getAttribute('data-videos') || '').split(/\s+/).filter(Boolean);
    var isAll = want.indexOf('all') !== -1;
    var list = isAll ? videos : videos.filter(function (v) {
      return (v.topics || []).some(function (t) { return want.indexOf(t) !== -1; });
    });
    var grid = $('.video-grid', wrap);
    var empty = $('.empty-state', wrap);

    if (!list.length) {
      if (empty) empty.hidden = false;
      if (!isAll) wrap.hidden = true;
      return;
    }
    wrap.hidden = false;
    if (empty) empty.hidden = true;
    list.forEach(function (v) { grid.appendChild(videoCard(v)); });

    // Filters (content page)
    var filters = $('.video-filters', wrap);
    if (isAll && filters) {
      var used = [];
      list.forEach(function (v) { (v.topics || []).forEach(function (t) { if (used.indexOf(t) === -1) used.push(t); }); });
      if (used.length > 1) {
        var chips = $('.chips', filters);
        var mk = function (key, label) {
          var b = document.createElement('button');
          b.type = 'button';
          b.className = 'chip';
          b.textContent = label;
          b.setAttribute('aria-pressed', key === 'all' ? 'true' : 'false');
          b.addEventListener('click', function () {
            $$('.chip', chips).forEach(function (c) { c.setAttribute('aria-pressed', 'false'); });
            b.setAttribute('aria-pressed', 'true');
            $$('.video-card', grid).forEach(function (card) {
              var t = (card.getAttribute('data-topics') || '').split(' ');
              card.hidden = key !== 'all' && t.indexOf(key) === -1;
            });
          });
          chips.appendChild(b);
        };
        mk('all', 'הכול');
        used.forEach(function (t) { mk(t, TOPICS[t] || t); });
        filters.hidden = false;
      }
    }
  });

  /* ---------- Tabs ---------- */
  var tabApi = {};
  $$('[data-tabs]').forEach(function (wrap) {
    var tabs = $$('[role="tab"]', wrap);
    var activate = function (key, focus) {
      tabs.forEach(function (t) {
        var on = t.getAttribute('data-tab') === key;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        var panel = document.getElementById(t.getAttribute('aria-controls'));
        if (panel) panel.hidden = !on;
        if (on && focus) t.focus();
      });
    };
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { activate(t.getAttribute('data-tab')); });
      t.addEventListener('keydown', function (e) {
        var dir = 0;
        // RTL: left arrow moves forward
        if (e.key === 'ArrowLeft') dir = 1;
        if (e.key === 'ArrowRight') dir = -1;
        if (!dir) return;
        e.preventDefault();
        var next = tabs[(i + dir + tabs.length) % tabs.length];
        activate(next.getAttribute('data-tab'), true);
      });
    });
    tabApi.activate = activate;
  });

  /* ---------- Preselect from URL (?type=org&sector=business&topic=trauma&timing=year) ---------- */
  var params = new URLSearchParams(window.location.search);
  if (params.get('type') === 'org' && tabApi.activate) tabApi.activate('org');
  function preselect(selectId, key) {
    var sel = document.getElementById(selectId);
    if (!sel || !key) return;
    $$('option', sel).forEach(function (o) { if (o.getAttribute('data-key') === key) sel.value = o.value; });
  }
  preselect('t-topic', params.get('topic'));
  preselect('o-sector', params.get('sector'));
  preselect('o-timing', params.get('timing'));

  /* ---------- Forms (FormSubmit AJAX + WhatsApp fallback) ---------- */
  function labelFor(form, name) {
    var el = form.querySelector('[name="' + name + '"]');
    var holder = el && el.closest('[data-label]');
    return holder ? holder.getAttribute('data-label') : name;
  }

  function errorText(el) {
    var v = el.validity;
    if (v.valid) return '';
    if (v.valueMissing) return el.getAttribute('data-msg-required') || 'השדה הזה חסר';
    if (v.typeMismatch && el.type === 'email') return 'נראה שכתובת המייל לא שלמה';
    if (v.patternMismatch || v.tooShort) return el.getAttribute('data-msg-pattern') || 'נראה שהערך לא שלם';
    return 'כדאי לבדוק שוב את השדה הזה';
  }

  function validateField(el) {
    var field = el.closest('.field');
    var err = field && $('.field__error', field);
    var msg = errorText(el);
    if (field) field.classList.toggle('is-invalid', !!msg);
    el.setAttribute('aria-invalid', msg ? 'true' : 'false');
    if (err) { err.textContent = msg; err.hidden = !msg; }
    return !msg;
  }

  $$('form[data-form]').forEach(function (form) {
    var btn = $('button[type="submit"]', form);
    var status = $('.form-status', form);
    var success = form.parentNode.querySelector('.form-success');
    var subject = form.getAttribute('data-subject') || 'פנייה חדשה מהאתר';
    var fields = $$('input, select, textarea', form).filter(function (el) {
      return el.name && el.name.charAt(0) !== '_' && el.type !== 'hidden' && (el.required || el.pattern || el.type === 'email');
    });

    fields.forEach(function (el) {
      el.addEventListener('blur', function () { if (el.value || el.getAttribute('data-touched')) { el.setAttribute('data-touched', '1'); validateField(el); } });
      el.addEventListener('input', function () { var f = el.closest('.field'); if (f && f.classList.contains('is-invalid')) validateField(el); });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (form._honey && form._honey.value) return;

      var firstBad = null;
      fields.forEach(function (el) { if (!validateField(el) && !firstBad) firstBad = el; });
      if (firstBad) { firstBad.focus(); return; }

      var fd = new FormData(form);
      var payload = {};
      var lines = [];
      fd.forEach(function (value, name) {
        if (name.charAt(0) === '_') return;
        value = String(value).trim();
        if (!value) return;
        var label = labelFor(form, name);
        payload[label] = value;
        lines.push(label + ': ' + value);
      });
      payload._subject = subject;
      payload._template = 'table';
      payload._captcha = 'false';

      if (status) { status.hidden = true; status.className = 'form-status'; status.innerHTML = ''; }
      btn.classList.add('is-loading');
      btn.disabled = true;

      fetch(FORM_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(function (res) { return res.json().catch(function () { return {}; }).then(function (j) { return { ok: res.ok, json: j }; }); })
        .then(function (r) {
          if (!(r.ok && String(r.json.success) === 'true')) throw new Error(r.json.message || 'send failed');
          form.hidden = true;
          if (success) { success.hidden = false; success.focus(); }
        })
        .catch(function () {
          var text = 'שלום דוד, ניסיתי להשאיר פרטים באתר:\n' + lines.join('\n');
          if (status) {
            status.className = 'form-status is-error';
            status.innerHTML =
              'משהו השתבש בשליחה, והפנייה לא נקלטה. אפשר לשלוח את אותם פרטים בוואטסאפ בלחיצה אחת, או להתקשר ל־<a href="tel:+972523931661" class="ltr">052-3931661</a>.' +
              '<br><a class="btn btn--wa btn--sm" target="_blank" rel="noopener" href="' + esc(waLink(text)) + '">שליחה בוואטסאפ</a>';
            status.hidden = false;
            status.setAttribute('tabindex', '-1');
            status.focus();
          }
        })
        .then(function () {
          btn.classList.remove('is-loading');
          btn.disabled = false;
        });
    });
  });
})();
