from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from health_backend_app import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path("users/", include("user.urls")),
    path('wallet/', include("wallet.urls")),
    path('health/', include("health.urls")),
    path('notification/', include("notification.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)