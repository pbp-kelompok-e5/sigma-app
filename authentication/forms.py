# Import Django forms module untuk membuat form
from django import forms
# Import form bawaan Django untuk registrasi dan autentikasi
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# Import model User bawaan Django
from django.contrib.auth.models import User
# Import model custom dari aplikasi authentication
from .models import UserProfile, SportPreference
# Import konstanta pilihan kota dari aplikasi utama
from sigma_app.constants import CITY_CHOICES
# Import validator untuk membatasi panjang karakter
from django.core.validators import MaxLengthValidator


class CustomUserCreationForm(UserCreationForm):
    """
    Form registrasi user dengan field tambahan untuk profil.
    Extends UserCreationForm bawaan Django dengan menambahkan field:
    - email, first_name, last_name (untuk User model)
    - city, bio, profile_image_url (untuk UserProfile model)
    """

    # Field email - wajib diisi, dengan placeholder untuk UX yang lebih baik
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'})
    )

    # Field nama depan - maksimal 30 karakter, wajib diisi
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'})
    )

    # Field nama belakang - maksimal 30 karakter, wajib diisi
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your last name'})
    )

    # Field pilihan kota - menggunakan choices dari CITY_CHOICES
    city = forms.ChoiceField(
        choices=CITY_CHOICES,
        required=True,
        widget=forms.Select(attrs={'data-placeholder': 'Search and select your city'})
    )

    # Field bio/deskripsi diri - opsional, maksimal 200 karakter
    bio = forms.CharField(
        validators=[MaxLengthValidator(200)],
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Tell us about yourself (optional)', 'rows': 3})
    )

    # Field URL gambar profil - opsional, user memberikan URL gambar
    profile_image_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'placeholder': 'Enter profile image URL (optional)'})
    )

    class Meta:
        # Model yang akan digunakan adalah User bawaan Django
        model = User
        # Field yang akan ditampilkan di form (dari User model)
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        # Widget custom untuk field username
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose a username'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Constructor untuk menambahkan placeholder pada field password.
        Password fields tidak bisa di-customize di Meta class, jadi dilakukan di __init__
        """
        super().__init__(*args, **kwargs)
        # Tambahkan placeholder untuk field password1 (password)
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter your password'})
        # Tambahkan placeholder untuk field password2 (konfirmasi password)
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm your password'})

    def save(self, commit=True):
        """
        Override method save untuk menyimpan data User dan UserProfile sekaligus.

        Args:
            commit (bool): Jika True, langsung save ke database. Jika False, return object tanpa save.

        Returns:
            User: Instance user yang telah dibuat
        """
        # Panggil save dari parent class (UserCreationForm) tapi jangan commit dulu
        user = super().save(commit=False)
        # Set field email, first_name, last_name dari cleaned_data
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        # Jika commit=True, simpan user dan buat profile-nya
        if commit:
            user.save()
            # Buat atau ambil UserProfile untuk user ini
            # get_or_create mengembalikan tuple (object, created)
            profile, created = UserProfile.objects.get_or_create(user=user)
            # Set field-field profile dari cleaned_data
            profile.full_name = f"{user.first_name} {user.last_name}"
            profile.city = self.cleaned_data['city']
            profile.bio = self.cleaned_data['bio']
            profile.profile_image_url = self.cleaned_data['profile_image_url']
            # Simpan profile ke database
            profile.save()

        return user


class CustomAuthenticationForm(AuthenticationForm):
    """
    Form login custom dengan placeholder untuk UX yang lebih baik.
    Extends AuthenticationForm bawaan Django.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor untuk menambahkan placeholder pada field username dan password.
        """
        super().__init__(*args, **kwargs)
        # Tambahkan placeholder untuk field username
        self.fields['username'].widget.attrs.update({'placeholder': 'Enter your username'})
        # Tambahkan placeholder untuk field password
        self.fields['password'].widget.attrs.update({'placeholder': 'Enter your password'})


class UserProfileForm(forms.ModelForm):
    """
    Form untuk mengedit profil user.
    Menggabungkan field dari User model (first_name, last_name, email)
    dan UserProfile model (bio, city, profile_image_url).
    """

    # Field nama depan - dari User model, wajib diisi
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'})
    )

    # Field nama belakang - dari User model, wajib diisi
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your last name'})
    )

    # Field email - dari User model, wajib diisi
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'})
    )

    class Meta:
        # Model yang digunakan adalah UserProfile
        model = UserProfile
        # Field yang akan ditampilkan dari UserProfile model
        fields = ['bio', 'city', 'profile_image_url']
        # Widget custom untuk setiap field
        widgets = {
            'bio': forms.Textarea(attrs={'placeholder': 'Tell us about yourself', 'rows': 4}),
            'city': forms.Select(attrs={'data-placeholder': 'Search and select your city'}),
            'profile_image_url': forms.URLInput(attrs={'placeholder': 'Enter profile image URL (optional)'})
        }

    def __init__(self, *args, **kwargs):
        """
        Constructor untuk mengambil user instance dan set initial values.

        Args:
            user: Instance User yang akan diedit (diambil dari kwargs)
        """
        # Pop 'user' dari kwargs sebelum memanggil super().__init__
        # karena ModelForm tidak menerima parameter 'user'
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Jika user ada, set initial value untuk field User model
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        """
        Override method save untuk menyimpan data User dan UserProfile sekaligus.

        Args:
            commit (bool): Jika True, langsung save ke database

        Returns:
            UserProfile: Instance profile yang telah diupdate
        """
        # Panggil save dari parent class tapi jangan commit dulu
        profile = super().save(commit=False)

        # Jika user ada, update field User model dan full_name di profile
        if self.user:
            # Update field di User model
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']

            # Update full_name di UserProfile berdasarkan first_name dan last_name
            profile.full_name = f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}"

            # Jika commit=True, simpan User dan UserProfile ke database
            if commit:
                self.user.save()
                profile.save()

        return profile


class SportPreferenceForm(forms.ModelForm):
    """
    Form untuk menambah/mengedit preferensi olahraga user.
    User bisa memilih jenis olahraga dan tingkat skill mereka.
    """

    class Meta:
        # Model yang digunakan adalah SportPreference
        model = SportPreference
        # Field yang akan ditampilkan: jenis olahraga dan tingkat skill
        fields = ['sport_type', 'skill_level']

    def __init__(self, *args, **kwargs):
        """
        Constructor untuk mengambil user instance.

        Args:
            user: Instance User yang akan ditambahkan preferensi olahraganya
        """
        # Pop 'user' dari kwargs sebelum memanggil super().__init__
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        Override method save untuk set user pada SportPreference.

        Args:
            commit (bool): Jika True, langsung save ke database

        Returns:
            SportPreference: Instance preferensi olahraga yang telah dibuat/diupdate
        """
        # Panggil save dari parent class tapi jangan commit dulu
        preference = super().save(commit=False)

        # Jika user ada, set user pada preference
        if self.user:
            preference.user = self.user

        # Jika commit=True, simpan preference ke database
        if commit:
            preference.save()

        return preference