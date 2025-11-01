# Panduan Git Workflow - BondUp

> [!IMPORTANT]
> **Setiap anggota tim mengerjakan fitur di branch masing-masing! (/name)**

---

## 🏃‍♂️ Tentang BondUp

**BondUp** adalah platform berbasis web yang menggabungkan konsep Sport Meetup dan Tinder for Friends, dirancang untuk membantu kamu membangun koneksi yang lebih kuat melalui olahraga.

Setiap interaksi, pertandingan, dan event di BondUp bukan hanya tentang bermain — tapi tentang terhubung, berkembang, dan menikmati energi positif bersama orang-orang dengan minat yang sama.

✨ “Where connections grow stronger through play.”

### 🎯 Fitur Utama

- **Profile Management**: Kelola profil dan preferensi olahraga
- **Partner Matching**: Temukan partner olahraga berdasarkan minat dan lokasi
- **Event Discovery**: Jelajahi event olahraga di kotamu
- **Event Creation**: Buat dan kelola event sendiri
- **Review System**: Berikan feedback setelah event
- **Leaderboard**: Kompetisi sehat melalui ranking points

### 💡 Cara Kerja

1. **Register** - Daftar dengan data olahraga favorit dan lokasi
2. **Find Partners** - Browse dan connect dengan teman berolahraga
3. **Join/Create Events** - Ikuti event atau buat event sendiri
4. **Play Together** - Bertemu dan berolahraga bersama
5. **Give Reviews** - Berikan feedback post-event
6. **Earn Points** - Naik ranking di leaderboard

---

## 📦 Pembagian Modul (6 Modul dengan Relasi)

**Note:** Konstanta seperti `SPORT_CHOICES`, `SKILL_CHOICES`, dan `CITY_CHOICES` didefinisikan di `sigma_app/constants.py` untuk konsistensi di seluruh aplikasi.

---

### Modul 1: Authentication & User Profile

**Tanggung Jawab:**
- Autentikasi user (register, login, logout)
- Manajemen profil user
- Data preferensi olahraga

**Fitur:**
- Register (nama, email, password, foto, kota)
- Login & Logout
- View Profile (public & private)
- Edit Profile
  - Update foto profil
  - Edit bio
  - Update kota
- Sport Preferences
  - Add/remove sport favorit
  - Set skill level per sport
- Delete Account

**Models:**

**User** (Django built-in)
```python
from django.contrib.auth.models import User
```

**UserProfile**
```python
from django.db import models
from django.contrib.auth.models import User
from sigma_app.constants import CITY_CHOICES

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=50, choices=CITY_CHOICES)
    profile_image_url = models.URLField(blank=True, null=True)
    total_points = models.IntegerField(default=0)
    total_events = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
```

**SportPreference**
```python
from sigma_app.constants import SPORT_CHOICES, SKILL_CHOICES

class SportPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sport_preferences')
    sport_type = models.CharField(max_length=20, choices=SPORT_CHOICES)
    skill_level = models.CharField(max_length=20, choices=SKILL_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'sport_type']

    def __str__(self):
        return f"{self.user.username} - {self.sport_type}"
```

**API Endpoints:**
- `GET /` (redirects to profile)
- `POST /auth/register/`
- `POST /auth/login/`
- `POST /auth/logout/`
- `GET /profile/`
- `GET /profile/<int:user_id>/`
- `POST /profile/update/`
- `GET /profile/sports/`
- `DELETE /profile/sports/<int:sport_id>/`

---

### Modul 2: Partner Matching

**Tanggung Jawab:**
- Browse & search users
- Connection system
- Match recommendations

**Fitur:**
- Browse Users
  - Card view
  - Grid view
- Search Users (by name, city)
- Filter Users
  - By sport type
  - By city
  - By skill level
- Connect with Users
- My Connections
  - View all connections
  - Remove connection
- Connection Requests
  - Accept/Reject

**Models:**

**Connection**
```python
from django.db import models
from django.contrib.auth.models import User

class Connection(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connections_sent')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connections_received')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['from_user', 'to_user']
    
    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({self.status})"
```

**API Endpoints:**
- `GET /partner-matching/browse/`
- `GET /partner-matching/browse-users-api/`
- `GET /partner-matching/profile/<int:user_id>/`
- `POST /partner-matching/connection/<str:action>/<int:user_id>/`
- `GET /partner-matching/connections/`
- `GET /partner-matching/profile/<int:user_id>/connections/`
- `POST /partner-matching/connection/<str:action>/user/<int:user_id>/`

---

### Modul 3: Event Discovery

**Tanggung Jawab:**
- Display & browse events
- Join event
- My events (as participant)

**Fitur:**
- Event Listing
  - List view
  - Card view
- Event Detail
  - Event info
  - Participants list
  - Organizer info
- Event Filtering
  - By sport type
  - By date
  - By city
- Event Search
- Join Event
- My Joined Events
  - Upcoming
  - Past
- Leave Event

**Models:**

**Event**
```python
from django.db import models
from django.contrib.auth.models import User
from sigma_app.constants import SPORT_CHOICES

class Event(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('full', 'Full'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail = models.URLField(blank=True, null=True)
    sport_type = models.CharField(max_length=20, choices=SPORT_CHOICES)
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    city = models.CharField(max_length=50)
    location_name = models.CharField(max_length=200)
    max_participants = models.IntegerField()
    current_participants = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def is_full(self):
        return self.current_participants >= self.max_participants
```

**EventParticipant**
```python
class EventParticipant(models.Model):
    STATUS_CHOICES = [
        ('joined', 'Joined'),
        ('attended', 'Attended'),
        ('cancelled', 'Cancelled'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='joined_events')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='joined')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
```

**API Endpoints:**
- `GET /events/`
- `GET /events/json/`
- `GET /events/<int:id>/`
- `GET /events/<int:id>/json/`
- `POST /events/<int:id>/join/`
- `DELETE /events/<int:id>/leave/`
- `GET /events/my-joined/`
- `GET /events/my-joined/json/`
- `GET /events/<int:id>/participant-status/`
- `GET /events/<int:id>/has-attended-participants/`
- `GET /events/<int:id>/user-has-reviewed/`

---

### Modul 4: Event Management

**Tanggung Jawab:**
- Create & edit event
- Manage participants (as organizer)
- My events (as organizer)

**Fitur:**
- Create Event
  - Form dengan validasi
  - Set tanggal & waktu
  - Set lokasi & max participants
- Edit Event
  - Update info
  - Reschedule
- Delete Event
- Cancel Event
- My Organized Events
  - Active events
  - Past events
  - Event statistics
- Manage Participants
  - View participants
  - Remove participant
  - Mark attendance

**Models:**

Menggunakan model **Event** dan **EventParticipant** dari Modul 3.

**API Endpoints:**
- `POST /event-management/create/`
- `GET /event-management/my-events/`
- `PUT /event-management/<int:event_id>/edit/`
- `DELETE /event-management/<int:event_id>/delete/`
- `POST /event-management/<int:event_id>/cancel/`
- `GET /event-management/<int:event_id>/participants/`

---

### Modul 5: Review & Rating

**Tanggung Jawab:**
- Review system post-event
- Rating system
- User reputation

**Fitur:**
- Write Review
  - Rate organizer/participant (1-5 stars)
  - Write comment
- View Reviews
  - My reviews given
  - Reviews received
- Edit/Delete Review
- User Rating Summary
  - Average rating
  - Total reviews
  - Rating distribution

**Models:**

**Review**
```python
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    event = models.ForeignKey('event_discovery.Event', on_delete=models.CASCADE, related_name='reviews')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['event', 'from_user', 'to_user']
    
    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({self.rating}⭐)"
```

**UserRating** (aggregate - updated via signals)
```python
class UserRating(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='rating_summary')
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.IntegerField(default=0)
    five_star = models.IntegerField(default=0)
    four_star = models.IntegerField(default=0)
    three_star = models.IntegerField(default=0)
    two_star = models.IntegerField(default=0)
    one_star = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.average_rating}⭐"
```

**API Endpoints:**
- `GET /reviews/<int:event_id>/`
- `GET /reviews/user/<int:user_id>/`
- `GET /reviews/written/<int:user_id>/`
- `GET /reviews/edit/<int:review_id>/`
- `POST /reviews/ajax/event/<int:event_id>/create/`
- `PUT /reviews/ajax/review/<int:review_id>/update/`
- `DELETE /reviews/ajax/review/<int:review_id>/delete/`

---

### Modul 6: Leaderboard & Points

**Tanggung Jawab:**
- Points tracking system
- Leaderboard ranking
- Achievement tracking

**Fitur:**
- Points Dashboard
  - Total points
  - Points history
  - Points breakdown
- Leaderboard
  - Global ranking
  - Filter by period (weekly, monthly, all-time)
  - Filter by sport
  - User's rank
- Achievements
  - Milestone tracking
  - Achievement list
  - Progress tracking

**Models:**

**PointTransaction**
```python
from django.db import models
from django.contrib.auth.models import User

class PointTransaction(models.Model):
    ACTIVITY_CHOICES = [
        ('event_join', 'Event Join'),
        ('event_complete', 'Event Complete'),
        ('event_organize', 'Event Organize'),
        ('review_given', 'Review Given'),
        ('five_star_received', 'Five Star Received'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_transactions')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    points = models.IntegerField()
    description = models.TextField()
    related_event = models.ForeignKey('event_discovery.Event', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} (+{self.points})"
```

**Leaderboard (Calculated Dynamically)**

The leaderboard is calculated dynamically from UserProfile's `total_points` field and PointTransaction records. There is no separate Leaderboard model. Rankings are computed on-the-fly based on:
- **All-time**: Total points from UserProfile
- **Weekly**: Sum of PointTransaction points from last 7 days
- **Monthly**: Sum of PointTransaction points from last 30 days

**Achievement**
```python
class Achievement(models.Model):
    ACHIEVEMENT_CODES = [
        ('first_event', 'First Event'),
        ('ten_events', '10 Events'),
        ('organizer', 'Organizer'),
        ('highly_rated', 'Highly Rated'),
        ('social_butterfly', 'Social Butterfly'),
        ('early_bird', 'Early Bird'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement_code = models.CharField(max_length=20, choices=ACHIEVEMENT_CODES)
    title = models.CharField(max_length=100)
    description = models.TextField()
    bonus_points = models.IntegerField(default=0)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'achievement_code']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
```

**API Endpoints:**
- `GET /leaderboard/`
- `GET /leaderboard/api/leaderboard/`
- `GET /leaderboard/points/dashboard/`
- `GET /leaderboard/points/history/`
- `GET /leaderboard/achievements/`

---

## 🎯 Sistem Points (Simplified)

### Points per Activity

| Activity | Points | Trigger |
|----------|--------|---------|
| Join Event | +10 | EventParticipant created |
| Complete Event (hadir) | +30 | EventParticipant status = 'attended' |
| Organize Event (selesai) | +50 | Event status = 'completed' |
| Give Review | +5 | Review created |
| Get 5-star Review | +10 | Review with rating = 5 received |

### Ranking Tiers

| Tier | Points Range | Badge |
|------|-------------|-------|
| 🥇 **Master** | 1000+ | Gold |
| 🥈 **Expert** | 500-999 | Silver |
| 🥉 **Advanced** | 200-499 | Bronze |
| ⭐ **Intermediate** | 50-199 | Star |
| 🔰 **Beginner** | 0-49 | Rookie |

### Achievements

| Achievement | Requirement | Bonus Points |
|-------------|-------------|--------------|
| 🏃 **First Event** | Join 1st event | +5 |
| 🎯 **10 Events** | Complete 10 events | +20 |
| 👑 **Organizer** | Organize 5 events | +30 |
| ⭐ **Highly Rated** | Get 10 five-star reviews | +25 |
| 🤝 **Social Butterfly** | Make 20 connections | +15 |
| 🌅 **Early Bird** | Join 5 morning events | +10 |
---

## 📥 Clone Repository

```bash
git clone https://github.com/pbp-kelompok-e5/sigma-app.git
cd sigma-app
```
---

## 🔄 Update ke Main Terbaru

```bash
git checkout main
git pull origin main
```

---

## 🌿 Membuat Branch Personal

```bash
git checkout -b nama-kalian
git branch  # cek branch aktif
```

---

## 💻 Workflow Development

> [!WARNING]
> - **JANGAN commit ke `main`**
> - **SELALU cek branch**: `git branch`
> - **Run migrations setelah pull**: `python manage.py migrate`

### Development Checklist

- [ ] Models defined with proper ForeignKeys
- [ ] Migrations created and tested
- [ ] Signals implemented (if needed)
- [ ] API endpoints working
- [ ] Clear commit messages

---

## 🚀 Quick Start

```bash
# Setup virtual environment
python -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Run development server
python manage.py runserver
```

---

## 👥 Tim Pengembang

| Nama | NPM | Modul | Design |
|------|-----|-------|--------------|
| Muhammad Hariz Albaari | 2406428775 | Authentication & Profile, Leaderboard & Points | Struktur Database | 
| Tsaniya Fini Ardiyanti | 2406437893 | Partner Matching | Partner Matching | 
| Farrell Bagoes Rahmantyo | 2406420596 | Event Discovery | Event Discovery | 
| Muhammad Arief Solomon | 2406343092 | Event Management | Event Management, Auth & Leaderboard | 
| Gerry | 2406495464 | Review & Rating | Review & Rating |

## 📅 Timeline Pengembangan

| Milestone | Tanggal | Deskripsi |
|-----------|---------|-----------|
| **MVP Modul & Design Figma** | 8 Oktober 2025 | Penyelesaian desain UI/UX di Figma dan prototype MVP semua modul |
| **Finalisasi Modul** | 22 Oktober 2025 | Penyelesaian pengembangan dan integrasi semua modul |
| **Testing & Review** | 23 Oktober 2025 | Pengujian fungsionalitas, bug fixing, dan code review |
| **Pengumpulan** | 24 Oktober 2025 | Submission final project |

---
## Sumber Dataset

1. Data Kota Indonesia:
- Sumber: Wikipedia - "Daftar kota di Indonesia menurut provinsi"
- Link: https://id.wikipedia.org/wiki/Daftar_kota_di_Indonesia_menurut_provinsi
- Lisensi: Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
- Digunakan untuk mengisi kolom: city

2. Foto Profil:
- Sumber: Unsplash
- Link: https://unsplash.com
- Digunakan untuk mengisi kolom: profile_image_url
- Catatan: Menggunakan credit global untuk seluruh foto

3. Data Pengguna:
- Sumber: Kaggle – “Social Media Users” oleh Arindam Sahoo
- Link: https://www.kaggle.com/datasets/arindamsahoo/social-media-users
- Lisensi: Database: Open Database License
- Digunakan untuk mengisi kolom: username, full_name, user_id

---
## 👤 Role Pengguna

### 1. Registered User (Pengguna Terdaftar)
Pengguna utama yang sudah registrasi dan dapat mengakses semua fitur aplikasi.

**Hak Akses:**
- Kelola profil dan preferensi olahraga
- Browse dan connect dengan pengguna lain
- Join event olahraga yang tersedia
- Membuat dan kelola event sendiri (sebagai organizer)
- Berikan review dan rating
- Tracking points dan leaderboard
- Manage participants pada event yang dibuat

### 2. Guest/Visitor (Pengunjung)
Pengguna yang belum registrasi, hanya dapat melihat landing page dan informasi umum aplikasi.

**Hak Akses:**
- Lihat landing page dan deskripsi fitur
- Akses halaman register dan login


**Catatan:**
- Tidak ada role admin (sistem peer-to-peer)
- Setiap registered user bisa menjadi organizer dengan membuat event
- Trust-based system melalui review dan rating

---
## 🔗 Deployment & Design

- **Deployment PWS**: https://farrell-bagoes-sigmaapp.pbp.cs.ui.ac.id/
- **Design Figma**: https://www.figma.com/design/FyD4mI3SwzVciuyidRCaim/Desain--Nama-Web-App-?node-id=0-1&t=sEvdR4GK5FUhPnUp-1
---

**Happy Coding! 🚀**

*Questions? Check Django docs or ask in team chat (discord)!*