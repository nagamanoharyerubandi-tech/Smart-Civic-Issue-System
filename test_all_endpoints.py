import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civic_management.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from complaints.models import Complaint

client = Client()

print("--- Testing Public Endpoints ---")
public_urls = ['/', '/about/', '/how-it-works/', '/contact/', '/track/', '/login/', '/register/']
for url in public_urls:
    res = client.get(url)
    assert res.status_code == 200, f"Failed {url}: {res.status_code}"
    print(f" [PASS] GET {url} -> 200")

# Test Public Track with real ref
sample_comp = Complaint.objects.first()
if sample_comp:
    res = client.get(f"/track/?ref={sample_comp.reference_id}")
    assert res.status_code == 200, f"Failed /track/ query: {res.status_code}"
    assert sample_comp.reference_id in res.content.decode()
    print(f" [PASS] GET /track/?ref={sample_comp.reference_id} -> 200 & Found")

print("\n--- Testing Citizen Endpoints ---")
citizen_user = User.objects.get(username='citizen_rahul')
client.force_login(citizen_user)

# Get a complaint submitted by citizen_rahul
rahul_comp = Complaint.objects.filter(citizen=citizen_user).first()
assert rahul_comp is not None

citizen_urls = [
    '/citizen/dashboard/',
    '/citizen/complaints/',
    '/citizen/complaints/create/',
    f'/citizen/complaints/{rahul_comp.id}/',
    f'/citizen/complaints/{rahul_comp.id}/track/',
    '/citizen/notifications/',
    '/profile/',
    '/profile/change-password/',
]

for url in citizen_urls:
    res = client.get(url)
    assert res.status_code in [200, 302], f"Failed {url}: {res.status_code}"
    print(f" [PASS] GET {url} -> {res.status_code}")

# Security check: citizen cannot view another citizen's complaint
other_comp = Complaint.objects.exclude(citizen=citizen_user).first()
if other_comp:
    blocked_res = client.get(f'/citizen/complaints/{other_comp.id}/')
    assert blocked_res.status_code == 404, "Security breach: Citizen viewed someone else's complaint!"
    print(f" [SECURITY PASS] Citizen viewing other citizen's complaint #{other_comp.id} blocked -> 404")

print("\n--- Testing Admin Endpoints ---")
admin_user = User.objects.get(username='admin')
client.force_login(admin_user)

admin_urls = [
    '/admin-portal/dashboard/',
    '/admin-portal/complaints/',
    '/admin-portal/complaints/?duplicate=yes',
    f'/admin-portal/complaints/{sample_comp.id}/',
    '/admin-portal/categories/',
    '/admin-portal/categories/create/',
    '/admin-portal/departments/',
    '/admin-portal/departments/create/',
    '/admin-portal/citizens/',
    '/admin-portal/analytics/',
    '/admin-portal/feedback/',
    '/admin-portal/notifications/',
    '/api/dashboard-charts/',
]

for url in admin_urls:
    res = client.get(url)
    assert res.status_code in [200, 302], f"Failed {url}: {res.status_code}"
    print(f" [PASS] GET {url} -> {res.status_code}")

print("\nALL 28 ENDPOINTS & SECURITY ACCESS CHECKS TESTED AND PASSED WITH 100% SUCCESS!")
