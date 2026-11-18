from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from accounts.models import Profile
from complaints.models import Category, Department, Complaint, ComplaintAssignment, ComplaintStatusHistory
from notifications.models import Notification
from feedback.models import Feedback


class Command(BaseCommand):
    help = 'Seeds database with realistic demonstration categories, departments, users, complaints, and feedback'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting Civic Data Seeding...'))

        # 1. Create or update Administrator
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@smartcivic.local',
                'first_name': 'Chief Admin',
                'last_name': 'Officer',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('adminpassword123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        admin_profile, _ = Profile.objects.get_or_create(user=admin_user)
        admin_profile.role = 'admin'
        admin_profile.phone_number = '+91 98765 00001'
        admin_profile.city = 'Metropolis City'
        admin_profile.address = 'Municipal Corporation Headquarters, Civil Lines'
        admin_profile.save()

        self.stdout.write(self.style.SUCCESS('Admin user ready: admin / adminpassword123'))

        # 2. Create Sample Citizens
        citizens_data = [
            {
                'username': 'citizen_rahul',
                'email': 'rahul.sharma@example.com',
                'first_name': 'Rahul',
                'last_name': 'Sharma',
                'phone': '+91 98234 11223',
                'city': 'Metropolis City',
                'address': 'Flat 402, Green Valley Apts, Sector 14, Rohini'
            },
            {
                'username': 'citizen_priya',
                'email': 'priya.patel@example.com',
                'first_name': 'Priya',
                'last_name': 'Patel',
                'phone': '+91 98450 33445',
                'city': 'Metropolis City',
                'address': 'B-12, Sunrise Residency, MG Road, Ward 7'
            },
            {
                'username': 'citizen_amit',
                'email': 'amit.verma@example.com',
                'first_name': 'Amit',
                'last_name': 'Verma',
                'phone': '+91 97110 55667',
                'city': 'Metropolis City',
                'address': 'Plot 89, Shivaji Nagar, Sector 5'
            },
            {
                'username': 'citizen_sneha',
                'email': 'sneha.iyer@example.com',
                'first_name': 'Sneha',
                'last_name': 'Iyer',
                'phone': '+91 99220 77889',
                'city': 'Metropolis City',
                'address': 'C-304, Palm Grove, Lake View Road, Ward 12'
            },
        ]

        citizen_users = []
        for cdata in citizens_data:
            c_user, _ = User.objects.get_or_create(
                username=cdata['username'],
                defaults={
                    'email': cdata['email'],
                    'first_name': cdata['first_name'],
                    'last_name': cdata['last_name'],
                }
            )
            c_user.set_password('citizen123')
            c_user.save()

            c_prof, _ = Profile.objects.get_or_create(user=c_user)
            c_prof.role = 'citizen'
            c_prof.phone_number = cdata['phone']
            c_prof.city = cdata['city']
            c_prof.address = cdata['address']
            c_prof.save()
            citizen_users.append(c_user)

        self.stdout.write(self.style.SUCCESS(f'Created {len(citizen_users)} citizens (password: citizen123)'))

        # 3. Create Categories
        categories_data = [
            {
                'name': 'Road Damage & Potholes',
                'slug': 'road-damage-potholes',
                'icon': 'bi-cone-striped',
                'color': '#d97706',
                'description': 'Reports of craters, dangerous potholes, broken asphalt, and road divider hazards.'
            },
            {
                'name': 'Garbage Accumulation',
                'slug': 'garbage-accumulation',
                'icon': 'bi-trash3-fill',
                'color': '#16a34a',
                'description': 'Overflowing municipal dumpsters, uncleared roadside trash, and open dumping.'
            },
            {
                'name': 'Water Leakage & Pipe Burst',
                'slug': 'water-leakage-pipe-burst',
                'icon': 'bi-droplet-half',
                'color': '#0284c7',
                'description': 'Underground main line bursts, leaking public valves, and treated water wastage.'
            },
            {
                'name': 'Drainage & Sewage Problems',
                'slug': 'drainage-sewage-problems',
                'icon': 'bi-water',
                'color': '#7c3aed',
                'description': 'Choked stormwater drains, overflowing manholes, backflow, and open gutters.'
            },
            {
                'name': 'Streetlight Failures',
                'slug': 'streetlight-failures',
                'icon': 'bi-lightbulb-fill',
                'color': '#eab308',
                'description': 'Non-functioning street lamps, flickering lights, exposed electrical wiring.'
            },
            {
                'name': 'Public Sanitation & Toilets',
                'slug': 'public-sanitation-toilets',
                'icon': 'bi-shield-check',
                'color': '#0d9488',
                'description': 'Unclean community restrooms, lack of running water, damaged sanitary fittings.'
            },
            {
                'name': 'Drinking Water Shortages',
                'slug': 'drinking-water-shortages',
                'icon': 'bi-cup-straw',
                'color': '#2563eb',
                'description': 'Low pressure or zero water supply in municipal feeder pipelines, tanker requests.'
            },
        ]

        categories_map = {}
        for cat in categories_data:
            c_obj, _ = Category.objects.update_or_create(
                slug=cat['slug'],
                defaults={
                    'name': cat['name'],
                    'icon': cat['icon'],
                    'color': cat['color'],
                    'description': cat['description'],
                    'is_active': True,
                }
            )
            categories_map[cat['slug']] = c_obj

        # 4. Create Departments
        departments_data = [
            {
                'name': 'Public Works Department (Civil)',
                'code': 'PWD-ROADS',
                'head': 'Er. Ramesh Gupta (Chief Engineer)',
                'email': 'pwd.roads@smartcivic.local',
                'phone': '+91 11 2345 6701',
                'desc': 'Oversees road resurfacing, pothole repairs, bridges, footpaths and pedestrian infrastructure.'
            },
            {
                'name': 'Solid Waste Management Wing',
                'code': 'SWM-CLEAN',
                'head': 'Smt. Sunita Rao (Director Sanitation)',
                'email': 'swm.sanitation@smartcivic.local',
                'phone': '+91 11 2345 6702',
                'desc': 'Daily municipal solid waste collection, dumpsters, recycling operations and roadside cleanup.'
            },
            {
                'name': 'Water Supply & Sewerage Board',
                'code': 'WSSB-WATER',
                'head': 'Er. K. Venkatesh (Superintending Engineer)',
                'email': 'water.board@smartcivic.local',
                'phone': '+91 11 2345 6703',
                'desc': 'Safe drinking water delivery, pipe repair, sewer line maintenance and water treatment.'
            },
            {
                'name': 'Electrical & Street Lighting Wing',
                'code': 'ESLW-POWER',
                'head': 'Er. Vikram Malhotra (Executive Engineer)',
                'email': 'electrical@smartcivic.local',
                'phone': '+91 11 2345 6704',
                'desc': 'Installation, repair, and smart monitoring of public streetlights, timers and wiring.'
            },
            {
                'name': 'Public Health & Sanitation Bureau',
                'code': 'PHSB-HEALTH',
                'head': 'Dr. Anita Deshmukh (Health Officer)',
                'email': 'publichealth@smartcivic.local',
                'phone': '+91 11 2345 6705',
                'desc': 'Public hygiene inspection, public comfort stations, pest control and sanitization drives.'
            },
        ]

        departments_map = {}
        for dep in departments_data:
            d_obj, _ = Department.objects.update_or_create(
                code=dep['code'],
                defaults={
                    'name': dep['name'],
                    'head_officer_name': dep['head'],
                    'email': dep['email'],
                    'phone': dep['phone'],
                    'description': dep['desc'],
                    'is_active': True,
                }
            )
            departments_map[dep['code']] = d_obj

        # 5. Create Sample Complaints across statuses & dates
        now = timezone.now()
        complaints_specs = [
            # 1. Road Damage - Resolved
            {
                'citizen': citizen_users[0],
                'category': categories_map['road-damage-potholes'],
                'title': 'Dangerous deep pothole on MG Road junction near Metro Pillar 114',
                'description': 'A massive 2-foot wide pothole has formed right in the middle of the bus lane. Multiple two-wheelers have skidded here during evening hours. Needs urgent cold mix asphalt filling.',
                'city': 'Metropolis City',
                'area': 'Ward 7, MG Road Corridor',
                'address': 'Opposite City Center Mall, Near Pillar 114, MG Road',
                'landmark': 'Next to Metro Pillar 114',
                'priority': 'High',
                'status': 'Resolved',
                'department': departments_map['PWD-ROADS'],
                'days_ago': 14,
                'resolved_days_ago': 2,
                'resolution_notes': 'PWD Mobile Repair Van dispatched with hot-mix bituminous batch. Pothole filled, leveled, and road compacted smoothly.',
                'feedback_rating': 5,
                'feedback_comments': 'Incredible turnaround! The pothole was repaired cleanly within 48 hours. Commute is now completely safe. Kudos to the team!'
            },
            # 2. Garbage Accumulation - In Progress
            {
                'citizen': citizen_users[1],
                'category': categories_map['garbage-accumulation'],
                'title': 'Huge garbage accumulation at Shivaji Nagar market entrance',
                'description': 'Municipal community bin has been overflowing for the last four days. Garbage has spilled over onto the pedestrian walkway, causing severe foul smell and stray animal menace.',
                'city': 'Metropolis City',
                'area': 'Ward 5, Shivaji Nagar',
                'address': 'Gate No. 2, Shivaji Wholesale Veg Market',
                'landmark': 'Opposite Old Police Chowki',
                'priority': 'High',
                'status': 'In Progress',
                'department': departments_map['SWM-CLEAN'],
                'days_ago': 5,
                'resolved_days_ago': None,
                'resolution_notes': 'Sanitation supervisor deployed hydraulic compacting truck. Secondary clearing underway.',
                'feedback_rating': None,
                'feedback_comments': None
            },
            # 3. Water Leakage - Assigned
            {
                'citizen': citizen_users[2],
                'category': categories_map['water-leakage-pipe-burst'],
                'title': 'Continuous water pipeline leak flooding 4th Cross Road',
                'description': 'Treated drinking water pipeline under pavement is leaking continuously at high pressure. Gallons of clean water wasted and creating waterlogging.',
                'city': 'Metropolis City',
                'area': 'Ward 14, Rohini Sector 14',
                'address': 'Near House #24, 4th Cross Road',
                'landmark': 'Near Community Park North Gate',
                'priority': 'Medium',
                'status': 'Assigned',
                'department': departments_map['WSSB-WATER'],
                'days_ago': 3,
                'resolved_days_ago': None,
                'resolution_notes': '',
                'feedback_rating': None,
                'feedback_comments': None
            },
            # 4. Streetlight Failures - Under Review
            {
                'citizen': citizen_users[3],
                'category': categories_map['streetlight-failures'],
                'title': 'Complete row of 6 streetlights dead on Lake View Promenade',
                'description': 'Entire 300-meter stretch of the pedestrian promenade has been pitch dark for three nights due to a faulty phase breaker or blown fuses. Unsafe for women and evening walkers.',
                'city': 'Metropolis City',
                'area': 'Ward 12, Lake View',
                'address': 'Promenade Walkway between Boat Club and Watchtower',
                'landmark': 'Near Sunset Point Garden',
                'priority': 'Medium',
                'status': 'Under Review',
                'department': None,
                'days_ago': 2,
                'resolved_days_ago': None,
                'resolution_notes': '',
                'feedback_rating': None,
                'feedback_comments': None
            },
            # 5. Drainage & Sewage - Submitted
            {
                'citizen': citizen_users[0],
                'category': categories_map['drainage-sewage-problems'],
                'title': 'Choked sewer line overflowing back into residential lane',
                'description': 'Heavy sewage blockage in the municipal sewer main. Dirty water is bubbling up from the storm grate and spreading foul stench into nearby ground floor residences.',
                'city': 'Metropolis City',
                'area': 'Ward 7, MG Road Corridor',
                'address': 'Lane 3, Behind City Hospital Annex',
                'landmark': 'Beside Govt Primary Dispensary',
                'priority': 'High',
                'status': 'Submitted',
                'department': None,
                'days_ago': 1,
                'resolved_days_ago': None,
                'resolution_notes': '',
                'feedback_rating': None,
                'feedback_comments': None
            },
            # 6. Drinking Water Shortage - Resolved
            {
                'citizen': citizen_users[1],
                'category': categories_map['drinking-water-shortages'],
                'title': 'Zero municipal water supply in Sunrise Residency for 4 consecutive days',
                'description': 'Pipeline valve issue upstream cut off drinking supply to 200+ households. Residents are forced to purchase private tankers at exorbitant prices.',
                'city': 'Metropolis City',
                'area': 'Ward 7, MG Road Corridor',
                'address': 'Sunrise Residency Block A & B, MG Road Ward 7',
                'landmark': 'Behind St. Jude High School',
                'priority': 'High',
                'status': 'Resolved',
                'department': departments_map['WSSB-WATER'],
                'days_ago': 20,
                'resolved_days_ago': 15,
                'resolution_notes': 'Main line sluice valve was clogged with silt deposit. Sluice valve flushed, pressure restored to 2.2 bar across Sector 7.',
                'feedback_rating': 4,
                'feedback_comments': 'Water supply returned to normal pressure within 3 days. Good response from the water board.'
            },
            # 7. Public Sanitation - Rejected
            {
                'citizen': citizen_users[2],
                'category': categories_map['public-sanitation-toilets'],
                'title': 'Private commercial mall washroom charging entry fee',
                'description': 'Private shopping complex in Sector 18 is charging Rs. 20 for washroom access. Please fine them.',
                'city': 'Metropolis City',
                'area': 'Ward 18, Commercial Zone',
                'address': 'Galaxy Mega Mall, 3rd Floor Food Court',
                'landmark': 'Galaxy Mall Sector 18',
                'priority': 'Low',
                'status': 'Rejected',
                'department': None,
                'days_ago': 8,
                'resolved_days_ago': None,
                'resolution_notes': 'Complaint falls outside municipal jurisdiction. Galaxy Mall is a privately managed enterprise; civic regulations apply solely to public/community municipal restrooms.',
                'feedback_rating': None,
                'feedback_comments': None
            },
            # 8. Duplicate Pair: Road Damage on MG Road
            {
                'citizen': citizen_users[3],
                'category': categories_map['road-damage-potholes'],
                'title': 'Huge road depression and pothole near Metro Pillar 115 MG Road',
                'description': 'There is a severe crater near Metro Pillar 114/115 on MG Road creating heavy traffic jams and hazard.',
                'city': 'Metropolis City',
                'area': 'Ward 7, MG Road Corridor',
                'address': 'MG Road near Pillar 114-115, Ward 7',
                'landmark': 'Near Pillar 115',
                'priority': 'Medium',
                'status': 'Submitted',
                'department': None,
                'days_ago': 0,
                'resolved_days_ago': None,
                'resolution_notes': '',
                'feedback_rating': None,
                'feedback_comments': None,
                'is_duplicate_flag': True
            }
        ]

        created_complaints = []
        for i, spec in enumerate(complaints_specs):
            created_time = now - timedelta(days=spec['days_ago'], hours=2 * i)
            complaint = Complaint(
                citizen=spec['citizen'],
                category=spec['category'],
                title=spec['title'],
                description=spec['description'],
                city=spec['city'],
                area=spec['area'],
                address=spec['address'],
                landmark=spec['landmark'],
                priority=spec['priority'],
                status=spec['status'],
                assigned_department=spec['department'],
                resolution_notes=spec['resolution_notes'],
            )
            complaint.save()

            # Overwrite auto_now_add timestamps for historical graphing
            Complaint.objects.filter(pk=complaint.pk).update(created_at=created_time)
            complaint.refresh_from_db()

            if spec['status'] == 'Resolved' and spec['resolved_days_ago'] is not None:
                res_time = now - timedelta(days=spec['resolved_days_ago'])
                Complaint.objects.filter(pk=complaint.pk).update(resolved_at=res_time)
                complaint.refresh_from_db()

            # Add status history
            ComplaintStatusHistory.objects.create(
                complaint=complaint,
                status='Submitted',
                changed_by=spec['citizen'],
                remarks='Complaint registered by citizen via online portal.',
                changed_at=created_time
            )

            if spec['status'] in ['Under Review', 'Assigned', 'In Progress', 'Resolved']:
                review_time = created_time + timedelta(hours=6)
                ComplaintStatusHistory.objects.create(
                    complaint=complaint,
                    status='Under Review',
                    changed_by=admin_user,
                    remarks='Complaint reviewed by municipal dispatch officer.',
                    changed_at=review_time
                )

            if spec['department']:
                assign_time = created_time + timedelta(hours=14)
                ComplaintAssignment.objects.create(
                    complaint=complaint,
                    department=spec['department'],
                    assigned_by=admin_user,
                    assigned_at=assign_time,
                    instructions='Inspect site promptly and resolve issue within standard SLA.',
                    target_completion_date=(assign_time + timedelta(days=3)).date(),
                    status='Active' if spec['status'] != 'Resolved' else 'Completed'
                )
                ComplaintStatusHistory.objects.create(
                    complaint=complaint,
                    status='Assigned',
                    changed_by=admin_user,
                    remarks=f"Complaint formally assigned to {spec['department'].name}.",
                    changed_at=assign_time
                )

            if spec['status'] in ['In Progress', 'Resolved']:
                prog_time = created_time + timedelta(hours=24)
                ComplaintStatusHistory.objects.create(
                    complaint=complaint,
                    status='In Progress',
                    changed_by=admin_user,
                    remarks='Field maintenance crew on-site with required machinery.',
                    changed_at=prog_time
                )

            if spec['status'] == 'Resolved':
                res_time = complaint.resolved_at or (created_time + timedelta(days=2))
                ComplaintStatusHistory.objects.create(
                    complaint=complaint,
                    status='Resolved',
                    changed_by=admin_user,
                    remarks=spec['resolution_notes'],
                    changed_at=res_time
                )

                # Create feedback if specified
                if spec['feedback_rating']:
                    Feedback.objects.create(
                        complaint=complaint,
                        citizen=spec['citizen'],
                        rating=spec['feedback_rating'],
                        comments=spec['feedback_comments'],
                        created_at=res_time + timedelta(hours=4)
                    )

            if spec['status'] == 'Rejected':
                rej_time = created_time + timedelta(hours=8)
                ComplaintStatusHistory.objects.create(
                    complaint=complaint,
                    status='Rejected',
                    changed_by=admin_user,
                    remarks=spec['resolution_notes'],
                    changed_at=rej_time
                )

            # Notifications
            Notification.objects.create(
                recipient=spec['citizen'],
                title=f"Complaint Registered: {complaint.reference_id}",
                message=f"Your complaint '{complaint.title}' has been successfully logged with status '{complaint.status}'.",
                notification_type='status_change',
                complaint=complaint,
                action_url=f"/citizen/complaints/{complaint.id}/"
            )

            if spec['status'] == 'Resolved':
                Notification.objects.create(
                    recipient=spec['citizen'],
                    title=f"Complaint Resolved: {complaint.reference_id}",
                    message="Your issue has been marked Resolved by the Municipal Department. Please share your feedback!",
                    notification_type='resolution',
                    complaint=complaint,
                    action_url=f"/citizen/feedback/{complaint.id}/"
                )

            created_complaints.append(complaint)

        # Flag the duplicate pair
        first_road_comp = created_complaints[0]
        duplicate_road_comp = created_complaints[-1]
        duplicate_road_comp.is_duplicate = True
        duplicate_road_comp.duplicate_of = first_road_comp
        duplicate_road_comp.duplicate_flagged_at = now
        duplicate_road_comp.save()

        Notification.objects.create(
            recipient=admin_user,
            title=f"Potential Duplicate Alert: {duplicate_road_comp.reference_id}",
            message=f"A complaint in {duplicate_road_comp.area} matches previous complaint {first_road_comp.reference_id}.",
            notification_type='duplicate_flag',
            complaint=duplicate_road_comp,
            action_url=f"/admin-portal/complaints/{duplicate_road_comp.id}/"
        )

        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(created_complaints)} realistic complaints with histories!'))
        self.stdout.write(self.style.SUCCESS('Seeding complete!'))
