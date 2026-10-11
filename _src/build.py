#!/usr/bin/env python3
"""
בונה את קבצי ה-HTML של האתר מתוך _src/pages.

למה? כדי שהתפריט, הכותרת התחתונה והטפסים יהיו זהים בכל העמודים
בלי להעתיק אותם ידנית. התוצר הוא HTML רגיל לגמרי — אין צורך בשום כלי בשרת.

הרצה (מתיקיית השורש של האתר):
    python _src/build.py

מבנה קובץ עמוד ב-_src/pages:
    <!--
    out: about/index.html
    key: about
    title: כותרת לחלון הדפדפן
    description: תיאור לגוגל ולשיתוף
    -->
    ...HTML של גוף העמוד...

תגיות שאפשר להשתמש בהן בתוך העמודים:
    {{root}}               נתיב יחסי לשורש האתר (עובד גם בכתובת github.io/שם-הריפו/)
    {{icon:phone}}         אייקון SVG
    {{wa}} / {{wa:טקסט}}   קישור וואטסאפ (עם הודעה מוכנה)
    {{tel}} {{phone}} {{email}} {{mailto}} {{maps}}
    {{form:therapy}} {{form:org}}
    {{contactlist}}  {{hotlines}}
    {{cta}} / {{cta:org}}
    {{videos:trauma reserves}}   אזור סרטונים לפי נושא (מתמלא מ-assets/js/site-config.js)
"""
import html
import os
import re
import sys
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES_DIR = os.path.join(ROOT, "_src", "pages")

# אם יש דומיין קבוע (למשל https://davidsolomon.co.il) — כתבו אותו כאן והריצו שוב.
# זה משפר את התצוגה המקדימה כשמשתפים קישור בוואטסאפ / פייסבוק.
SITE_URL = ""

ASSET_VERSION = "1"

PHONE_DISPLAY = "052-3931661"
PHONE_INTL = "972523931661"
EMAIL = "david.solo0050@gmail.com"
WA_DEFAULT = "שלום דוד, הגעתי מהאתר ואשמח לדבר"
MAPS_URL = "https://www.google.com/maps/search/?api=1&query=" + quote("מושב שדה יעקב")

NAV = [
    ("about", "אודות", "about/"),
    ("therapy", "טיפול וקליניקה", "therapy/"),
    ("trauma", "פוסט־טראומה", "trauma/"),
    ("lectures", "הרצאות וסדנאות", "lectures/"),
    ("organizations", "ארגונים ומסגרות", "organizations/"),
    ("content", "תוכן ופודקאסטים", "content/"),
    ("contact", "יצירת קשר", "contact/"),
]

# ---------------------------------------------------------------------------
# Icons (Lucide-style, 24x24, stroke)
# ---------------------------------------------------------------------------
ICONS = {
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "map-pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "arrow": '<path d="M19 12H5"/><path d="m12 19-7-7 7-7"/>',
    "chevron-down": '<path d="m6 9 6 6 6-6"/>',
    "user": '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "heart-hands": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M12 5 9.04 7.96a2.17 2.17 0 0 0 0 3.08c.82.82 2.13.85 3 .07l2.07-1.9a2.82 2.82 0 0 1 3.79 0l2.96 2.66"/><path d="m18 15-2-2"/><path d="m15 18-2-2"/>',
    "sprout": '<path d="M7 20h10"/><path d="M10 20c5.5-2.5.8-6.4 3-10"/><path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z"/><path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "life-buoy": '<circle cx="12" cy="12" r="10"/><path d="m4.93 4.93 4.24 4.24"/><path d="m14.83 9.17 4.24-4.24"/><path d="m14.83 14.83 4.24 4.24"/><path d="m9.17 14.83-4.24 4.24"/><circle cx="12" cy="12" r="4"/>',
    "mic": '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><path d="M12 19v3"/>',
    "tv": '<rect width="20" height="15" x="2" y="7" rx="2" ry="2"/><path d="m17 2-5 5-5-5"/>',
    "building": '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/>',
    "landmark": '<path d="M3 22h18"/><path d="M6 18v-7"/><path d="M10 18v-7"/><path d="M14 18v-7"/><path d="M18 18v-7"/><path d="m12 2 8 5H4z"/>',
    "school": '<path d="M22 10 12 5 2 10l10 5 10-5Z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/><path d="M22 10v6"/>',
    "home": '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
    "calendar": '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/><path d="m9 16 2 2 4-4"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "check-circle": '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    "menu": '<path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/>',
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "laptop": '<path d="M20 16V7a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v9m16 0H4m16 0 1.28 2.55a1 1 0 0 1-.9 1.45H3.62a1 1 0 0 1-.9-1.45L4 16"/>',
    "message": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
    "wind": '<path d="M17.7 7.7a2.5 2.5 0 1 1 1.8 4.3H2"/><path d="M9.6 4.6A2 2 0 1 1 11 8H2"/><path d="M12.6 19.4A2 2 0 1 0 14 16H2"/>',
    "presentation": '<path d="M2 3h20"/><path d="M21 3v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V3"/><path d="m7 21 5-5 5 5"/>',
    "route": '<circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/>',
    "compass": '<circle cx="12" cy="12" r="10"/><path d="m16.24 7.76-1.804 5.411a2 2 0 0 1-1.265 1.265L7.76 16.24l1.804-5.411a2 2 0 0 1 1.265-1.265z"/>',
    "lock": '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "send": '<path d="M14.54 21.69a.5.5 0 0 0 .94-.03l6.5-19a.5.5 0 0 0-.64-.64l-19 6.5a.5.5 0 0 0-.03.94l7.93 3.18a2 2 0 0 1 1.11 1.11z"/><path d="m21.85 2.15-10.94 10.94"/>',
    "play-circle": '<circle cx="12" cy="12" r="10"/><path d="m10 8 6 4-6 4Z"/>',
    "quote": '<path d="M16 3a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2 1 1 0 0 1 1 1v1a2 2 0 0 1-2 2 1 1 0 0 0-1 1v2a1 1 0 0 0 1 1 6 6 0 0 0 6-6V5a2 2 0 0 0-2-2z"/><path d="M5 3a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2 1 1 0 0 1 1 1v1a2 2 0 0 1-2 2 1 1 0 0 0-1 1v2a1 1 0 0 0 1 1 6 6 0 0 0 6-6V5a2 2 0 0 0-2-2z"/>',
    "youtube": '<path d="M2.5 17a24.12 24.12 0 0 1 0-10 2 2 0 0 1 1.4-1.4 49.56 49.56 0 0 1 16.2 0A2 2 0 0 1 21.5 7a24.12 24.12 0 0 1 0 10 2 2 0 0 1-1.4 1.4 49.55 49.55 0 0 1-16.2 0A2 2 0 0 1 2.5 17"/><path d="m10 15 5-3-5-3z"/>',
    "instagram": '<rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><path d="M17.5 6.5h.01"/>',
    "facebook": '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "horse": '<path d="M7 21v-4.5c0-1.5-1-2.5-1-4.5 0-3.5 2.5-6 6-7l1-2.5 1.5 2.5c2 .5 3.5 2 4.5 4l1.5 3.5-2 1.5-2.5-1.5-1 2v6.5"/><path d="M11 21v-4"/><path d="M14.5 8.5h.01"/>',
}

WHATSAPP_PATH = ('<path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z"/>')


def icon(name, cls=""):
    klass = "icon" + (" " + cls if cls else "")
    if name == "whatsapp":
        return f'<svg class="{klass}" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false">{WHATSAPP_PATH}</svg>'
    if name not in ICONS:
        raise KeyError(f"unknown icon: {name}")
    return (f'<svg class="{klass}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{ICONS[name]}</svg>')


BRAND_MARK = ('<svg class="brand__mark" viewBox="0 0 44 44" aria-hidden="true" focusable="false">'
              '<path d="M10 38V20a12 12 0 0 1 24 0v18" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>'
              '<path d="M5 38h34" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>'
              '<circle cx="22" cy="24" r="3.4" fill="#A5512D"/></svg>')


def wa(text=None):
    return f"https://wa.me/{PHONE_INTL}?text=" + quote(text or WA_DEFAULT)


# ---------------------------------------------------------------------------
# Shared components
# ---------------------------------------------------------------------------
def contact_list():
    return f"""<ul class="contact-list">
  <li><a class="contact-item contact-item--wa" href="{wa()}" target="_blank" rel="noopener">
    <span class="contact-item__icon">{icon("whatsapp")}</span>
    <span><span class="contact-item__label">הכי מהיר</span><span class="contact-item__value">כתבו לי בוואטסאפ</span></span>
    {icon("arrow")}</a></li>
  <li><a class="contact-item contact-item--call" href="tel:+{PHONE_INTL}">
    <span class="contact-item__icon">{icon("phone")}</span>
    <span><span class="contact-item__label">שיחת טלפון</span><span class="contact-item__value ltr">{PHONE_DISPLAY}</span></span>
    {icon("arrow")}</a></li>
  <li><a class="contact-item" href="mailto:{EMAIL}">
    <span class="contact-item__icon">{icon("mail")}</span>
    <span><span class="contact-item__label">מייל</span><span class="contact-item__value ltr">{EMAIL}</span></span>
    {icon("arrow")}</a></li>
  <li><a class="contact-item" href="{MAPS_URL}" target="_blank" rel="noopener">
    <span class="contact-item__icon">{icon("map-pin")}</span>
    <span><span class="contact-item__label">הקליניקה</span><span class="contact-item__value">מושב שדה יעקב · וגם אונליין</span></span>
    {icon("arrow")}</a></li>
</ul>"""


def hotlines():
    return f"""<div class="note note--olive hotlines" role="note">
  {icon("life-buoy")}
  <p><strong>במצוקה עכשיו?</strong> אם אתם או מישהו קרוב אליכם נמצאים במצוקה חריפה, אל תחכו.
  ער״ן: <a href="tel:1201">1201</a> · נט״ל, קו סיוע לנפגעי טראומה: <a href="tel:1800363363" class="ltr">1-800-363-363</a> · במצב חירום: מד״א <a href="tel:101">101</a></p>
</div>"""


def field_error():
    return f'<span class="field__error" hidden></span>'


def form_therapy(root):
    return f"""<div class="form-wrap">
<form class="form" data-form="therapy" data-subject="פנייה חדשה לטיפול — מהאתר" novalidate>
  <div class="form-grid form-grid--2">
    <div class="field" data-label="שם">
      <label for="t-name">איך לפנות אליכם?<span class="req" aria-hidden="true">*</span></label>
      <input id="t-name" name="name" type="text" autocomplete="name" required data-msg-required="נשמח לדעת איך לפנות אליכם" aria-describedby="t-name-err">
      <span class="field__error" id="t-name-err" hidden></span>
    </div>
    <div class="field" data-label="טלפון">
      <label for="t-phone">טלפון<span class="req" aria-hidden="true">*</span></label>
      <input id="t-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" required pattern="[\\d\\s\\+\\-\\(\\)]{{9,}}" data-msg-required="צריך מספר טלפון כדי שאוכל לחזור אליכם" data-msg-pattern="נראה שמספר הטלפון לא שלם" aria-describedby="t-phone-err">
      <span class="field__error" id="t-phone-err" hidden></span>
    </div>
    <div class="field field--full" data-label="נושא">
      <label for="t-topic">במה מדובר? <span class="optional">(לא חובה)</span></label>
      <select id="t-topic" name="topic">
        <option value="עוד לא בטוח/ה" data-key="unsure">עוד לא בטוח/ה</option>
        <option value="טראומה ופוסט־טראומה" data-key="trauma">טראומה ופוסט־טראומה</option>
        <option value="טיפול פרטני (מבוגרים / מתבגרים)" data-key="individual">טיפול פרטני (מבוגרים / מתבגרים)</option>
        <option value="טיפול זוגי או משפחתי" data-key="couples">טיפול זוגי או משפחתי</option>
        <option value="הדרכת הורים" data-key="parents">הדרכת הורים וליווי משפחה</option>
        <option value="חרדה, משבר או תקופת שינוי" data-key="anxiety">חרדה, משבר או תקופת שינוי</option>
        <option value="חזרה ממילואים" data-key="reserves">חזרה ממילואים</option>
      </select>
    </div>
    <fieldset class="field field--full" data-label="מעדיפים להיפגש">
      <legend>איפה נוח לכם להיפגש?</legend>
      <div class="choice-group">
        <label class="choice"><input type="radio" name="format" value="בקליניקה בשדה יעקב"><span>בקליניקה בשדה יעקב</span></label>
        <label class="choice"><input type="radio" name="format" value="אונליין"><span>אונליין</span></label>
        <label class="choice"><input type="radio" name="format" value="עוד לא יודע/ת" checked><span>עוד לא יודע/ת</span></label>
      </div>
    </fieldset>
    <fieldset class="field field--full" data-label="איך לחזור">
      <legend>איך נוח שאחזור אליכם?</legend>
      <div class="choice-group">
        <label class="choice"><input type="radio" name="reply" value="שיחת טלפון" checked><span>שיחת טלפון</span></label>
        <label class="choice"><input type="radio" name="reply" value="וואטסאפ"><span>וואטסאפ</span></label>
      </div>
    </fieldset>
    <div class="field field--full" data-label="הודעה">
      <label for="t-msg">רוצים לספר משהו? <span class="optional">(לא חובה)</span></label>
      <textarea id="t-msg" name="message" rows="4" aria-describedby="t-msg-help"></textarea>
      <span class="field__help" id="t-msg-help">אפשר גם להשאיר ריק. את השאר נדבר בשיחה.</span>
    </div>
  </div>
  <input class="hp" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true">
  <div class="form-foot">
    <button class="btn btn--primary btn--block" type="submit">{icon("send")}<span class="spinner" aria-hidden="true"></span>שלחו, ואחזור אליכם</button>
    <p class="form-privacy">{icon("lock")}הפנייה מגיעה ישירות אליי ונשמרת בדיסקרטיות מלאה.</p>
  </div>
  <div class="form-status" role="alert" hidden></div>
</form>
<div class="form-success" tabindex="-1" hidden>
  <div class="form-success__icon">{icon("check")}</div>
  <h3>תודה, הפנייה התקבלה.</h3>
  <p>אחזור אליכם בהקדם. אם זה דחוף, אפשר תמיד להתקשר: <a href="tel:+{PHONE_INTL}" class="ltr">{PHONE_DISPLAY}</a></p>
</div>
</div>"""


def form_org(root):
    return f"""<div class="form-wrap">
<form class="form" data-form="org" data-subject="פנייה מארגון — הרצאה / סדנה / פעילות" novalidate>
  <div class="form-grid form-grid--2">
    <div class="field" data-label="שם">
      <label for="o-name">שם מלא<span class="req" aria-hidden="true">*</span></label>
      <input id="o-name" name="name" type="text" autocomplete="name" required data-msg-required="נשמח לדעת עם מי מדברים" aria-describedby="o-name-err">
      <span class="field__error" id="o-name-err" hidden></span>
    </div>
    <div class="field" data-label="ארגון">
      <label for="o-org">ארגון / מסגרת<span class="req" aria-hidden="true">*</span></label>
      <input id="o-org" name="org" type="text" autocomplete="organization" required data-msg-required="איזה ארגון או מסגרת?" aria-describedby="o-org-err">
      <span class="field__error" id="o-org-err" hidden></span>
    </div>
    <div class="field" data-label="טלפון">
      <label for="o-phone">טלפון<span class="req" aria-hidden="true">*</span></label>
      <input id="o-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" required pattern="[\\d\\s\\+\\-\\(\\)]{{9,}}" data-msg-required="צריך מספר טלפון לחזרה" data-msg-pattern="נראה שמספר הטלפון לא שלם" aria-describedby="o-phone-err">
      <span class="field__error" id="o-phone-err" hidden></span>
    </div>
    <div class="field" data-label="מייל">
      <label for="o-email">מייל <span class="optional">(לא חובה)</span></label>
      <input id="o-email" name="email" type="email" autocomplete="email" aria-describedby="o-email-err">
      <span class="field__error" id="o-email-err" hidden></span>
    </div>
    <div class="field" data-label="תפקיד">
      <label for="o-role">תפקיד <span class="optional">(לא חובה)</span></label>
      <input id="o-role" name="role" type="text" autocomplete="organization-title" placeholder="למשל: מנהלת משאבי אנוש">
    </div>
    <div class="field" data-label="סוג הארגון">
      <label for="o-sector">סוג הארגון</label>
      <select id="o-sector" name="sector">
        <option value="חברה / ארגון עסקי" data-key="business">חברה / ארגון עסקי</option>
        <option value="גוף ממשלתי או ציבורי" data-key="gov">גוף ממשלתי או ציבורי</option>
        <option value="חינוך / רווחה" data-key="edu">חינוך / רווחה</option>
        <option value="קהילה / יישוב / קבוצה" data-key="community">קהילה / יישוב / קבוצה</option>
        <option value="אחר" data-key="other">אחר</option>
      </select>
    </div>
    <div class="field" data-label="סוג הפעילות">
      <label for="o-type">מה מעניין אתכם?</label>
      <select id="o-type" name="type">
        <option value="עוד לא בטוחים">עוד לא בטוחים — נחשוב יחד</option>
        <option value="הרצאה">הרצאה</option>
        <option value="סדנה">סדנה</option>
        <option value="סדרת מפגשים">סדרת מפגשים</option>
        <option value="תהליך מתמשך / ליווי">תהליך מתמשך / ליווי</option>
      </select>
    </div>
    <div class="field" data-label="מתי">
      <label for="o-timing">מתי בערך?</label>
      <select id="o-timing" name="timing">
        <option value="עוד לא נקבע" data-key="open">עוד לא נקבע</option>
        <option value="בחודש־חודשיים הקרובים" data-key="soon">בחודש־חודשיים הקרובים</option>
        <option value="בשנת העבודה הקרובה" data-key="year">בשנת העבודה הקרובה</option>
      </select>
    </div>
    <div class="field field--full" data-label="פרטים">
      <label for="o-msg">ספרו קצת על הקבוצה ועל הצורך <span class="optional">(לא חובה)</span></label>
      <textarea id="o-msg" name="message" rows="4" placeholder="מי הקהל, כמה משתתפים בערך, ומה חשוב לכם שיקרה במפגש"></textarea>
    </div>
  </div>
  <input class="hp" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true">
  <div class="form-foot">
    <button class="btn btn--primary btn--block" type="submit">{icon("send")}<span class="spinner" aria-hidden="true"></span>שלחו, ואחזור אליכם לתיאום</button>
    <p class="form-privacy">{icon("lock")}הפרטים מגיעים ישירות אליי ומשמשים רק לתיאום הפעילות.</p>
  </div>
  <div class="form-status" role="alert" hidden></div>
</form>
<div class="form-success" tabindex="-1" hidden>
  <div class="form-success__icon">{icon("check")}</div>
  <h3>תודה, קיבלתי.</h3>
  <p>אחזור אליכם בהקדם כדי לשמוע עוד ולהתחיל לבנות את הפעילות.</p>
</div>
</div>"""


def cta(root, kind=""):
    if kind == "org":
        return f"""<section class="section section--tight">
  <div class="container">
    <div class="cta-band cta-band--simple reveal">
      <p class="eyebrow">בונים פעילות יחד</p>
      <h2>ספרו לי מה קורה אצלכם, ונבנה את זה יחד.</h2>
      <p class="lead">שיחה קצרה מספיקה כדי להבין מי הקבוצה, מה הצורך ואיזה פורמט מתאים. משם בונים הרצאה, סדנה או תהליך.</p>
      <div class="btn-row">
        <a class="btn btn--light" href="{root}contact/?type=org#forms">{icon("calendar")}לתיאום פעילות לארגון</a>
        <a class="btn btn--ghost-light" href="{wa("שלום דוד, אני מארגון ואשמח לשמוע על הרצאה או סדנה")}" target="_blank" rel="noopener">{icon("whatsapp")}בוואטסאפ</a>
        <a class="btn btn--ghost-light" href="tel:+{PHONE_INTL}">{icon("phone")}<span class="ltr">{PHONE_DISPLAY}</span></a>
      </div>
    </div>
  </div>
</section>"""
    return f"""<section class="section section--tight">
  <div class="container">
    <div class="cta-band cta-band--simple reveal">
      <p class="eyebrow">אפשר להתחיל בשיחה</p>
      <h2>לא צריך לדעת בדיוק מה להגיד.</h2>
      <p class="lead">מספיקות כמה מילים: מה מביא אתכם, ואיך נוח שאחזור אליכם. משם נמשיך יחד.</p>
      <div class="btn-row">
        <a class="btn btn--wa" href="{wa()}" target="_blank" rel="noopener">{icon("whatsapp")}כתבו לי בוואטסאפ</a>
        <a class="btn btn--light" href="tel:+{PHONE_INTL}">{icon("phone")}התקשרו: <span class="ltr">{PHONE_DISPLAY}</span></a>
        <a class="btn btn--ghost-light" href="{root}contact/#forms">השאירו פרטים</a>
      </div>
    </div>
  </div>
</section>"""


def videos(root, topics):
    return f"""<section class="section section--tight" data-videos="{html.escape(topics)}" hidden>
  <div class="container">
    <div class="section-head">
      <p class="section-num">לצפייה ולהאזנה</p>
      <h2>סרטונים ופודקאסטים בנושא</h2>
    </div>
    <div class="video-grid"></div>
    <p class="mt-l mb-0"><a class="link-arrow" href="{root}content/">לכל התוכן והפודקאסטים {icon("arrow")}</a></p>
  </div>
</section>"""


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
def header(root, key):
    items = []
    for k, label, href in NAV:
        if k == "contact":
            continue
        cur = ' aria-current="page"' if k == key else ""
        items.append(f'<li><a class="nav__link" href="{root}{href}"{cur}>{label}{icon("arrow")}</a></li>')
    cur_contact = ' aria-current="page"' if key == "contact" else ""
    items.append(f'<li class="nav__item--contact-mobile"><a class="nav__link" href="{root}contact/"{cur_contact}>יצירת קשר{icon("arrow")}</a></li>')
    return f"""<header class="site-header">
  <div class="container header__inner">
    <a class="brand" href="{root}" aria-label="דוד סולומון — לעמוד הבית">
      {BRAND_MARK}
      <span class="brand__text"><span class="brand__name">דוד סולומון</span><span class="brand__role">עובד סוציאלי קליני · מטפל זוגי ומשפחתי</span></span>
    </a>
    <nav class="nav" id="site-nav" aria-label="ניווט ראשי">
      <ul class="nav__list">
        {"".join(items)}
      </ul>
      <div class="nav__contact">
        <a class="btn btn--wa" href="{wa()}" target="_blank" rel="noopener">{icon("whatsapp")}כתבו לי בוואטסאפ</a>
        <a class="btn btn--ghost" href="tel:+{PHONE_INTL}">{icon("phone")}<span class="ltr">{PHONE_DISPLAY}</span></a>
      </div>
    </nav>
    <a class="btn btn--primary btn--sm header__cta" href="{root}contact/">צרו קשר</a>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="פתיחת התפריט">
      {icon("menu", "icon-open")}{icon("x", "icon-close")}
    </button>
  </div>
</header>"""


def footer(root):
    links = "".join(f'<li><a href="{root}{href}">{label}</a></li>' for k, label, href in NAV)
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer__grid">
      <div class="footer__brand">
        <a class="brand" href="{root}" aria-label="דוד סולומון — לעמוד הבית">
          {BRAND_MARK}
          <span class="brand__text"><span class="brand__name">דוד סולומון</span><span class="brand__role">MSW · עובד סוציאלי קליני</span></span>
        </a>
        <p>טיפול בטראומה, במשברים ובתהליכי שינוי. לאדם, לזוג, למשפחה — ולארגונים ולקהילות.</p>
        <ul class="social" data-social-group hidden aria-label="רשתות חברתיות">
          <li><a data-social="youtube" href="#" hidden target="_blank" rel="noopener" aria-label="יוטיוב">{icon("youtube")}</a></li>
          <li><a data-social="instagram" href="#" hidden target="_blank" rel="noopener" aria-label="אינסטגרם">{icon("instagram")}</a></li>
          <li><a data-social="facebook" href="#" hidden target="_blank" rel="noopener" aria-label="פייסבוק">{icon("facebook")}</a></li>
        </ul>
      </div>
      <div>
        <p class="footer__title">באתר</p>
        <ul class="footer__links">{links}</ul>
      </div>
      <div>
        <p class="footer__title">יצירת קשר</p>
        <ul class="footer__links">
          <li><a href="{wa()}" target="_blank" rel="noopener">{icon("whatsapp")}וואטסאפ</a></li>
          <li><a href="tel:+{PHONE_INTL}">{icon("phone")}<span class="ltr">{PHONE_DISPLAY}</span></a></li>
          <li><a href="mailto:{EMAIL}">{icon("mail")}<span class="ltr">{EMAIL}</span></a></li>
          <li><a href="{MAPS_URL}" target="_blank" rel="noopener">{icon("map-pin")}מושב שדה יעקב</a></li>
        </ul>
      </div>
      <div>
        <p class="footer__title">במצוקה עכשיו?</p>
        <p class="footer__help">אם אתם או מישהו קרוב אליכם במצוקה חריפה, אל תחכו:<br>
        ער״ן — <a href="tel:1201">1201</a><br>
        נט״ל, קו סיוע לנפגעי טראומה — <a href="tel:1800363363" class="ltr">1-800-363-363</a><br>
        במצב חירום — מד״א <a href="tel:101">101</a></p>
      </div>
    </div>
    <div class="footer__bottom">
      <span>© <span data-year>2026</span> דוד סולומון · כל הזכויות שמורות</span>
      <span>קליניקה במושב שדה יעקב · מפגשים גם אונליין</span>
    </div>
  </div>
</footer>"""


def quick_contact(root, key):
    form_href = "#forms" if key == "contact" else f"{root}contact/#forms"
    return f"""<nav class="mobile-bar" aria-label="יצירת קשר מהירה">
  <a class="mobile-bar__btn mobile-bar__btn--wa" href="{wa()}" target="_blank" rel="noopener">{icon("whatsapp")}<span>וואטסאפ</span></a>
  <a class="mobile-bar__btn mobile-bar__btn--call" href="tel:+{PHONE_INTL}">{icon("phone")}<span>התקשרו עכשיו</span></a>
  <a class="mobile-bar__btn" href="{form_href}">{icon("message")}<span>השארת פרטים</span></a>
</nav>
<a class="wa-float" href="{wa()}" target="_blank" rel="noopener" aria-label="כתבו לי בוואטסאפ">{icon("whatsapp")}<span>וואטסאפ</span></a>"""


def layout(meta, body, root):
    key = meta.get("key", "")
    title = meta["title"]
    desc = meta.get("description", "")
    og_img = (SITE_URL.rstrip("/") + "/" if SITE_URL else root) + "assets/img/og-image.jpg"
    page_url = ""
    if SITE_URL:
        rel = meta["out"].replace("index.html", "")
        page_url = SITE_URL.rstrip("/") + "/" + rel
    canonical = f'<link rel="canonical" href="{page_url}">\n<meta property="og:url" content="{page_url}">\n' if page_url else ""
    extra_head = meta.get("_head", "")
    base_script = ""
    if meta.get("base") == "dynamic":
        # 404.html is served from any missing URL, so relative paths need a <base>.
        # On a GitHub *project* site (user.github.io/repo/) the base is /repo/; elsewhere it's /.
        base_script = ("<script>(function(){var p=location.pathname.split('/');"
                       "var b=(/\\.github\\.io$/.test(location.hostname)&&p.length>2&&p[1])?'/'+p[1]+'/':'/';"
                       "document.write('<base href=\"'+b+'\">');})();</script>\n")
    return f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
{base_script}<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="theme-color" content="#F7F3EA">
{canonical}<meta property="og:type" content="website">
<meta property="og:locale" content="he_IL">
<meta property="og:site_name" content="דוד סולומון">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{root}assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{root}assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;500;600;700;800&amp;family=Frank+Ruhl+Libre:wght@400;500;700&amp;display=swap">
<link rel="stylesheet" href="{root}assets/css/style.css?v={ASSET_VERSION}">
<script>document.documentElement.classList.add('js');setTimeout(function(){{if(!window.__siteReady)document.documentElement.classList.add('no-reveal')}},3000)</script>
{extra_head}</head>
<body class="page-{key}">
<a class="skip-link" href="#main">דילוג לתוכן הראשי</a>
{header(root, key)}
<main id="main" tabindex="-1">
{body}
</main>
{footer(root)}
{quick_contact(root, key)}
<script src="{root}assets/js/site-config.js?v={ASSET_VERSION}" defer></script>
<script src="{root}assets/js/main.js?v={ASSET_VERSION}" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
TOKEN = re.compile(r"\{\{(\w+)(?::([^}]*))?\}\}")


def render_tokens(text, root, key):
    def rep(m):
        name, arg = m.group(1), m.group(2)
        if name == "root":
            return root
        if name == "icon":
            parts = arg.split(" ", 1)
            return icon(parts[0], parts[1] if len(parts) > 1 else "")
        if name == "wa":
            return wa(arg)
        if name == "tel":
            return f"tel:+{PHONE_INTL}"
        if name == "phone":
            return f'<span class="ltr">{PHONE_DISPLAY}</span>'
        if name == "email":
            return EMAIL
        if name == "mailto":
            return f"mailto:{EMAIL}"
        if name == "maps":
            return MAPS_URL
        if name == "form":
            return form_org(root) if arg == "org" else form_therapy(root)
        if name == "contactlist":
            return contact_list()
        if name == "hotlines":
            return hotlines()
        if name == "cta":
            return cta(root, arg or "")
        if name == "videos":
            return videos(root, arg or "general")
        raise KeyError(f"unknown token {{{{{name}}}}} in page {key}")
    # two passes so components that contain tokens get resolved too
    return TOKEN.sub(rep, TOKEN.sub(rep, text))


def parse_page(path):
    with open(path, encoding="utf-8") as f:
        src = f.read()
    m = re.match(r"\s*<!--(.*?)-->\s*", src, re.S)
    if not m:
        raise ValueError(f"{path}: missing meta comment")
    meta = {}
    for line in m.group(1).strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    body = src[m.end():]
    head_m = re.search(r"<!--HEAD-->(.*?)<!--/HEAD-->", body, re.S)
    if head_m:
        meta["_head"] = head_m.group(1).strip() + "\n"
        body = body[:head_m.start()] + body[head_m.end():]
    return meta, body


def main():
    count = 0
    for name in sorted(os.listdir(PAGES_DIR)):
        if not name.endswith(".html"):
            continue
        meta, body = parse_page(os.path.join(PAGES_DIR, name))
        out = meta["out"]
        depth = out.count("/")
        root = "../" * depth if depth else "./"
        key = meta.get("key", "")
        body = render_tokens(body, root, key)
        if "_head" in meta:
            meta["_head"] = render_tokens(meta["_head"], root, key)
        page = layout(meta, body.strip(), root)
        if root == "./":
            # tidy: home links like ./about/ are fine, but the brand link "./" is clearer as "./"
            pass
        dest = os.path.join(ROOT, out)
        os.makedirs(os.path.dirname(dest) or ROOT, exist_ok=True)
        with open(dest, "w", encoding="utf-8", newline="\n") as f:
            f.write(page)
        count += 1
        print(f"  ✓ {out}")
    print(f"built {count} pages")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
