from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from .models import Complaint


def detect_potential_duplicates(category, city, area, address, exclude_id=None, days_threshold=30):
    """
    Identifies potential duplicate complaints based on:
    - Same Category
    - Same City
    - Similar / matching Area or matching Address tokens
    - Filed within the last `days_threshold` days and not yet rejected
    """
    cutoff_date = timezone.now() - timedelta(days=days_threshold)

    qs = Complaint.objects.filter(
        category=category,
        city__iexact=city.strip(),
        created_at__gte=cutoff_date
    ).exclude(status='Rejected')

    if exclude_id:
        qs = qs.exclude(id=exclude_id)

    # Clean and split area words for keyword matching
    area_clean = area.strip().lower()
    area_tokens = [w for w in area_clean.replace(',', ' ').split() if len(w) > 3]

    matching_ids = []
    for complaint in qs:
        comp_area = complaint.area.strip().lower()
        # Direct exact match or substring match
        if area_clean == comp_area or area_clean in comp_area or comp_area in area_clean:
            matching_ids.append(complaint.id)
            continue

        # Token intersection
        comp_tokens = [w for w in comp_area.replace(',', ' ').split() if len(w) > 3]
        common = set(area_tokens).intersection(set(comp_tokens))
        if common:
            matching_ids.append(complaint.id)
            continue

        # Check address match if address is given
        if address and complaint.address:
            addr_tokens = set([w for w in address.lower().replace(',', ' ').split() if len(w) > 4])
            c_addr_tokens = set([w for w in complaint.address.lower().replace(',', ' ').split() if len(w) > 4])
            if len(addr_tokens.intersection(c_addr_tokens)) >= 2:
                matching_ids.append(complaint.id)

    return Complaint.objects.filter(id__in=matching_ids)
