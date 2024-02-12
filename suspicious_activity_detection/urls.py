import statistics
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import predict_and_save_video, index

urlpatterns = [
    path('', index, name='index'),
    path('/predict_video', predict_and_save_video, name='predict_and_save_video'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

