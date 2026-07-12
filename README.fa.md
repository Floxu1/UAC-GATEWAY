# UAC Gateway

**Language / زبان:** [English](README.md) | **فارسی**

UAC Gateway یک ابزار دسکتاپ ویندوزی برای اشتراک‌گذاری مسیر VPN فعال یا منبع پراکسی محلی تنظیم‌شده با تلویزیون‌ها و دستگاه‌های داخل شبکه LAN است؛ مخصوص دستگاه‌هایی که خودشان کلاینت VPN ندارند.

این برنامه یک رابط گرافیکی با PySide6 دارد، کارت‌های شبکه VPN و LAN را تشخیص می‌دهد، فقط هنگام تغییر تنظیمات Routing ویندوز درخواست دسترسی Administrator می‌کند و مقادیر لازم برای تنظیم دستی شبکه روی تلویزیون یا دستگاه مقصد را نمایش می‌دهد.

> این پروژه تنظیمات Routing، IP Forwarding و در صورت نیاز NAT ویندوز را تغییر می‌دهد. فقط روی شبکه‌ها و دستگاه‌هایی استفاده کنید که مالک آن هستید یا اجازه مدیریت آن‌ها را دارید.

---

## امکانات

- اشتراک‌گذاری اتصال VPN ویندوز با تلویزیون یا دستگاه LAN.
- تشخیص آداپتورهای VPN و Tunnelهای مبتنی بر Route.
- تشخیص منبع پراکسی محلی پشتیبانی‌شده در صورت تنظیم بودن.
- تشخیص خودکار آداپتورهای VPN و LAN.
- تولید مقادیر IP دستی برای تلویزیون یا دستگاه مقصد.
- حالت اختیاری سازگاری با WinNAT.
- Kill Switch اختیاری برای توقف اشتراک‌گذاری در صورت قطع شدن VPN.
- اجرای Start و Stop با درخواست UAC ویندوز.
- ذخیره فایل‌های وضعیت برای Restore و بازیابی تنظیمات.

---

## نحوه کار

روند معمول کار:

1. ابتدا VPN روی کامپیوتر ویندوزی وصل است.
2. تلویزیون یا دستگاه LAN به همان Wi-Fi/LAN کامپیوتر وصل است.
3. UAC Gateway مسیر Routing را از آداپتور LAN انتخاب‌شده به آداپتور VPN یا منبع انتخاب‌شده فعال می‌کند.
4. برنامه مقادیر IP دستی را برای تلویزیون یا دستگاه نمایش می‌دهد.
5. تلویزیون یا دستگاه از کامپیوتر ویندوزی به عنوان Gateway استفاده می‌کند.

نمونه تنظیمات دستگاه بعد از اجرای موفق:

```text
IP Address: 192.168.70.200
Subnet Mask: 255.255.255.0
Gateway: 192.168.70.151
DNS: 9.9.9.9
Backup DNS: 208.67.222.222
```

---

## تصویر برنامه


```md
i'll upload it soon
```

---

## پیش‌نیازها

- Windows 10 یا Windows 11
- Python نسخه 3.10 یا جدیدتر
- وجود PowerShell با نام `powershell.exe`
- دسترسی Administrator برای عملیات Start و Stop
- یک آداپتور VPN فعال، Tunnel مبتنی بر Route، یا منبع پراکسی محلی پشتیبانی‌شده
- اتصال تلویزیون یا دستگاه LAN به همان شبکه محلی کامپیوتر ویندوزی

وابستگی Python:

```text
PySide6>=6.7
```

---

## فایل‌های لازم پروژه

ساختار پیشنهادی ریپازیتوری:

```text
UAC-Gateway/
  README.md
  README.fa.md
  LICENSE
  main.py
  backend.py
  requirements.txt
  UAC Gateway.bat
  discover.ps1
  gateway.ps1
  assets/
    uac_gateway_preview.png
  data/                   # در زمان اجرا ساخته می‌شود؛ commit نشود
```

نکته مهم: فایل `backend.py` انتظار دارد این دو اسکریپت PowerShell کنار `main.py` وجود داشته باشند:

```text
discover.ps1
gateway.ps1
```

بدون این فایل‌ها ممکن است رابط گرافیکی باز شود، اما تشخیص آداپتورها و عملیات Start/Stop کار نخواهد کرد.

---

## نصب

### 1. کلون کردن ریپازیتوری

```powershell
git clone https://github.com/Floxu1/UAC-GATEWAY.git
cd UAC-GATEWAY
```

### 2. ساخت محیط مجازی

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

اگر PowerShell اجازه فعال‌سازی محیط مجازی را نداد، اجرا کنید:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### 3. نصب وابستگی‌ها

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. اضافه کردن اسکریپت‌های PowerShell

مطمئن شوید این فایل‌ها کنار `main.py` وجود دارند:

```text
discover.ps1
gateway.ps1
```

### 5. اجرای برنامه

روش پیشنهادی:

```powershell
."UAC Gateway.bat"
```

روش جایگزین:

```powershell
python main.py
```

---

## استفاده

1. ابتدا VPN را روی ویندوز وصل کنید.
2. برنامه UAC Gateway را باز کنید.
3. اگر آداپتورها نمایش داده نشدند، روی **AUTO DETECT** بزنید.
4. در بخش **ACTIVE VPN / TUNNEL** مسیر VPN یا آداپتور منبع را انتخاب کنید.
5. در بخش **TV NETWORK / LAN** آداپتور Wi-Fi/LAN متصل به تلویزیون یا دستگاه را انتخاب کنید.
6. گزینه **Enable WinNAT compatibility mode** را روشن نگه دارید، مگر اینکه مشکل ایجاد کند.
7. گزینه **Stop sharing automatically if VPN disconnects** را برای امنیت بیشتر روشن نگه دارید.
8. روی **START GATEWAY** بزنید.
9. پیام UAC ویندوز را تأیید کنید.
10. تنظیمات نمایش‌داده‌شده برای تلویزیون یا دستگاه را کپی کنید.
11. همان مقادیر را در تنظیمات **Manual IP / Static IP** دستگاه وارد کنید. اگر کاربر نمی‌داند این تنظیمات کجاست، از راهنمای مخصوص هر دستگاه در بخش بعد استفاده کند.
12. اینترنت دستگاه را تست کنید.

---

## تنظیم دستی تلویزیون، موبایل یا دستگاه مقصد

بعد از فعال شدن Gateway، برنامه چند مقدار شبکه نمایش می‌دهد. این مقادیر باید روی **تلویزیون، موبایل، تبلت، کنسول یا دستگاه مقصد** وارد شوند.

مقادیر را دقیقاً مطابق چیزی که UAC Gateway نشان می‌دهد وارد کنید:

- **IP Address**: آی‌پی جدید دستگاه مقصد
- **Subnet Mask**: ماسک شبکه محلی
- **Gateway**: آی‌پی LAN کامپیوتر ویندوزی که برنامه نشان می‌دهد
- **DNS**: DNS نمایش‌داده‌شده توسط برنامه
- **Backup DNS**: DNS دوم، در صورت وجود

نکات مهم:

- این مقادیر را روی **دستگاه مقصد** وارد کنید، نه روی کامپیوتر ویندوزی.
- دستگاه مقصد باید به همان Wi-Fi/LAN کامپیوتر ویندوزی وصل باشد.
- آی‌پی ساخته‌شده برای دستگاه نباید قبلاً توسط دستگاه دیگری در شبکه استفاده شده باشد.
- اسم این بخش در دستگاه‌های مختلف ممکن است فرق کند: **Manual IP**، **Static IP**، **IP Settings**، **Configure IP** یا **Advanced network settings**.
- برای برگشت به حالت عادی، تنظیمات دستگاه را دوباره روی **Automatic**، **DHCP** یا **Auto IP** بگذارید.

### تلویزیون LG / webOS

1. با کنترل تلویزیون وارد **Settings** شوید.
2. وارد **All Settings** شوید.
3. به مسیر **General** > **Network** بروید.
4. اتصال فعال را انتخاب کنید: **Wi-Fi Connection** یا **Wired Connection**.
5. وارد **Advanced Wi-Fi Settings**، **Edit** یا **Other Network Settings** شوید. نام دقیق این گزینه ممکن است در نسخه‌های مختلف webOS فرق کند.
6. گزینه **Set Automatically**، **Auto IP** یا **IP Auto Setting** را خاموش کنید.
7. مقادیر UAC Gateway را وارد کنید:
   - **IP Address** = مقدار `IP Address`
   - **Subnet Mask** = مقدار `Subnet Mask`
   - **Gateway** = مقدار `Gateway`
   - **DNS Server** = مقدار `DNS`
8. تنظیمات را ذخیره کنید و اگر تلویزیون درخواست کرد، دوباره به شبکه وصل شوید.
9. یک برنامه مثل YouTube، Netflix یا مرورگر تلویزیون را باز کنید و اینترنت را تست کنید.

### تلویزیون Samsung Smart TV / Tizen

1. وارد **Settings** شوید.
2. به مسیر **General** > **Network** بروید.
3. وارد **Network Status** شوید.
4. گزینه **IP Settings** را انتخاب کنید.
5. گزینه **IP Setting** را روی **Enter manually** بگذارید.
6. گزینه **DNS Setting** را روی **Enter manually** بگذارید.
7. مقادیر UAC Gateway را وارد کنید:
   - **IP Address** = مقدار `IP Address`
   - **Subnet Mask** = مقدار `Subnet Mask`
   - **Gateway** = مقدار `Gateway`
   - **DNS Server** = مقدار `DNS`
8. تنظیمات را ذخیره کنید و Network Test تلویزیون را اجرا کنید.

### Android TV / Google TV / Chromecast with Google TV / Mi Box

1. وارد **Settings** شوید.
2. به **Network & Internet** بروید.
3. شبکه Wi-Fi متصل‌شده را انتخاب کنید.
4. وارد **IP settings** شوید و گزینه **Static** را انتخاب کنید.
5. اگر این گزینه را نمی‌بینید، شبکه را **Forget** کنید، دوباره وصل شوید، وارد **Advanced options** شوید و **IP settings** را روی **Static** بگذارید.
6. مقادیر UAC Gateway را وارد کنید:
   - **IP address** = مقدار `IP Address`
   - **Gateway** = مقدار `Gateway`
   - **Network prefix length** = اگر `Subnet Mask` برابر `255.255.255.0` است، مقدار `24` را وارد کنید
   - **DNS 1** = مقدار `DNS`
   - **DNS 2** = مقدار `Backup DNS`، در صورت وجود
7. ذخیره کنید و YouTube یا مرورگر را تست کنید.

### Amazon Fire TV / Fire TV Stick

1. وارد **Settings** شوید.
2. به **Network** بروید.
3. شبکه Wi-Fi خود را انتخاب کنید.
4. اگر گزینه **Advanced** وجود دارد، آن را باز کنید. در بعضی نسخه‌ها باید اول **Forget This Network** را بزنید، دوباره به Wi-Fi وصل شوید، رمز Wi-Fi را وارد کنید و بعد **Advanced** را انتخاب کنید.
5. گزینه **Static** یا تنظیم دستی IP را انتخاب کنید.
6. مقادیر UAC Gateway را وارد کنید:
   - **IP Address** = مقدار `IP Address`
   - **Gateway** = مقدار `Gateway`
   - **Network Prefix Length** = اگر `Subnet Mask` برابر `255.255.255.0` است، مقدار `24` را وارد کنید
   - **DNS 1** = مقدار `DNS`
   - **DNS 2** = مقدار `Backup DNS`، در صورت وجود
7. ذخیره کنید و یک برنامه را تست کنید.

### موبایل یا تبلت Android

1. وارد **Settings** شوید.
2. به **Network & Internet** یا **Connections** بروید.
3. وارد **Wi-Fi** شوید.
4. روی Wi-Fi متصل‌شده بزنید، یا روی آن نگه دارید و **Modify network** را انتخاب کنید.
5. وارد **Advanced options** شوید.
6. گزینه **IP settings** را از **DHCP** به **Static** تغییر دهید.
7. مقادیر UAC Gateway را وارد کنید:
   - **IP address** = مقدار `IP Address`
   - **Gateway** = مقدار `Gateway`
   - **Network prefix length** = اگر `Subnet Mask` برابر `255.255.255.0` است، مقدار `24` را وارد کنید
   - **DNS 1** = مقدار `DNS`
   - **DNS 2** = مقدار `Backup DNS`، در صورت وجود
8. ذخیره کنید، اگر لازم بود Wi-Fi را قطع و وصل کنید، سپس مرورگر را تست کنید.

### iPhone یا iPad

1. وارد **Settings** شوید.
2. وارد **Wi-Fi** شوید.
3. کنار Wi-Fi متصل‌شده روی دکمه **ⓘ** بزنید.
4. در بخش **IPv4 Address** روی **Configure IP** بزنید.
5. گزینه **Manual** را انتخاب کنید.
6. این مقادیر را وارد کنید:
   - **IP Address** = مقدار `IP Address`
   - **Subnet Mask** = مقدار `Subnet Mask`
   - **Router** = مقدار `Gateway`
7. به صفحه قبل برگردید و روی **Configure DNS** بزنید.
8. گزینه **Manual** را انتخاب کنید.
9. اگر DNS قبلی وجود دارد، آن را حذف کنید و این موارد را اضافه کنید:
   - **DNS Server** = مقدار `DNS`
   - در صورت وجود، `Backup DNS` را هم به عنوان سرور دوم اضافه کنید
10. ذخیره کنید و Safari یا یک برنامه دیگر را تست کنید.

### دستگاه Windows به عنوان دستگاه مقصد

1. وارد **Settings** شوید.
2. به **Network & Internet** بروید.
3. بسته به اتصال فعال، وارد **Wi-Fi** یا **Ethernet** شوید.
4. Properties شبکه فعال را باز کنید.
5. بخش **IP assignment** را پیدا کنید و روی **Edit** بزنید.
6. گزینه **Manual** را انتخاب کنید و **IPv4** را روشن کنید.
7. مقادیر UAC Gateway را وارد کنید:
   - **IP address** = مقدار `IP Address`
   - **Subnet mask** = مقدار `Subnet Mask`
   - **Gateway** = مقدار `Gateway`
   - **Preferred DNS** = مقدار `DNS`
   - **Alternate DNS** = مقدار `Backup DNS`، در صورت وجود
8. ذخیره کنید و مرورگر را تست کنید.

### روش تست بعد از تنظیم دستی

بعد از ذخیره تنظیمات Manual IP:

1. Wi-Fi دستگاه مقصد را یک بار قطع و وصل کنید، یا دستگاه را Restart کنید.
2. مرورگر یا یک برنامه مثل YouTube را باز کنید.
3. اگر اینترنت کار نکرد، تنظیمات دستگاه را دوباره روی **Automatic/DHCP** بگذارید، دوباره وصل شوید و سپس بخش رفع اشکال پایین را بررسی کنید.

---

## توقف و بازگردانی تنظیمات

از دکمه **STOP & RESTORE** داخل برنامه استفاده کنید.

این کار تنظیمات Routing و Forwarding ویندوز را به حالت ذخیره‌شده قبل از شروع Gateway برمی‌گرداند.

اگر برنامه بسته شد یا کرش کرد:

1. دوباره UAC Gateway را باز کنید.
2. روی **STOP & RESTORE** بزنید.
3. پیام UAC را تأیید کنید.
4. اگر Routing هنوز مشکل داشت، ویندوز را Restart کنید و Route/NATهای موقت ساخته‌شده توسط `gateway.ps1` را دستی بررسی و حذف کنید.

---

## فایل‌های زمان اجرا

برنامه ممکن است فایل‌های زیر را در زمان اجرا بسازد:

```text
data/gateway-config.json
data/gateway-state.json
data/gateway-result.json
*.log
```

این فایل‌ها ممکن است شامل آی‌پی‌های محلی، شماره Interface، DNS، Process ID و وضعیت اجرای برنامه باشند. آن‌ها را در ریپازیتوری عمومی commit نکنید.

---

## `.gitignore` پیشنهادی

```gitignore
.venv/
__pycache__/
*.pyc
*.pyo
*.log

# Runtime data
data/
gateway-config.json
gateway-state.json
gateway-result.json

# Local builds
build/
dist/
*.spec
```

---

## رفع اشکال

### برنامه باز می‌شود اما آداپتورها تشخیص داده نمی‌شوند

بررسی کنید فایل `discover.ps1` کنار `main.py` وجود دارد و قابل اجرا است:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\discover.ps1
```

### Start بلافاصله خطا می‌دهد

بررسی کنید فایل `gateway.ps1` کنار `main.py` وجود دارد و پارامترهای مورد انتظار را پشتیبانی می‌کند:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\gateway.ps1 -Action start -ConfigPath .\data\gateway-config.json
```

### پیام UAC نمایش داده نمی‌شود

برنامه را از یک حساب کاربری عادی ویندوز اجرا کنید و بررسی کنید Windows Security، آنتی‌ویروس یا Group Policy جلوی نمایش UAC را نگرفته باشد.

### تلویزیون یا دستگاه اینترنت ندارد

این موارد را بررسی کنید:

- کامپیوتر و دستگاه روی یک LAN/Subnet باشند.
- IP دستگاه توسط دستگاه دیگری استفاده نشده باشد.
- Gateway دستگاه روی IP LAN کامپیوتر که برنامه نشان می‌دهد تنظیم شده باشد.
- DNS روی مقدار نمایش‌داده‌شده در برنامه تنظیم شده باشد.
- آداپتور منبع و آداپتور LAN یکسان نباشند.
- VPN هنوز روی کامپیوتر کار کند.
- Windows Firewall یا نرم‌افزار امنیتی دیگر جلوی Forwarding را نگرفته باشد.

### هشدار WinNAT unavailable

اگر نتیجه شامل هشدار زیر بود:

```text
WinNAT unavailable; forwarding-only mode is active
```

یعنی NAT ویندوز فعال نشده و برنامه در حالت Forwarding-only کار می‌کند. بعضی شبکه‌ها ممکن است همچنان کار کنند، اما ترافیک وابسته به NAT ممکن است مشکل داشته باشد.

راه‌حل‌های پیشنهادی:

- Stop/Start را دوباره با دسترسی Administrator انجام دهید.
- ویندوز را Restart کنید.
- بررسی کنید VPN، ماشین مجازی، کانتینر یا نرم‌افزار امنیتی دیگری تنظیمات NAT را اشغال نکرده باشد.
- با غیرفعال کردن WinNAT compatibility mode تست کنید.

---

## توسعه

بررسی Syntax:

```powershell
python -m py_compile main.py backend.py
```

اجرای مستقیم رابط گرافیکی:

```powershell
python main.py
```

---

## نکات امنیتی

- عملیات Start/Stop به دسترسی Administrator نیاز دارد، چون تنظیمات Routing و Forwarding ویندوز تغییر می‌کند.
- اسکریپت PowerShell، فایل EXE یا DLL ناشناس را از منابع غیرقابل اعتماد اجرا نکنید.
- فایل‌های وضعیت، لاگ‌ها و تنظیمات مخصوص سیستم خودتان را commit نکنید.
- اگر قطعه یا ابزار شخص ثالثی همراه پروژه منتشر می‌کنید، لایسنس آن را جداگانه بررسی کنید.
- برای انتشار عمومی، در صورت امکان فایل‌ها را Code-sign کنید و Checksum منتشر کنید.

---

## محدودیت‌های شناخته‌شده

- فقط برای ویندوز است.
- برای تشخیص آداپتورها و تغییر Routing به اسکریپت‌های PowerShell نیاز دارد.
- نیازمند تنظیم دستی IP روی تلویزیون یا دستگاه مقصد است.
- شماره Interface کارت شبکه مخصوص همان سیستم است و ممکن است بعد از Restart یا تغییر آداپتور عوض شود.
- رابط گرافیکی ابزارهای پیشرفته تشخیص Route ندارد.

---

## لایسنس

این پروژه تحت لایسنس MIT منتشر شده است. برای جزئیات فایل [LICENSE](LICENSE) را ببینید.

قطعات شخص ثالث، در صورت اضافه شدن، تحت لایسنس‌های خودشان باقی می‌مانند.

---

## سلب مسئولیت

این ابزار برای تست داخلی و مدیریت قانونی شبکه محلی طراحی شده است. فقط روی شبکه‌ها و دستگاه‌هایی استفاده کنید که مالک آن هستید یا اجازه مدیریت آن‌ها را دارید. نویسنده مسئول تنظیمات اشتباه شبکه، از دست رفتن داده یا سوءاستفاده از برنامه نیست.
