# Panduan Git Workflow - PLACEHOLDER App

> [!IMPORTANT]
> **Setiap anggota tim mengerjakan fitur di branch masing-masing!**

---

## 🏃‍♂️ Tentang PLACEHOLDER App

**PLACEHOLDER App** adalah platform berbasis web yang menggabungkan konsep **Sport Meetup** dan **Tinder for Friends** — membantu pengguna menemukan teman berolahraga dan mengikuti event olahraga lokal di Indonesia.

### 🎯 Fitur Utama

- **Smart Matching System**: Temukan partner olahraga berdasarkan minat, lokasi, dan skill level
- **Event Discovery**: Jelajahi dan bergabung dengan event olahraga di kotamu
- **Event Creation**: Buat dan kelola event olahraga sendiri
- **Social Gamification**: Dapatkan badge, rating, dan bangun reputasi di komunitas
- **Profile & Statistics**: Tampilkan pencapaian, skill, dan jadwal ketersediaan
- **Rating & Review System**: Berikan feedback setelah event untuk meningkatkan kualitas komunitas

### 💡 Cara Kerja

1. **Onboarding** - Register dengan data olahraga favorit, skill level, dan lokasi
2. **Find Partners** - Swipe-style matching untuk menemukan teman berolahraga
3. **Join/Create Events** - Ikuti event yang ada atau buat event sendiri
4. **Play Together** - Bertemu dan berolahraga bersama secara offline
5. **Build Reputation** - Dapatkan rating dan badge berdasarkan partisipasi

---

## 📦 Pembagian Modul

> [!IMPORTANT]
> **Prinsip DRY**: Setiap model hanya didefinisikan di SATU modul. Modul lain mengimport jika diperlukan.

---

### Modul 1: Authentication & User Management
**PIC: [Nama Anggota 1]**

**Tanggung Jawab:**
- Autentikasi user (register, login, logout)
- Manajemen profil user
- Data preferensi olahraga user
- Data jadwal ketersediaan user

**Fitur:**
- Register dengan form lengkap (nama, email, password, foto, lokasi)
- Login & Logout
- View Profile (public & private view)
- Edit Profile
  - Update foto profil
  - Edit bio & deskripsi
  - Manage olahraga favorit & skill level
  - Set jadwal free time (hari & jam)
  - Update lokasi
- Delete Account

**Models & Atribut:**

**User** (extend Django User)
```python
- username (CharField, unique)
- email (EmailField, unique)
- date_joined (DateTimeField)
- is_verified (BooleanField)
```

**UserProfile**
```python
- user (OneToOneField -> User)
- full_name (CharField)
- bio (TextField, nullable)
- profile_picture (ImageField, nullable)
- gender (CharField, choices)
- city (CharField)
- reputation_score (IntegerField, default=0)
- attendance_rate (DecimalField, default=0.0)
- total_events_joined (IntegerField, default=0)
- total_events_organized (IntegerField, default=0)
- created_at (DateTimeField)
- updated_at (DateTimeField)
```

**SportPreference**
```python
- user (ForeignKey -> User)
- sport_type (CharField, choices: football, basketball, badminton, tennis, running, cycling, swimming, volleyball, gym, yoga)
- skill_level (CharField, choices: beginner, intermediate, advanced, expert)
- is_primary (BooleanField) # olahraga utama/favorit
- years_of_experience (IntegerField, nullable)
- created_at (DateTimeField)
```

**Availability** (jadwal free time)
```python
- user (ForeignKey -> User)
- day_of_week (CharField, choices: monday-sunday)
- start_time (TimeField)
- end_time (TimeField)
- is_active (BooleanField, default=True)
```

**API Endpoints:**
- `POST /auth/register/`
- `POST /auth/login/`
- `POST /auth/logout/`
- `GET /profile/<user_id>/`
- `PUT /profile/update/`
- `DELETE /profile/delete/`
- `GET /profile/<user_id>/sport-preferences/`
- `POST /profile/sport-preferences/add/`
- `PUT /profile/availability/update/`

---

### Modul 2: Partner Matching System
**PIC: [Nama Anggota 2]**

**Tanggung Jawab:**
- Sistem matching & recommendation partners
- Manajemen koneksi antar user
- Filter & search partners

**Fitur:**
- Browse People
  - Card view dengan swipe functionality
  - Grid view untuk desktop
- Smart Matches (rekomendasi berdasarkan algoritma)
- Filter Partners
  - By sport type
  - By location/distance
  - By skill level
  - By availability
- Connect/Skip functionality
- Friends List
  - View all connections
  - Remove connection
- Connection Request Management
  - Accept/Reject requests
  - View pending requests
- Mutual Connection Notification
- Search Partners by name

**Models & Atribut:**

**Connection**
```python
- from_user (ForeignKey -> User)
- to_user (ForeignKey -> User)
- status (CharField, choices: pending, accepted, rejected, blocked)
- match_score (DecimalField, nullable) # compatibility score
- message (TextField, nullable) # pesan saat connect
- created_at (DateTimeField)
- updated_at (DateTimeField)
- is_mutual (BooleanField, default=False)

# Constraint: unique_together = ('from_user', 'to_user')
```

**MatchPreference**
```python
- user (OneToOneField -> User)
- preferred_sports (ManyToManyField -> SportPreference)
- preferred_cities (CharField) # JSON array of cities
- preferred_skill_levels (CharField) # JSON array
- preferred_gender (CharField, nullable)
- only_mutual_sports (BooleanField, default=False)
- updated_at (DateTimeField)
```

**MatchHistory**
```python
- user (ForeignKey -> User)
- viewed_user (ForeignKey -> User)
- action (CharField, choices: skip, connect, view_profile)
- timestamp (DateTimeField)
```

**API Endpoints:**
- `GET /matching/browse/` # list users with pagination
- `GET /matching/smart-matches/` # AI recommended matches
- `POST /matching/connect/<user_id>/`
- `POST /matching/skip/<user_id>/`
- `GET /matching/connections/` # friends list
- `DELETE /matching/connections/<connection_id>/`
- `GET /matching/requests/` # pending requests
- `PUT /matching/requests/<connection_id>/accept/`
- `PUT /matching/requests/<connection_id>/reject/`
- `GET /matching/search/?q=<query>`

---

### Modul 3: Event Discovery & Management
**PIC: [Nama Anggota 3]**

**Tanggung Jawab:**
- Display & browse semua event
- Join event sebagai participant
- Manajemen participant dari sisi user

**Fitur:**
- Event Listing
  - List view dengan pagination
  - Card view dengan thumbnail
- Event Detail Page
  - Info lengkap event
  - List participants
  - Organizer info
  - Location map
- Event Filtering
  - By sport type
  - By date range
  - By location
  - By price (free/paid)
  - By skill level required
  - By availability status (open/full/waitlist)
- Event Search (by title, description)
- Join Event
  - Direct join (jika slot tersedia)
  - Waiting list (jika full)
- My Joined Events
  - Upcoming events
  - Past events
  - Cancelled events
- Leave Event (cancel participation)
- Event Recommendations (berdasarkan algoritma)

**Models & Atribut:**

**Event** (Model Utama - didefinisikan di sini)
```python
- organizer (ForeignKey -> User)
- title (CharField)
- description (TextField)
- sport_type (CharField, choices: sama dengan SportPreference)
- event_type (CharField, choices: casual, competitive, training)
- skill_level_required (CharField, choices: any, beginner, intermediate, advanced)
- event_date (DateField)
- start_time (TimeField)
- end_time (TimeField)
- location_name (CharField)
- city (CharField)
- address (TextField)
- max_participants (IntegerField)
- current_participants (IntegerField, default=0)
- min_participants (IntegerField, default=2)
- price (DecimalField, default=0.0)
- is_paid (BooleanField, default=False)
- payment_details (TextField, nullable)
- event_image (ImageField, nullable)
- is_public (BooleanField, default=True)
- status (CharField, choices: draft, published, ongoing, completed, cancelled)
- cancellation_reason (TextField, nullable)
- created_at (DateTimeField)
- updated_at (DateTimeField)
```

**EventParticipant**
```python
- event (ForeignKey -> Event)
- user (ForeignKey -> User)
- status (CharField, choices: joined, waitlist, confirmed, cancelled, rejected)
- join_timestamp (DateTimeField)
- payment_status (CharField, choices: pending, confirmed, refunded)
- payment_proof (ImageField, nullable)
- is_organizer (BooleanField, default=False)
- notes (TextField, nullable) # catatan dari participant
- priority_score (DecimalField, nullable) # untuk waiting list
- updated_at (DateTimeField)

# Constraint: unique_together = ('event', 'user')
```

**EventCategory**
```python
- name (CharField)
- slug (SlugField, unique)
- description (TextField, nullable)
- icon (CharField, nullable) # emoji atau icon class
- is_active (BooleanField, default=True)
```

**API Endpoints:**
- `GET /events/` # list all events
- `GET /events/<event_id>/`
- `GET /events/filter/?sport=<>&date=<>&location=<>`
- `GET /events/search/?q=<query>`
- `POST /events/<event_id>/join/`
- `DELETE /events/<event_id>/leave/`
- `GET /events/my-events/` # joined events
- `GET /events/recommendations/`

---

### Modul 4: Event Creation & Organization
**PIC: [Nama Anggota 4]**

**Tanggung Jawab:**
- Create & manage event (CRUD)
- Manajemen participants dari sisi organizer
- Invitation system

**Fitur:**
- Create Event
  - Form lengkap dengan validasi
  - Upload event image
  - Set public/private
  - Draft & publish
- Edit Event
  - Update info event
  - Reschedule
- Delete Event (soft delete)
- Cancel Event dengan alasan
- Manage Participants
  - View all participants & waitlist
  - Accept/Reject from waitlist
  - Remove participant
  - Send custom message
- Payment Confirmation
  - Verify payment proof
  - Mark as paid
  - Request additional proof
- Invite Friends
  - Send invitation ke connections
  - Bulk invite
- My Events Dashboard (as organizer)
  - Active events
  - Past events
  - Draft events
  - Event statistics
- Duplicate Event (create similar event)

**Models & Atribut:**

**EventInvitation**
```python
- event (ForeignKey -> Event)
- from_user (ForeignKey -> User) # organizer
- to_user (ForeignKey -> User) # invited user
- status (CharField, choices: pending, accepted, declined, expired)
- message (TextField, nullable)
- sent_at (DateTimeField)
- responded_at (DateTimeField, nullable)
- expires_at (DateTimeField)
```

**EventUpdate** (pengumuman dari organizer)
```python
- event (ForeignKey -> Event)
- author (ForeignKey -> User)
- title (CharField)
- message (TextField)
- is_important (BooleanField, default=False)
- created_at (DateTimeField)
```

**EventPayment**
```python
- event (ForeignKey -> Event)
- participant (ForeignKey -> User)
- amount (DecimalField)
- payment_method (CharField, nullable)
- payment_proof (ImageField)
- verification_status (CharField, choices: pending, verified, rejected)
- verified_by (ForeignKey -> User, nullable)
- verified_at (DateTimeField, nullable)
- rejection_reason (TextField, nullable)
- created_at (DateTimeField)
- updated_at (DateTimeField)
```

**API Endpoints:**
- `POST /events/create/`
- `PUT /events/<event_id>/update/`
- `DELETE /events/<event_id>/`
- `POST /events/<event_id>/cancel/`
- `GET /events/my-organized/`
- `GET /events/<event_id>/participants/`
- `PUT /events/<event_id>/participants/<user_id>/accept/`
- `PUT /events/<event_id>/participants/<user_id>/reject/`
- `DELETE /events/<event_id>/participants/<user_id>/`
- `POST /events/<event_id>/invite/`
- `PUT /events/payments/<payment_id>/verify/`
- `POST /events/<event_id>/updates/`

---

### Modul 5: Rating, Review & Gamification
**PIC: [Nama Anggota 5]**

**Tanggung Jawab:**
- Rating & review system post-event
- Badge & achievement system
- Notification system
- Reputation management

**Fitur:**
- Post-Event Rating
  - Rate organizer (jika participant)
  - Rate participants (jika organizer)
  - Multi-criteria rating (punctuality, skill, attitude, communication)
- Review & Feedback
  - Write review dengan foto
  - Edit/delete own review
  - Report inappropriate review
- Badge System
  - Display earned badges di profile
  - Badge progress tracking
  - Badge descriptions & requirements
- Leaderboard
  - By reputation score
  - By total events
  - By sport category
  - Weekly/Monthly/All-time
- Achievement Tracking
  - Progress bars untuk badge
  - Milestone notifications
- Notification System
  - Event reminders (H-1, H-2 jam)
  - Connection requests
  - Event invitations
  - Payment confirmations
  - Badge earned
  - Event updates
  - Mark as read
  - Notification preferences

**Models & Atribut:**

**Rating**
```python
- event (ForeignKey -> Event)
- from_user (ForeignKey -> User) # pemberi rating
- to_user (ForeignKey -> User) # penerima rating
- overall_score (DecimalField) # 1.0 - 5.0
- punctuality_score (IntegerField, 1-5)
- skill_score (IntegerField, 1-5)
- attitude_score (IntegerField, 1-5)
- communication_score (IntegerField, 1-5)
- created_at (DateTimeField)
- updated_at (DateTimeField)

# Constraint: unique_together = ('event', 'from_user', 'to_user')
```

**Review**
```python
- rating (OneToOneField -> Rating)
- comment (TextField)
- images (ImageField, nullable) # multiple images support
- is_public (BooleanField, default=True)
- helpful_count (IntegerField, default=0) # upvote review
- is_reported (BooleanField, default=False)
- report_reason (TextField, nullable)
- created_at (DateTimeField)
- updated_at (DateTimeField)
```

**Badge**
```python
- code (CharField, unique) # weekend_warrior, reliable_player, etc
- name (CharField)
- description (TextField)
- icon (CharField) # emoji
- category (CharField, choices: attendance, social, performance, achievement)
- requirement_type (CharField) # event_count, rating_avg, etc
- requirement_value (IntegerField)
- score_bonus (IntegerField)
- is_active (BooleanField, default=True)
```

**UserBadge**
```python
- user (ForeignKey -> User)
- badge (ForeignKey -> Badge)
- earned_at (DateTimeField)
- progress (IntegerField, default=0) # untuk tracking progress
- is_displayed (BooleanField, default=True) # tampilkan di profile
```

**Achievement**
```python
- user (ForeignKey -> User)
- achievement_type (CharField) # first_event, 10_events, etc
- title (CharField)
- description (TextField)
- earned_at (DateTimeField)
- related_event (ForeignKey -> Event, nullable)
```

**Notification**
```python
- user (ForeignKey -> User) # penerima notif
- notification_type (CharField, choices: event_reminder, connection_request, invitation, payment, badge, event_update, rating_received)
- title (CharField)
- message (TextField)
- related_event (ForeignKey -> Event, nullable)
- related_user (ForeignKey -> User, nullable)
- action_url (CharField, nullable)
- is_read (BooleanField, default=False)
- is_sent (BooleanField, default=False) # untuk scheduling
- scheduled_at (DateTimeField, nullable)
- created_at (DateTimeField)
- read_at (DateTimeField, nullable)
```

**NotificationPreference**
```python
- user (OneToOneField -> User)
- email_notifications (BooleanField, default=True)
- push_notifications (BooleanField, default=True)
- event_reminders (BooleanField, default=True)
- connection_requests (BooleanField, default=True)
- event_invitations (BooleanField, default=True)
- event_updates (BooleanField, default=True)
- badge_earned (BooleanField, default=True)
- rating_received (BooleanField, default=True)
```

**API Endpoints:**
- `POST /ratings/create/`
- `GET /ratings/user/<user_id>/` # all ratings for user
- `GET /reviews/event/<event_id>/`
- `POST /reviews/create/`
- `PUT /reviews/<review_id>/update/`
- `DELETE /reviews/<review_id>/`
- `POST /reviews/<review_id>/report/`
- `GET /badges/`
- `GET /badges/user/<user_id>/`
- `GET /achievements/user/<user_id>/`
- `GET /leaderboard/?type=<>&period=<>`
- `GET /notifications/`
- `PUT /notifications/<notification_id>/read/`
- `PUT /notifications/mark-all-read/`
- `GET /notifications/preferences/`
- `PUT /notifications/preferences/update/`

---

## 📊 Dependensi Antar Modul

```
Modul 1 (User) ← Modul 2 (Matching) → perlu data user & preferences
Modul 1 (User) ← Modul 3 (Event Discovery) → perlu data user
Modul 1 (User) ← Modul 4 (Event Organization) → perlu data user
Modul 3 (Event) ← Modul 4 (Organization) → CRUD event
Modul 3 (Event) → Modul 5 (Rating) → rating berdasarkan event
Modul 1 (User) ← Modul 5 (Rating) → rating untuk user
```

---

## ⚠️ Catatan Penting

> [!WARNING]
> **Hindari Circular Import:**
> - Gunakan `get_user_model()` untuk referensi User model
> - Import model dari app lain hanya di views/serializers, bukan di models.py
> - Gunakan string reference untuk ForeignKey: `ForeignKey('app.Model')`

> [!TIP]
> **Best Practices:**
> - Setiap model punya satu PIC yang bertanggung jawab
> - Koordinasi dengan PIC lain saat butuh akses model mereka
---

## 🧮 Algoritma & Formula Aplikasi

### 1. Smart Matching Score

Formula untuk menghitung compatibility score antara dua user:

```
Match Score = (W1 × Sport Similarity) + (W2 × Location Proximity) + (W3 × Skill Compatibility)

Dimana:
- W1, W2, W3 = Bobot (total = 1.0)
- W1 = 0.4 (Sport Similarity)
- W2 = 0.4 (Location Proximity)
- W3 = 0.2 (Skill Compatibility)
```
---

### 2. Event Recommendation Score

Formula untuk merekomendasikan event ke user:

```
Event Score = (W1 × Sport Match) + (W2 × Location Match(True/False)) + (W3 × Time Match)

Dimana:
W1 = 0.4, W2 = 0.2, W3 = 0.4,
```

**Komponen:**

**Sport Match:**
```
Sport Match = {
  1.0, jika event olahraga = olahraga favorit user
  0.7, jika event olahraga dalam list interest user
  0.2, jika tidak ada kecocokan
}
```

**Time Match:**
```
Time Match = {
  1.0, jika waktu event sesuai jadwal free time user
  0.5, jika waktu event di hari yang sama dengan free time
  0.2, jika tidak ada kecocokan
}
```
---

### 3. Badge Achievement System

**Badge Categories & Requirements:**

| Badge | Requirement | Score Bonus |
|-------|-------------|-------------|
| 🏃 **Weekend Warrior** | Join 4 events di weekend dalam 1 bulan | +10 |
| ⭐ **Reliable Player** | Attendance rate ≥ 95% (min 10 events) | +15 |
| 🎯 **Perfect Rating** | Maintain 5.0 rating (min 20 reviews) | +20 |
| 👑 **Top Organizer** | Successfully organize 10+ events | +15 |
| 🤝 **Social Butterfly** | Connect dengan 50+ users | +10 |
| 🔥 **On Fire** | Join events 7 hari berturut-turut | +15 |
| 💎 **Veteran** | Active user 6+ bulan | +20 |
| 🌟 **Multi-Sport** | Participate in 5+ different sports | +10 |
---

### 5. Waiting List Priority

Formula untuk menentukan prioritas dalam waiting list:

```
Priority Score = (Response Time × 0.3) + (Activity History × 0.3)

Range: 0-100
```

**Response Time:**
```
Response Time Score = {
  100, jika join dalam 1 jam pertama
  80,  jika join dalam 6 jam pertama
  60,  jika join dalam 24 jam pertama
  40,  jika join setelah 24 jam
}
```

**Activity History Score:**
```
Activity History Score = Persentasi kehadiran di semua event yang telah dilakukan
```

---
## 📥 Clone Repository

1. **Buat direktori lokal** dengan nama `PLACEHOLDER-app`

2. **Buka folder** di VSCode

3. **Clone repository:**
   ```bash
   git clone https://github.com/pbp-kelompok-e5/PLACEHOLDER-app.git
   ```

---

## 🔄 Update ke Versi Main Terbaru

Sebelum membuat branch baru, pastikan Anda memiliki versi terbaru dari `main`:

1. **Pindah ke branch main:**
   ```bash
   git checkout main
   ```

2. **Update dari remote:**
   ```bash
   git pull origin main
   ```

---

## 🌿 Membuat Branch Personal

1. **Buat branch baru** dengan nama Anda:
   ```bash
   git checkout -b nama-kalian
   ```

2. **Cek branch aktif** (pastikan berada di branch Anda):
   ```bash
   git branch
   ```
   
   > [!TIP]
   > Branch yang aktif akan ditandai dengan tanda `*`

---

## 💻 Workflow Development

> [!WARNING]
> - **JANGAN commit langsung ke `main`**
> - **SELALU cek branch sebelum commit** menggunakan `git branch`

> [!NOTE]
> Kerjakan semua fitur di branch masing-masing untuk menghindari konflik

### 📋 Development Checklist

Sebelum push ke remote, pastikan:
- [ ] Code sudah ditest di lokal
- [ ] Tidak ada conflict dengan branch main
- [ ] Migrations sudah dibuat (jika ada perubahan model)
- [ ] Requirements.txt sudah diupdate (jika ada library baru)
- [ ] Commit message jelas dan deskriptif

---

## 📚 Referensi

Untuk informasi lebih lengkap, rujuk ke:  
[PBP Fasilkom UI - Development di Feature Branch](https://pbp-fasilkom-ui.github.io/ganjil-2026/assignments/group/midterm-guide#development-di-feature-branch)

---

## 📝 Tips Tambahan

> [!TIP]
> **Best Practices:**
> - Commit secara berkala dengan pesan yang jelas dan deskriptif
> - Pull dari `main` secara rutin untuk menghindari konflik besar
> - Komunikasikan dengan tim sebelum merge ke `main`
> - Test fitur Anda sebelum push ke remote
> - Gunakan virtual environment untuk isolasi dependencies
> - Dokumentasikan API endpoints yang dibuat

---

## 🚀 Quick Start Development

```bash
# 1. Setup virtual environment
python -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py makemigrations
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Run development server
python manage.py runserver
```

---

## 👥 Tim Pengembang

| Nama | Modul | GitHub |
|------|-------|--------|
| [Nama Anggota 1] | Authentication & User Management | [@username1] |
| [Nama Anggota 2] | Partner Matching System | [@username2] |
| [Nama Anggota 3] | Event Discovery & Management | [@username3] |
| [Nama Anggota 4] | Event Creation & Organization | [@username4] |
| [Nama Anggota 5] | Rating, Review & Gamification | [@username5] |
---

**Happy Coding! 🚀**