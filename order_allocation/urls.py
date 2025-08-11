from django.contrib import admin
from django.urls import path
from allocation.views import allocate_order_view, center_analytics_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('allocate/', allocate_order_view, name='allocate_order'),
    path('analytics/', center_analytics_view, name='center_analytics'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]