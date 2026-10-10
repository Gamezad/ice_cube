# مژه (Eyelash) در Ice Cube — چطور کار می‌کند و چطور استایل جدید اضافه کنیم

این سند بر اساس بررسی واقعی فایل‌های `Assets/*.blend` و کد افزونه نوشته شده (با Blender 4.2 تست شده).
هر چیزی که اینجا گفته می‌شود با نسخه‌ی فعلی ریگ (`Ice_Cube_v2_Remake`، ریگ‌ورژن ۲.۱.۱) مطابقت دارد.

---

## ۱. معماری: مژه‌ها در عمل چطور کار می‌کنند؟

### هر استایل = یک مش (Mesh) داخل یک کالکشن اختصاصی

```
Ice Cube  [ice_cube.main]
└─ Meshes
   └─ Face  [ice_cube.face]                 ← تمام اجزای صورت اینجاست
      ├─ Eyelashes Default   [ice_cube.eyelashes_default]    → مش "Eyelashes"
      ├─ Eyelashes Andromeda [ice_cube.eyelashes_andromeda]  → مش "Eyelashes Andromeda"
      ├─ Eyelashes Bushy     [ice_cube.eyelashes_bushy]      → مش "Eyelashes Bushy"
      ├─ مش "Plane"      (مژه‌ی پایینِ Standard)   ← مستقیم داخل Face، کالکشن ندارد
      └─ مش "Plane.001"  (مژه‌ی پایینِ Bushy)      ← مستقیم داخل Face، کالکشن ندارد
```

* اسم کالکشن در `ice_cube_collection_id` ذخیره می‌شود و افزونه با آن استایل‌ها را پیدا می‌کند.
* مژه‌های **بالا** کالکشن اختصاصی دارند؛ مژه‌های **پایین** نه (فقط داخل `Face` هستند)،
  به همین دلیل «Bake Rig» مژه‌های پایین را پاک نمی‌کند.

### کلید روشن/خاموش: مادیفایر **Weld** (نه hide!)

هیچ‌وقت مش مژه از صحنه حذف یا مخفی نمی‌شود؛ در عوض روی مادیفایر `Weld` آن دو درایور است
(`show_viewport` و `show_render`) با این عبارت:

```python
(0 if eyelashes == INDEX else 1) + (1-face_rig) + emotion_eye_shape
```

| مقدار درایور | نتیجه |
|---|---|
| `0` | Weld خاموش → مش سالم و **نمایش داده می‌شود** |
| `1` یا بیشتر | Weld روشن → تمام ورتکس‌ها روی هم جمع می‌شوند → مش عملاً **ناپدید** |

بنابراین:

* عبارت فقط وقتی صفر می‌شود که استایل انتخاب‌شده با `INDEX` آن مش یکی باشد.
* `(1-face_rig)` یعنی اگر Face Rig خاموش باشد، همه‌ی مژه‌ها مخفی می‌شوند.
* `emotion_eye_shape` یعنی با فعال بودن هر شکل چشم احساسی (X، قلب، ستاره…) مژه‌ها مخفی می‌شوند.

سه متغیر درایور همگی به آبجکت ریگ (`Ice Cube`) اشاره می‌کنند:
`eyelashes` (یا `eyelashes_lower`)، `face_rig`، `emotion_eye_shape`.

### ⚠️ مهم‌ترین نکته: enum داخل درایور «عددِ صفر-پایه» است

در پایتون مقدار را به صورت رشته می‌بینید (`'1'`، `'2'`، …) اما **درایور مقدار enum را به صورت
اندیسِ عددیِ آیتم می‌خواند** (تست شده: مقدار `'3'` در درایور برابر `2` است).
برای `bpy.types.Object.eyelashes`:

| شناسه (در پایتون) | اندیس (در درایور) | استایل | مش |
|---|---|---|---|
| `'1'` | `0` | None | — (همه مخفی) |
| `'2'` | `1` | Standard | `Eyelashes` |
| `'3'` | `2` | Andromeda | `Eyelashes Andromeda` |
| `'4'` | `3` | Bushy | `Eyelashes Bushy` |
| `'5'` | `4` | اولین استایل شخصی | … |

یعنی استایل شخصیِ جدیدِ شما اندیس **۴** می‌گیرد. (این همان چیزی است که اسکریپت
`dev/add_eyelash_style.py` برایتان حساب می‌کند.)

### بقیه‌ی اجزای یک مشِ مژه

| مورد | مقدار |
|---|---|
| متریال‌ها | `Left Eyelash` و `Right Eyelash` (روی آبجکت `ice_cube_material_holder`؛ با id های `left_eyelash` / `right_eyelash`) |
| ترتیب مادیفایرها | `Weld` → `Armature` (ریگ) → `Subdivision` → `Lattice` (Head Twist) → `Lattice.001` (Head Cosmetic Lattice) |
| والد | آبجکت `Ice Cube` (آرماتور) |
| Vertex groupها | `Left/Right Eye Upper 1..3`، `... Middle 1..2`، `... Lower 1` و `Head` (برای مژه‌ی پایین: `... Lower 1..3` و `Head`) |
| پراپ سفارشی | `ice_cube.parented = True` (تا «Update Parenting» آن را دست‌نخورده بگذارد) |

---

## ۲. سه راه برای داشتن مژه‌ی جدید

### الف) جایگزین کردن مش یک استایل موجود (بدون دست زدن به کد)

ساده‌ترین راه: داخل `Assets/ice_cube.blend` مشِ `Eyelashes` را پاک نکنید، فقط **مش‌اش (Mesh Data) را
عوض کنید** یا ورتکس‌هایش را ویرایش کنید. اسم آبجکت، کالکشن، مادیفایرها و درایورها سر جایشان می‌مانند
و همه‌چیز کار می‌کند. عیبش این است که یکی از استایل‌های پیش‌فرض را از دست می‌دهید.

### ب) استایل کاملاً جدید (روش پیشنهادی)

اسکریپت `dev/add_eyelash_style.py` همه‌چیز را خودش می‌سازد:

```bash
blender Assets/ice_cube.blend --background --python dev/add_eyelash_style.py -- \
    --id wispy --label "Wispy" --source "Eyelashes"
```

* یک کپی از مش `--source` می‌سازد (با مش‌دیتای مجزا، پس ویرایشش روی استایل اصلی اثر نمی‌گذارد)،
* کالکشن `Eyelashes Wispy` با id ی `ice_cube.eyelashes_wispy` و `ice_cube_eyelash_index = 4` می‌سازد،
* درایورهای Weld را با اندیس درست از نو می‌سازد،
* فایل را ذخیره می‌کند.

همین دستور را برای هر سه نسخه‌ی ریگ اجرا کنید:

```bash
for f in ice_cube ice_cube_14px ice_cube_10px; do
  blender Assets/$f.blend --background --python dev/add_eyelash_style.py -- \
      --id wispy --label "Wispy" --source "Eyelashes"
done
```

سپس مش جدید را در بلندر باز کنید و مدل‌سازی‌اش را تغییر دهید (بخش ۴).
افزونه استایل جدید را **خودکار** در منوی کشویی «Eyelashes» نشان می‌دهد (نیازی به تغییر کد نیست).

سایر آپشن‌ها: `--lower` (مژه‌ی پایین)، `--index` (اندیس دستی)، `--no-save`، و `--list`
برای دیدن استایل‌های موجودِ یک فایل.

### ج) مژه‌ی پایین (Lower)

مژه‌های پایین فرق دارند: کالکشن اختصاصی ندارند و درایورشان پراپرتیِ `eyelashes_lower` را می‌خواند،
و آن enum در `Properties/enumerators.py` هنوز دستی است. اسکریپت اندیس را حساب می‌کند و خط مورد نیاز
را چاپ می‌کند؛ آن را به enum اضافه کنید:

```python
bpy.types.Object.eyelashes_lower = EnumProperty(
    name = "Eyelash Lower Type",
    default='1',
    items=[
        ('1', 'None', 'No Eyelashes'),
        ('2', 'Standard', 'Standard Ice Cube Eyelashes'),
        ('3', 'Bushy', 'Bushy Eyelashes'),
        ('4', 'Wispy', 'Wispy Eyelashes'),        # ← خط جدید (اندیس درایور: ۳)
    ],
    override={"LIBRARY_OVERRIDABLE"}
)
```

---

## ۳. بعد از تغییر فایل blend

1. **نسخه را بالا ببرید** تا پنل دروغ نگوید. دو جا باید با هم هماهنگ باشند:
   * `constants.py` → `ADDON_VERSION` و `INTERNAL_VERSION`
   * داخل فایل blend → پراپرتیِ `ice_cube.rig_version` روی دیتای آرماتور:
     ```python
     bpy.data.objects['Ice Cube'].data['ice_cube.rig_version'] = (2, 1, 2)
     ```
   اگر فقط فایل blend را عوض کنید و نسخه‌ی افزونه را نه، پنل می‌نویسد «Addon Outdated!».
2. فایل‌های blend ذخیره‌شده **فشرده نیستند** (`compress=False`)؛ موقع ذخیره همین را نگه دارید تا
   حجم و دیف‌ها بی‌دلیل بزرگ نشوند.
3. اگر می‌خواهید از خود بلندر ذخیره کنید، اپراتورهای `ice_cube.dev_update_ice_cube`
   (و `..._14px` / `..._10px`) فایل جاری را دقیقاً روی همان مسیر `Assets/` ذخیره می‌کنند.
4. تغییرات را تست کنید: ریگ را Append کنید، از منوی کشویی استایل جدید را انتخاب کنید و
   در حالت‌های مختلف (Face Rig خاموش، emotion eye shape فعال) نتیجه را ببینید.

---

## ۴. نکات مدل‌سازی

* **همیشه از روی یک مش موجود کپی بگیرید** (اسکریپت همین کار را می‌کند) تا vertex groupها،
  متریال‌ها، ترتیب مادیفایرها و درایورها درست باشند.
* ورتکس‌گروپ‌ها را دست نزنید: وزن‌دهی به استخوان‌های `Left/Right Eye Upper/Middle/Lower` و `Head`
  باعث می‌شود مژه با پلک و چشم حرکت کند. یک گروه را حذف کنید → مژه در جایش میخکوب می‌شود.
* متریال‌ها (`Left Eyelash` / `Right Eyelash`) را **به اشتراک** بگذارید؛ پنلِ
  `Style ▸ Material ▸ MISC` رنگ آن‌ها را از طریق همین دو متریال تغییر می‌دهد.
* مژه باید **یک** مش با دو متریال (چپ/راست) باشد، نه دو آبجکت جدا.
* مادیفایر `Weld` باید همیشه **اولین** مادیفایر بماند (در غیر این صورت قبل ازِ جمع‌شدن،
  subdivided و deformed می‌شود).
* اگر مش جدید شکل موجود را تغییر می‌دهد، حتماً با «Bake Rig» هم تست کنید
  (در این نسخه فقط مژه‌های بالا هنگام bake پاک می‌شوند).

---

## ۵. عیب‌یابی

| علامت | علت احتمالی |
|---|---|
| استایل جدید در منو نیست | کالکشن دارای `ice_cube_collection_id` با پیشوند `ice_cube.eyelashes_` نیست، یا زیرمجموعه‌ی `ice_cube.face` نیست |
| انتخاب استایل هیچ اتفاقی نمی‌اندازد | اندیسِ درایور با اندیسِ enum یکی نیست (`--list` را اجرا کنید) |
| مژه همیشه نمایش داده می‌شود | درایور روی `modifiers["Weld"].show_viewport` نیست یا عبارتش درست نیست |
| مژه هیچ‌وقت دیده نمی‌شود | `face_rig` خاموش است یا یک `emotion_eye_shape` فعال است (عبارت درایور را چک کنید) |
| بعد از Append، مژه‌ها به ریگ قدیمی وصل‌اند | درایور باید به آبجکتِ append‌شده اشاره کند (`targets[0].id`)؛ بلندر این را خودش اصلاح می‌کند |
| «Reset All» ارور می‌دهد | enumهایی که آیتم‌هاشان در زمان اجرا ساخته می‌شود مقدار پیش‌فرضِ رشته‌ای ندارند؛ برای همین `Operators/reset_all.py` یک fallback دارد |

---

## ۶. فایل‌های مرتبط در کد

| فایل | نقش |
|---|---|
| `Properties/enumerators.py` | تعریف enumهای `eyelashes` (خودکار) و `eyelashes_lower` (دستی) |
| `ice_cube_selectors.py` | `GetEyelashStyles()` — پیدا کردن کالکشن‌های استایل روی ریگ |
| `Panels/style.py` | نمایش منوی کشویی در `Style ▸ Cosmetics` |
| `Operators/bake_rig.py` | هنگام bake، فقط استایل انتخاب‌شده باقی می‌ماند |
| `Operators/reset_all.py` | ریست کردن پراپرتی‌ها (و fallback برای enum پویا) |
| `Operators/statistics.py` | خروجی/ورودی تنظیمات (شامل `eyelashes`) |
| `dev/add_eyelash_style.py` | اسکریپت کمکیِ ساخت استایل جدید |
