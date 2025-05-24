from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'your-secret-key'  # <<<< โปรดเปลี่ยนค่านี้เมื่อ Deploy จริง
DEBUG = True
ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your apps
    'clothes',
    'django.contrib.humanize',

    # Allauth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',  # For social authentication
    'allauth.socialaccount.providers.google',  # For Google provider
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'allauth.account.middleware.AccountMiddleware', # Allauth Account Middleware
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Required by allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/stable/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
] # คุณสามารถเปิดใช้งาน validators เหล่านี้ได้ในภายหลัง

# Internationalization
# https://docs.djangoproject.com/en/stable/topics/i18n/

LANGUAGE_CODE = 'th' # เปลี่ยนเป็น 'th' ถ้าเนื้อหาส่วนใหญ่เป็นภาษาไทย
TIME_ZONE = 'Asia/Bangkok'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

# Media files (User uploaded content)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/stable/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django Allauth settings
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1 # จำเป็นสำหรับ django.contrib.sites และ allauth

LOGIN_URL = 'clothes:login' # หรือ 'account_login' ถ้าใช้ URL ของ allauth โดยตรง
LOGIN_REDIRECT_URL = 'clothes:home'
LOGOUT_REDIRECT_URL = 'clothes:welcome' # หรือ 'account_logout'

# Allauth Account settings (ตัวอย่างการตั้งค่าเพิ่มเติม)
ACCOUNT_EMAIL_VERIFICATION = 'optional' # ('mandatory', 'optional', or 'none')
ACCOUNT_AUTHENTICATION_METHOD = 'username_email' # ('username', 'email', or 'username_email')
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True # ตั้งเป็น False ถ้าไม่ต้องการให้มี username แยกต่างหาก (ใช้ email เป็น username)
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_SESSION_REMEMBER = True # ให้จำ session ของ user
# ACCOUNT_UNIQUE_EMAIL = True # บังคับให้ email ไม่ซ้ำกัน (allauth จัดการให้โดย default)
# ACCOUNT_LOGOUT_ON_GET = True # (พิจารณาเรื่องความปลอดภัย ถ้าเปิดใช้)

# Allauth SocialAccount settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the client_id and secret to the
        # database, or define these settings:
        # 'APP': {
        #     'client_id': 'YOUR_GOOGLE_CLIENT_ID_FROM_GOOGLE_CONSOLE',
        #     'secret': 'YOUR_GOOGLE_CLIENT_SECRET_FROM_GOOGLE_CONSOLE',
        #     'key': '' # Usually not needed for Google
        # },
        # These SCOPE and AUTH_PARAMS are defaults and usually work well.
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        # เพิ่มการตั้งค่าเพิ่มเติมตามต้องการ เช่น
        # 'EMAIL_AUTHENTICATION': True, # ถ้าต้องการให้ login ด้วย email จาก Google โดยตรง
        # 'VERIFIED_EMAIL': True, # บังคับว่า email จาก Google ต้อง verified แล้ว
    }
}

# (แนะนำ) ถ้าต้องการให้สมัครสมาชิกอัตโนมัติเมื่อ login ผ่าน social ครั้งแรก
# SOCIALACCOUNT_AUTO_SIGNUP = True
# SOCIALACCOUNT_EMAIL_VERIFICATION = 'none' # ถ้า auto signup อาจจะไม่ต้องการให้ verify email อีก
# SOCIALACCOUNT_EMAIL_REQUIRED = ACCOUNT_EMAIL_REQUIRED

# (แนะนำ) ถ้าต้องการให้ user กรอก username เองหลังจาก social signup
# SOCIALACCOUNT_ADAPTER = 'your_project.adapter.SocialAccountAdapter' # คุณจะต้องสร้าง adapter นี้เอง
