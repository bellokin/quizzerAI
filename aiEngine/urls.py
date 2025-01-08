from django.urls import path
from . import views  # Import views from the `aiEngine` app

urlpatterns = [
    path('', views.index, name='index'),  # Root path for `aiEngine`
    path('articleLoad', views.take_in_article, name='take_in_article'),  # Example route
    # Uncomment and adjust other routes as needed
    # path('compareCompatibility/', views.predict_compatibility, name='predict_compatibility'),
    # path('sendMail/', views.send_email, name='send_email'),
]
