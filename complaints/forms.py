from django import forms
from django.core.exceptions import ValidationError
from PIL import Image
from .models import Complaint, Category, Department, ComplaintAssignment


class ComplaintSubmitForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        empty_label="-- Select Complaint Category --",
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'})
    )
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'E.g., Severe waterlogging and broken drainage near Bus Stop'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Provide detailed information about the issue, severity, duration, and impact on public safety...'
        })
    )
    city = forms.CharField(
        max_length=100,
        initial='Metropolis City',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'})
    )
    area = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ward / Neighborhood (e.g. Ward 7, MG Road)'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Exact Street Address, House / Plot Number, or Road Stretch'
        })
    )
    landmark = forms.CharField(
        required=False,
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nearby prominent landmark (e.g. Opposite Metro Pillar 114)'})
    )
    photograph = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )
    latitude = forms.DecimalField(
        required=False,
        widget=forms.HiddenInput()
    )
    longitude = forms.DecimalField(
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Complaint
        fields = (
            'category', 'title', 'description', 'city', 'area',
            'address', 'landmark', 'photograph', 'latitude', 'longitude'
        )

    def clean_photograph(self):
        photo = self.cleaned_data.get('photograph')
        if photo:
            # Check file size (5MB max)
            if photo.size > 5 * 1024 * 1024:
                raise ValidationError("Image file size must not exceed 5MB.")
            # Validate image integrity using Pillow
            try:
                img = Image.open(photo)
                img.verify()
            except Exception:
                raise ValidationError("The uploaded file is not a valid image.")
        return photo


class ComplaintStatusUpdateForm(forms.Form):
    status = forms.ChoiceField(
        choices=Complaint.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    priority = forms.ChoiceField(
        choices=Complaint.PRIORITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    remarks = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter operational notes, field inspection feedback, or resolution details...'
        })
    )


class ComplaintAssignDepartmentForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        empty_label="-- Select Department --",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Specific administrative instructions or dispatch guidelines...'
        })
    )
    target_completion_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    class Meta:
        model = ComplaintAssignment
        fields = ('department', 'instructions', 'target_completion_date')


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'icon', 'color', 'description', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bootstrap icon e.g. bi-cone-striped'}),
            'color': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ('name', 'code', 'head_officer_name', 'email', 'phone', 'description', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department Name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g. PWD-ROADS'}),
            'head_officer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Designated Officer Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'department@smartcivic.local'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 11 2345 6789'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
