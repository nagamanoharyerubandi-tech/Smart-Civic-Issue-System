from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Category, Department, Complaint, ComplaintAssignment, ComplaintStatusHistory
from .utils import detect_potential_duplicates
from feedback.models import Feedback
from notifications.models import Notification


class SmartCivicSystemTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Category
        self.category = Category.objects.create(
            name='Road Damage & Potholes',
            slug='road-damage-potholes',
            icon='bi-cone-striped',
            color='#d97706',
            description='Potholes and broken roads',
            is_active=True
        )

        # Create Department
        self.department = Department.objects.create(
            name='Public Works Department',
            code='PWD-ROADS',
            head_officer_name='Er. Ramesh Gupta',
            email='pwd@smartcivic.local',
            phone='+91 11 2345 6701',
            is_active=True
        )

        # Create Citizen User
        self.citizen = User.objects.create_user(
            username='test_citizen',
            email='citizen@test.local',
            password='testpassword123',
            first_name='Test',
            last_name='Citizen'
        )
        self.citizen.profile.role = 'citizen'
        self.citizen.profile.city = 'Metropolis City'
        self.citizen.profile.save()

        # Create Admin User
        self.admin = User.objects.create_user(
            username='test_admin',
            email='admin@test.local',
            password='adminpassword123',
            first_name='Admin',
            last_name='Officer',
            is_staff=True,
            is_superuser=True
        )
        self.admin.profile.role = 'admin'
        self.admin.profile.save()

    def test_complaint_creation_and_reference_id(self):
        """Test complaint creation generates auto-formatted reference number and initial history."""
        complaint = Complaint.objects.create(
            citizen=self.citizen,
            category=self.category,
            title='Severe pothole near Metro station',
            description='Deep pothole damaging vehicles and causing traffic slowdown.',
            city='Metropolis City',
            area='Ward 7, MG Road',
            address='Opposite Pillar 100',
            priority='High',
            status='Submitted'
        )

        self.assertIsNotNone(complaint.reference_id)
        self.assertTrue(complaint.reference_id.startswith('CIV-'))
        self.assertEqual(complaint.status, 'Submitted')
        self.assertTrue(complaint.is_cancellable)

    def test_duplicate_detection(self):
        """Test that duplicate complaints with matching category, city, and area are detected."""
        comp1 = Complaint.objects.create(
            citizen=self.citizen,
            category=self.category,
            title='Large crater on MG Road',
            description='Vehicles skidding daily.',
            city='Metropolis City',
            area='Ward 7, MG Road',
            address='Near Pillar 110',
            status='Submitted'
        )

        duplicates = detect_potential_duplicates(
            category=self.category,
            city='Metropolis City',
            area='Ward 7, MG Road',
            address='Near Pillar 110',
            exclude_id=None
        )

        self.assertTrue(duplicates.filter(id=comp1.id).exists())

    def test_status_update_and_history(self):
        """Test status transitions update timestamp, history records, and resolution notes."""
        complaint = Complaint.objects.create(
            citizen=self.citizen,
            category=self.category,
            title='Water leakage on Main Street',
            description='Burst pipe wasting clean water.',
            city='Metropolis City',
            area='Ward 4',
            address='Plot 12',
            status='Submitted'
        )

        ComplaintStatusHistory.objects.create(
            complaint=complaint,
            status='Submitted',
            changed_by=self.citizen,
            remarks='Complaint submitted.'
        )

        # Update to Resolved
        complaint.status = 'Resolved'
        complaint.resolution_notes = 'Pipe welded and repaired.'
        complaint.save()

        ComplaintStatusHistory.objects.create(
            complaint=complaint,
            status='Resolved',
            changed_by=self.admin,
            remarks='Pipe welded and repaired.'
        )

        self.assertEqual(complaint.status_history.count(), 2)
        self.assertIsNotNone(complaint.resolved_at)

    def test_department_assignment(self):
        """Test assigning department creates ComplaintAssignment record."""
        complaint = Complaint.objects.create(
            citizen=self.citizen,
            category=self.category,
            title='Road crack',
            description='Asphalt peeling off.',
            city='Metropolis City',
            area='Ward 7',
            address='Street 5',
            status='Submitted'
        )

        assignment = ComplaintAssignment.objects.create(
            complaint=complaint,
            department=self.department,
            assigned_by=self.admin,
            instructions='Fill cracks with bitumen.',
            status='Active'
        )

        complaint.assigned_department = self.department
        complaint.status = 'Assigned'
        complaint.save()

        self.assertEqual(complaint.assigned_department, self.department)
        self.assertEqual(complaint.assignments.first().department, self.department)

    def test_feedback_submission(self):
        """Test citizen can rate resolved complaint and average rating is computed."""
        complaint = Complaint.objects.create(
            citizen=self.citizen,
            category=self.category,
            title='Pothole repair',
            description='Pothole in Ward 7',
            city='Metropolis City',
            area='Ward 7',
            address='Street 5',
            status='Resolved'
        )

        fb = Feedback.objects.create(
            complaint=complaint,
            citizen=self.citizen,
            rating=5,
            comments='Great work and quick repair!'
        )

        self.assertEqual(complaint.feedback.rating, 5)
        self.assertEqual(len(fb.stars_range), 5)
        self.assertEqual(len(fb.empty_stars_range), 0)

    def test_public_track_lookup(self):
        """Test public tracking endpoint finds complaint by reference ID."""
        complaint = Complaint.objects.create(
            citizen=self.citizen,
            category=self.category,
            title='Streetlight out',
            description='Dark road',
            city='Metropolis City',
            area='Ward 3',
            address='Lane 2',
            status='Submitted'
        )

        response = self.client.get(reverse('public_track'), {'ref': complaint.reference_id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, complaint.reference_id)
        self.assertContains(response, 'Submitted')

    def test_role_based_access(self):
        """Test citizen cannot access admin portal and gets redirected."""
        self.client.login(username='test_citizen', password='testpassword123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/citizen/dashboard/', response.url)

        # Admin can access admin portal
        self.client.logout()
        self.client.login(username='test_admin', password='adminpassword123')
        admin_response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(admin_response.status_code, 200)
        self.assertContains(admin_response, 'Municipal Control Center')
