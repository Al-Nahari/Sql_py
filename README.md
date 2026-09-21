# Student Data Pipeline — Multi-Source ETL

مشروع Data Engineering يقوم ببناء **Data Integration & ETL Pipeline** يجمع بيانات الطلاب من ثلاثة مصادر مختلفة (CSV، REST API، SQLite)، ثم يقوم بالتحقق من جودتها وتنظيفها ودمجها وتحويلها، لينتج في النهاية Dataset موحد وجاهز للتحليل أو Machine Learning.

## 1. Project Overview

يحاكي المشروع سيناريو مؤسسة تعليمية تمتلك بيانات طلابها موزعة على ثلاثة أنظمة منفصلة:

| المصدر | البيانات | آلية الوصول |
|---|---|---|
| **CSV File** | البيانات الأساسية للطالب (الاسم، العمر، التخصص، المدينة) | `pandas.read_csv` |
| **REST API** | البيانات الأكاديمية (GPA، الحضور، الحالة) | `requests` عبر HTTP حقيقي إلى Mock API محلي |
| **SQLite Database** | المقررات والتسجيلات والدرجات (`courses`, `enrollments`) | `sqlite3` مع JOIN |

الناتج النهائي هو ملف واحد نظيف وموحد: `data/processed/final_dataset.csv`، بالإضافة إلى `data/rejected/rejected_records.csv` الذي يوثّق كل سجل تم رفضه وسبب الرفض.

## 2. Architecture

```
student_data_pipeline/
│
├── app/
│   ├── sources/            # Extract layer — مصدر واحد لكل ملف
│   │   ├── csv_source.py
│   │   ├── api_source.py
│   │   └── database_source.py
│   │
│   ├── mock_api/            # خادم REST API محلي (بديل API خارجي)
│   │   └── server.py
│   │
│   ├── transformation/
│   │   ├── cleaner.py       # Duplicates / Missing Values / Text normalization
│   │   ├── transformer.py   # Column naming / Type casting / Derived columns
│   │   └── integration.py   # الدمج على student_id + Data Lineage
│   │
│   ├── validation/
│   │   └── quality.py       # Rules 1–7 + رفض السجلات غير الصالحة
│   │
│   ├── output/
│   │   └── csv_writer.py    # Load: final_dataset.csv / rejected_records.csv
│   │
│   └── utils/
│       ├── config.py        # قراءة config.yaml
│       ├── logger.py        # إعداد Logging موحّد
│       └── metrics.py       # Pipeline Execution Summary
│
├── data/
│   ├── raw/students.csv     # بيانات خام تحتوي على مشاكل متعمدة
│   ├── processed/           # final_dataset.csv (يُنشأ عند التشغيل)
│   └── rejected/            # rejected_records.csv (يُنشأ عند التشغيل)
│
├── database/students.db     # يُنشأ ويُملأ تلقائيًا عند أول تشغيل
├── logs/pipeline.log        # يُنشأ عند التشغيل
├── tests/test_pipeline.py
├── config.yaml
├── main.py
├── requirements.txt
└── README.md
```

كل طبقة مسؤولة عن شيء واحد فقط (Single Responsibility): `sources` لا تعرف شيئًا عن التنظيف، و`transformation` لا تعرف من أين أتت البيانات، و`validation` لا تكتب ملفات. هذا الفصل هو ما يسمح بإضافة مصدر جديد (Excel، MongoDB...) دون إعادة كتابة الـ Pipeline بالكامل.

## 3. Data Sources

### 3.1 CSV — `data/raw/students.csv`
الأعمدة: `student_id, student_name, age, major, city`.
يحتوي عمدًا على: قيمة اسم مفقودة، صف مكرر بالكامل، عمر غير منطقي (200 و5)، ومسافات/اختلاف حالة أحرف في المدينة (`Sanaa` / `SANAA` / ` sanaa `).

### 3.2 REST API — `app/mock_api/server.py`
خادم HTTP محلي حقيقي (بدون Flask، فقط `http.server` من المكتبة القياسية) يوفر `GET /students` بصيغة JSON تحتوي على `student_id, gpa, attendance, status`. يتم استدعاؤه عبر `requests.get()` تمامًا كأي REST API خارجي، مع معالجة كاملة لـ: Connection Error، Timeout، HTTP Error، JSON غير صالح، واستجابة فارغة — بإعادة محاولة (retry) تصل إلى 3 مرات. تم اختيار Mock API محلي بدلًا من API عام خارجي حتى يعمل المشروع بشكل موثوق دون الاعتماد على اتصال إنترنت وقت التصحيح.

### 3.3 SQLite — `database/students.db`
يُنشأ تلقائيًا عند أول تشغيل (seed) بجدولين:
- `courses(course_id, course_name, credit_hours)`
- `enrollments(student_id, course_id, semester, score)`

يتم تجميع الدرجات عبر `student_id` (متوسط الدرجات وعدد المقررات) قبل الدمج مع المصدرين الآخرين، لأن كل طالب قد يكون مسجلاً في أكثر من مقرر.

## 4. ETL Pipeline

الترتيب الفعلي في `main.py::run_pipeline()`:

```
Extract (CSV + API + SQLite)
        │
        ▼
Validate Sources  (فحص أولي سريع، تسجيل فقط)
        │
        ▼
Clean  (إزالة التكرارات، توحيد النصوص، معالجة القيم المفقودة)
        │
        ▼
Integrate  (دمج على student_id + تسجيل مصدر كل سجل)
        │
        ▼
Transform  (توحيد أسماء الأعمدة، تحويل الأنواع، أعمدة مشتقة)
        │
        ▼
Final Validation  (Rules 1–7 → Valid / Rejected)
        │
        ▼
Load  (final_dataset.csv + rejected_records.csv)
```

- **Extract**: قراءة كل مصدر كما هو دون أي تعديل على المحتوى.
- **Transform**: توحيد الأعمدة (`Student ID` → `student_id`)، تحويل الأنواع، وإنشاء عمودين مشتقين: `performance_level` (من GPA) و`attendance_status` (من نسبة الحضور).
- **Validate**: تطبيق قواعد الجودة والفصل بين السجلات الصالحة والمرفوضة.
- **Integrate**: `outer merge` على `student_id` حتى لا يُفقد أي سجل من أي مصدر، مع عمود `source` يوثّق من أي مصدر/مصادر جاء كل سجل (Data Lineage).
- **Load**: كتابة الناتج النهائي والسجلات المرفوضة كملفات CSV منفصلة.

## 5. Data Quality

يتم تطبيق القواعد التالية في `app/validation/quality.py`:

| # | القاعدة |
|---|---|
| 1 | `student_id` لا يمكن أن يكون NULL |
| 2 | `student_id` يجب أن يكون فريدًا (التكرار يُرفض بالكامل) |
| 3 | `age` بين 16 و80 |
| 4 | `gpa` بين 0 و4 |
| 5 | `attendance` بين 0 و100 |
| 6 | `avg_score` بين 0 و100 |
| 7 | توافق `student_id` بين المصادر (يُضمن عبر الدمج على نفس المفتاح ونوع بيانات موحّد) |

كل سجل يفشل في أي قاعدة يُنقل إلى `data/rejected/rejected_records.csv` مع عمود `error_reason` يوضح السبب (قد يحتوي على أكثر من سبب واحد للسجل نفسه).

## 6. Installation

```bash
pip install -r requirements.txt
```

## 7. Running

```bash
python main.py
```

عند التشغيل الأول، سيقوم البرنامج تلقائيًا بـ: إنشاء `database/students.db` وتعبئته، تشغيل خادم الـ Mock API محليًا، وتنفيذ الـ Pipeline كاملًا، ثم طباعة ملخص التنفيذ (Pipeline Execution Summary).

## 8. Output

| الملف | الوصف |
|---|---|
| `data/processed/final_dataset.csv` | Dataset النهائي الموحد والنظيف، جاهز للتحليل أو ML |
| `data/rejected/rejected_records.csv` | السجلات المرفوضة مع `error_reason` |
| `logs/pipeline.log` | سجل تفصيلي لكل مرحلة من مراحل الـ Pipeline |

## Testing

```bash
python -m unittest discover -s tests -v
```

يغطي `tests/test_pipeline.py` الاختبارات الثمانية المطلوبة: تحميل CSV، الاتصال بالـ API، استخراج SQLite، إزالة التكرارات، معالجة القيم المفقودة، رفض البيانات غير الصالحة، نجاح الدمج، وإنشاء `final_dataset.csv`.

## Bonus Features (متطلبات التميز)

- **Pipeline Configuration**: جميع المسارات وعتبات التحقق موجودة في `config.yaml` بدلًا من ترميزها داخل الكود.
- **Data Lineage**: عمود `source` في الناتج النهائي يوضح أي المصادر (CSV/API/DATABASE) ساهم في كل سجل.
- **Pipeline Metrics**: ملخص تنفيذي (`PIPELINE EXECUTION SUMMARY`) يُطبع ويُسجَّل في نهاية كل تشغيل، يتضمن عدد السجلات من كل مصدر، عدد الصالحة والمرفوضة والمكررة، ووقت التنفيذ.
- **Reusable Architecture**: إضافة مصدر جديد (Excel/MongoDB/PostgreSQL...) تتطلب فقط ملف جديد في `app/sources/` يُعيد `DataFrame`، دون أي تعديل على طبقات التنظيف أو التحقق أو الدمج.

---

## أسئلة نهائية (Section 22)

**1. لماذا نحتاج إلى Data Pipeline عند التعامل مع مصادر متعددة؟**
لأن كل مصدر له تنسيقه وأخطاءه الخاصة، وبدون Pipeline موحّد سيقوم كل مطوّر أو تقرير بمعالجة البيانات بطريقة مختلفة. الـ Pipeline يضمن أن كل سجل يمر بنفس خطوات التحقق والتنظيف والدمج، بشكل قابل للتكرار والتوثيق والاختبار.

**2. ما الفرق بين Raw Data وProcessed Data؟**
الـ Raw Data هي البيانات كما وصلت من المصدر دون أي تعديل (قد تحتوي على تكرار، قيم مفقودة، أخطاء تنسيق). الـ Processed Data هي نتيجة تمرير هذه البيانات عبر التنظيف والتحقق والتحويل، وتكون جاهزة للاستخدام المباشر في التحليل أو النماذج.

**3. ما الفرق بين Extract وTransform وLoad؟**
Extract هو استخراج البيانات كما هي من مصدرها (CSV/API/DB). Transform هو تعديل شكل البيانات ومحتواها (تحويل الأنواع، توحيد الأسماء، إضافة أعمدة مشتقة). Load هو حفظ الناتج النهائي في وجهته (هنا: ملفات CSV).

**4. ما المشاكل التي واجهتها أثناء دمج البيانات؟**
اختلاف نوع `student_id` بين المصادر (نص/رقم) كان يمنع الدمج الصحيح، فتم توحيده إلى رقم صحيح (`Int64`) قبل الـ merge. كذلك وجود سجل في API غير موجود في CSV (`1099`) تطلّب استخدام `outer join` بدل `inner join` حتى لا يُفقد أي سجل، مع قبول أن بعض الأعمدة ستكون فارغة لهذا النوع من السجلات.

**5. كيف تعاملت مع Missing Values؟**
حسب نوع العمود: الاسم المفقود عُوّض بقيمة `"Unknown"` بدلًا من حذف السجل بالكامل، GPA المفقود عُوّض بالوسيط (median) لتفادي تأثير القيم الشاذة، والحضور المفقود عُوّض بقاعدة عمل واضحة (0) بدل تخمينه لأنه رقم حساس أكاديميًا.

**6. كيف تعاملت مع Duplicate Records؟**
على مستوى CSV: إزالة الصفوف المكررة بالكامل (`drop_duplicates`). على مستوى SQLite: إزالة صفوف التسجيل (`enrollments`) المكررة بنفس (`student_id, course_id, semester`) قبل التجميع. وعلى مستوى الناتج النهائي: أي `student_id` مكرر بعد الدمج يُرفض بالكامل (Rule 2) بدل اختيار نسخة عشوائية منه.

**7. كيف تعاملت مع Invalid Records؟**
لا يتم حذفها بصمت. تُفحص بمجموعة قواعد واضحة (Rules 1–6) في `validate_final_data`، وأي سجل يفشل ينتقل إلى `rejected_records.csv` مع توضيح دقيق لسبب الرفض (قد يكون أكثر من سبب واحد)، بحيث يمكن مراجعتها لاحقًا يدويًا بدل أن تختفي.

**8. لماذا يجب فصل طبقة Extraction عن Transformation؟**
حتى يمكن اختبار كل طبقة بمعزل عن الأخرى، وحتى يمكن استبدال مصدر بيانات (مثلًا تغيير API) دون التأثير على منطق التنظيف والتحويل الذي لا علاقة له بمصدر البيانات. هذا الفصل هو ما يجعل إضافة مصدر جديد مستقبلًا أمرًا بسيطًا.

**9. لماذا يعتبر Data Validation جزءًا أساسيًا من هندسة البيانات؟**
لأن نموذج Machine Learning أو تقرير BI مبني على بيانات خاطئة سيُنتج نتائج خاطئة بثقة عالية (Garbage In, Garbage Out). التحقق من الجودة هو خط الدفاع الذي يمنع وصول بيانات غير موثوقة إلى مراحل اتخاذ القرار.

**10. كيف يمكن تطوير Pipeline ليعمل بشكل دوري وآلي؟**
عبر جدولته باستخدام أداة Orchestration مثل `cron` لتشغيل بسيط، أو أدوات متخصصة مثل Apache Airflow / Prefect لإدارة الاعتمادية بين المهام، إعادة المحاولة عند الفشل، والتنبيهات، مع فصل الإعدادات (`config.yaml`) عن الكود حتى يسهل تغيير الجدولة دون تعديل منطق المعالجة.

**11. كيف يمكن جعل Pipeline يتعامل مع ملايين السجلات؟**
عبر معالجة البيانات على دفعات (Chunking) بدلًا من تحميلها كاملة في الذاكرة، استخدام تنسيقات تخزين عمودية أسرع مثل Parquet بدل CSV، توزيع المعالجة على عدة عُقد (Spark/Dask)، وفهرسة قواعد البيانات المصدر لتسريع عمليات القراءة والـ JOIN.

**12. ما الفرق بين Batch Processing وStreaming Processing؟**
Batch Processing يعالج مجموعة كبيرة من البيانات دفعة واحدة على فترات محددة (كما في هذا المشروع: تشغيل كامل للـ Pipeline كل مرة). Streaming Processing يعالج كل سجل أو حدث فور وصوله بشكل مستمر ولحظي، وهو مناسب عندما يكون الوقت الفعلي (Real-time) مطلوبًا، لكنه أعقد من ناحية إدارة الحالة والأخطاء.
