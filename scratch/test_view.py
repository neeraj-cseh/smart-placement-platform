import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from core.views import VerificationDashboardView
from rest_framework.test import APIRequestFactory, force_authenticate

try:
    user = User.objects.get(email="student@prepsmart.dev")
    view = VerificationDashboardView.as_view()
    factory = APIRequestFactory()
    request = factory.get('/api/verification/')
    force_authenticate(request, user=user)
    response = view(request)
    print("STATUS CODE:", response.status_code)
    print("DATA:", response.data)
except Exception as e:
    import traceback
    print("ERROR:", str(e))
    traceback.print_exc()
