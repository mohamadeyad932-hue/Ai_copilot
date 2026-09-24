```markdown
# قواعد

## المادة  المعلوماتية  القسم
1. المعطيات                         رقم    DC

### دمشق Training Centre
- **unrwa**    30/4/2025  التاريخ    8          المحاضرة
- **الاونروا**

4    عدد              الحكيم نور  المدرب  المتوسط دمشق معهد
الصفحات

### :المحاضرة محاور

- االستعالمات حفظ  o
- عامة تمارين      o

### . New Query
ديدج مالعتسا ىلع طغضلاب موقن ديدج مالعتسا ةباتكل ،اقباس انملعت امك

### :التالية الخطوات نتبع بتنفيذه قمنا الذي االستعالم لحفظ

1. ctrl + S نضغط
2. save ونضغط أدناه موضح هو كما ،حفظه نريد الذي الملف اسم نكتب

```
SQLQuery2.sql- LAPTOP-01.master {LAPTOP-01User (53))*- Microsoft SQL Server Management Studio    Quick Launch (Ctri+Q)                                                     x
File  Edit     View      Query    Proiect  Tools Window Help
*
master                       Execute
Object Explorer                         4× SQLQuery2.sgl- LA...PTOP-01User (53))*X
Connect.                          t                 use pubs;                                                                                                                    +
8 Databases                                   select * from authors;
System Databases
E               Database Snapshots
clinic                                                             Save File As         ×
B               pubs
B     Database Diagrams                                                                   This PC  Desktop    v0 Search Desktop    P
8          Tables
System Tables                                            Organize             New folder
FileTables                                                DB1
External Tables                                                                                             No items match your search.
Graph Tables                                              Screenshots
dbo.authors                                                         Semester1
dbo.discounts                                                       UN
dbo.employee
dbo.jobs                                                           SSMS 20
dbo.pub_info
dbo.publishers                                                     This PC
dbouroysched                                                       3D Objects
dbo.sales
dbo.stores                                                          Desktop
dbo.titleauthor                                                    Dooumens
dbo.titles                                                          File name: SQLQuery1
Dropped Ledger Table
Save as type:
Views                                                                               SQL Files (*.sql)
8          External Resources
Synonyms
E     Programmability
0          Query Store             174 %                 Hide Folders                                                 Save                    Cancel
+          Service Broker
Connected. (1/1)                                                                                                 master 00:00:00 0 rows
```
```

---

```markdown
# CURRENT_PAGE_RAW_OCR_TEXT

:كالتالي الملف بفتح نقوم ،حفظه بعد ذاته الملف استخدام إلعادة .3

## Solution1 - Microsoft SQL Server Management Studio
**Quick Launch (Ctrl+Q)**

- File
- Edit
- View
- Project
- Tools
- Window
- Help

### Connect Object Explorer..
- Disconnect Object Explorer

### Open
- Project/Solution...          Ctrl+Shift+O
- Folder...                    Ctrl-Shitt+Alt-O
- Close
- Merge Extended Event Files...
- Close Solution
- Save Selected Items                    Ctrl+5
- File...                      Ctrl+0
- Save Selected Items As..
- Save All                               Ctrl+Shift+S
- File with New Connection..
- View in Browser                        Ctrl+Shift+W
- File Disconnected..
- Browse With...
- Policy
- Page Setup...
- Print...                               Ctrl+P
- Recent Files
- Recent Projects and Solutions
- Exit                                   Alt+F4

### Object Explorer
- dbo.roysched
- dbo.sales
- dbo.stores
- dbo.titleauthor
- dbo.titles
- Dropped Ledger Table
- 188 Views
- External Resources
- Synonyms
- Programmability
- Query Store
- Service Broker

**Ready**

## Solution1 - Microsoft SQL Server Management Studio
**Quick Launch (Ctrl+)**

- File
- Edit
- View
- Project
- Tools
- Window
- Help

### New Query
- Object Explorer
- Connect
- Databases
- System Databases
- Database Snapshots
- clinic
- pubs
- Database Diagrams
- Tables
- System Tables
- FileTables
- External Tables
- Graph Tables
- dbo.euthors
- dbo.discounts
- dbo.employee
- dbo.jobs
- dbo.pub_info
- dbo.publishers
- dbo.roysched
- dbo.sales
- dbo.stores
- dbo.titleauthor
- dbo.titles
- Dropped Ledger Table
- Views
- External Resources
- Synonyms
- Programmability
- Query Store
- Service Broker

### File Information
- File name: SQLQuery2
- File type: SQL Server files (.sql)
- Size: 33 bytes
```

---

# تمارين

## 1. مؤلفين فيها يوجد التي المدن عدد

## 2. كتب 5 من أكثر ينشرون الذين الناشرين لكل المبيعات قيمة مع الناشرين بأرقام قائمة

## 3. مدينة لكل المؤلفين عدد

## 4. مؤلفين 3 من أكثر بها يوجد التي المدن عدد

## 5. وظيفة كل في الموظفين عدد

## 6. موظفين ثالث من أكثر بها يعمل التي الوظائف

# الحل

## الأول والثاني

```sql
use pubs;

select count(distinct city) from authors;

select pub_id, sum(ytd_sales) from titles
group by pub_id
having count(*) > 5;
```

## الثالث والرابع

```sql
SELECT city, COUNT(*) AS author_count
FROM authors
GROUP BY city;

SELECT city, COUNT(*) AS author_count
FROM authors
GROUP BY city
HAVING COUNT(*) > 3;
```

---

```markdown
# والسادس الخامس

## استعلامات SQL

```sql
SELECT job_id, COUNT(*) AS employee_count
FROM employee
GROUP BY job_id;

SELECT job_id, COUNT(*) AS employee_count
FROM employee
GROUP BY job_id
HAVING COUNT(*) > 3;
```

## المستعار (Alias)

الكلمة AS نستخدم لتحديد اسم مستعار لعمود أو جدول في SQL. المستعارة تساعد في تحسين قراءة الاستعلامات وتبسيط أسماء الجداول أو الأعمدة.

### ملاحظات

- لا يوجد اسم لها أو توابع عن الناتجة الأعمدة مثل.
- إذا كانت هناك حاجة لتجميع البيانات، يمكن استخدام الدوال التجميعية.
```