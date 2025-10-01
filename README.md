# Panduan Git Workflow - PLACEHOLDER App

> [!IMPORTANT]
> **Setiap anggota tim mengerjakan fitur di branch masing-masing!**

---

## 🏃‍♂️ Tentang PLACEHOLDER App

**PLACEHOLDER App** adalah platform berbasis web yang menggabungkan konsep **Sport Meetup** dan **Tinder for Friends** — membantu pengguna menemukan teman berolahraga dan mengikuti event olahraga lokal di Indonesia.

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

> [!NOTE]
> **Setiap modul tetap fokus pada tanggung jawabnya, tetapi menggunakan Foreign Key untuk relasi yang efisien**

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

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=50)
    total_points = models.IntegerField(default=0)
    total_events = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.full_name
```

**SportPreference**
```python
SPORT_CHOICES = [
    ('football', 'Football'),
    ('basketball', 'Basketball'),
    ('badminton', 'Badminton'),
    ('tennis', 'Tennis'),
    ('running', 'Running'),
    ('cycling', 'Cycling'),
    ('swimming', 'Swimming'),
    ('volleyball', 'Volleyball'),
]

SKILL_CHOICES = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
]

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
- `POST /auth/register/`
- `POST /auth/login/`
- `POST /auth/logout/`
- `GET /profile/<int:user_id>/`
- `PUT /profile/update/`
- `DELETE /profile/delete/`
- `GET /profile/sports/`
- `POST /profile/sports/add/`
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
- `GET /users/browse/`
- `GET /users/search/?q=<query>`
- `GET /users/filter/?sport=<>&city=<>&skill=<>`
- `POST /connections/send/<int:user_id>/`
- `GET /connections/my-connections/`
- `DELETE /connections/<int:connection_id>/`
- `GET /connections/requests/`
- `PUT /connections/<int:connection_id>/accept/`
- `PUT /connections/<int:connection_id>/reject/`

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

class Event(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('full', 'Full'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    SPORT_CHOICES = [
        ('football', 'Football'),
        ('basketball', 'Basketball'),
        ('badminton', 'Badminton'),
        ('tennis', 'Tennis'),
        ('running', 'Running'),
        ('cycling', 'Cycling'),
        ('swimming', 'Swimming'),
        ('volleyball', 'Volleyball'),
    ]
    
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    title = models.CharField(max_length=200)
    description = models.TextField()
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
- `GET /events/<int:event_id>/`
- `GET /events/filter/?sport=<>&date=<>&city=<>`
- `GET /events/search/?q=<query>`
- `POST /events/<int:event_id>/join/`
- `GET /events/my-joined/`
- `DELETE /events/<int:event_id>/leave/`

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
- `POST /events/create/`
- `PUT /events/<int:event_id>/update/`
- `DELETE /events/<int:event_id>/`
- `POST /events/<int:event_id>/cancel/`
- `GET /events/my-organized/`
- `GET /events/<int:event_id>/participants/`
- `DELETE /events/<int:event_id>/participants/<int:user_id>/`
- `POST /events/<int:event_id>/mark-attendance/`

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
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='reviews')
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
- `POST /reviews/create/`
- `GET /reviews/event/<int:event_id>/`
- `GET /reviews/user/<int:user_id>/received/`
- `GET /reviews/my-reviews/`
- `PUT /reviews/<int:review_id>/update/`
- `DELETE /reviews/<int:review_id>/`
- `GET /reviews/user/<int:user_id>/summary/`

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
    related_event = models.ForeignKey('events.Event', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} (+{self.points})"
```

**Leaderboard**
```python
class Leaderboard(models.Model):
    PERIOD_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('all_time', 'All Time'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries')
    rank = models.IntegerField()
    total_points = models.IntegerField()
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    sport_type = models.CharField(max_length=20, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'period', 'sport_type']
        ordering = ['rank']
    
    def __str__(self):
        return f"#{self.rank} - {self.user.username} ({self.total_points} pts)"
```

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
- `GET /points/dashboard/`
- `GET /points/history/`
- `POST /points/add/` # Internal use (called by other modules via signals)
- `GET /leaderboard/`
- `GET /leaderboard/filter/?period=<>&sport=<>`
- `GET /leaderboard/my-rank/`
- `GET /achievements/`
- `GET /achievements/<int:user_id>/`

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

## 📊 Struktur Database dengan Relasi

```
User (Django Auth)
  │
  ├─── OneToOne ──> UserProfile (Modul 1)
  │                     └─── total_points (updated by Modul 6)
  │
  ├─── ForeignKey ──> SportPreference (Modul 1)
  │                     └─── Multiple sports per user
  │
  ├─── ForeignKey ──> Connection (Modul 2)
  │                     ├─── from_user (connections sent)
  │                     └─── to_user (connections received)
  │
  ├─── ForeignKey ──> Event (Modul 3/4)
  │                     ├─── organizer (who created)
  │                     └─── ForeignKey ──> EventParticipant (Modul 3)
  │                                           └─── user (who joined)
  │
  ├─── ForeignKey ──> Review (Modul 5)
  │                     ├─── from_user (reviewer)
  │                     ├─── to_user (reviewed)
  │                     └─── event (context)
  │
  ├─── OneToOne ──> UserRating (Modul 5)
  │                     └─── aggregate review data
  │
  ├─── ForeignKey ──> PointTransaction (Modul 6)
  │                     └─── history of points earned
  │
  ├─── ForeignKey ──> Leaderboard (Modul 6)
  │                     └─── ranking per period/sport
  │
  └─── ForeignKey ──> Achievement (Modul 6)
                        └─── earned achievements
```
---

## 📥 Clone Repository

```bash
git clone https://github.com/pbp-kelompok-e5/sigma-app.git
cd sigma-app
```
---
## Sumber Dataset
https://www.kaggle.com/datasets/arindamsahoo/social-media-users
https://id.wikipedia.org/wiki/Daftar_kota_di_Indonesia_menurut_provinsi

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

| Nama | Modul |
|------|-------|
| Hariz | Authentication & Profile, Leaderboard & Points | 
| Fini  | Partner Matching | 
| Farrell| Event Discovery | 
| Arief | Event Management | 
| Gerry | Review & Rating | 

---

**Happy Coding! 🚀**

*Questions? Check Django docs or ask in team chat!*
