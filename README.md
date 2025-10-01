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
- **Social Gamification**: Dapatkan points, badge, rating, dan bangun reputasi di komunitas
- **Profile & Statistics**: Tampilkan pencapaian, skill, dan jadwal ketersediaan
- **Rating & Review System**: Berikan feedback setelah event untuk meningkatkan kualitas komunitas
- **Leaderboard System**: Kompetisi sehat melalui ranking points user

### 💡 Cara Kerja

1. **Onboarding** - Register dengan data olahraga favorit, skill level, dan lokasi
2. **Find Partners** - Swipe-style matching untuk menemukan teman berolahraga
3. **Join/Create Events** - Ikuti event yang ada atau buat event sendiri
4. **Play Together** - Bertemu dan berolahraga bersama secara offline
5. **Build Reputation** - Dapatkan points, rating dan badge berdasarkan partisipasi
6. **Compete** - Naik ranking di leaderboard dan tunjukkan kehebatan Anda!

---

## 📦 Pembagian Modul (5 Modul Independen)

> [!IMPORTANT]
> **Prinsip DRY**: Setiap model hanya didefinisikan di SATU modul. Modul lain mengimport jika diperlukan.

---

### Modul 1: Profile & User Management
**PIC: [Nama Anggota 1]**

**Tanggung Jawab:**
- Autentikasi user (register, login, logout)
- Manajemen profil user
- Data preferensi olahraga user
- Data jadwal ketersediaan user
- **Sistem Points & Leaderboard**

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
- **Points Dashboard**
  - View total points
  - Points history & breakdown
  - Points earning activities
- **Leaderboard Page**
  - Global ranking by total points
  - Filter by period (weekly, monthly, all-time)
  - Filter by sport category
  - View top performers
  - User's current rank & position
  - Points comparison

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
- total_points (IntegerField, default=0) # NEW: Total Points
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
- is_primary (BooleanField)
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

**PointTransaction** (NEW)
```python
- user (ForeignKey -> User)
- activity_type (CharField, choices: event_join, event_complete, event_organize, connection_made, rating_received, badge_earned, review_given, consecutive_attendance)
- points_earned (IntegerField)
- description (TextField)
- related_event_id (IntegerField, nullable)
- related_user_id (IntegerField, nullable)
- created_at (DateTimeField)
```

**LeaderboardEntry** (NEW)
```python
- user (ForeignKey -> User)
- rank (IntegerField)
- total_points (IntegerField)
- period_type (CharField, choices: weekly, monthly, all_time)
- sport_category (CharField, nullable)
- last_updated (DateTimeField)
- rank_change (IntegerField, default=0) # naik/turun rank
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
- `GET /profile/points/` # Points dashboard
- `GET /profile/points/history/` # Points transaction history
- `GET /leaderboard/` # Global leaderboard
- `GET /leaderboard/filter/?period=<>&sport=<>` # Filtered leaderboard
- `GET /leaderboard/my-rank/` # User's current rank

---

### Modul 2: Partner Matching & Social Network
**PIC: [Nama Anggota 2]**

**Tanggung Jawab:**
- Sistem matching & recommendation partners
- Manajemen koneksi antar user
- Filter & search partners
- Social networking features

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
  - By points range
- Connect/Skip functionality
- Friends List
  - View all connections
  - Remove connection
  - View mutual friends
- Connection Request Management
  - Accept/Reject requests
  - View pending requests
- Mutual Connection Notification
- Search Partners by name
- User Statistics
  - Total connections
  - Connection growth

**Models & Atribut:**

**Connection**
```python
- from_user (ForeignKey -> User)
- to_user (ForeignKey -> User)
- status (CharField, choices: pending, accepted, rejected, blocked)
- match_score (DecimalField, nullable)
- message (TextField, nullable)
- created_at (DateTimeField)
- updated_at (DateTimeField)
- is_mutual (BooleanField, default=False)
```

**MatchPreference**
```python
- user (OneToOneField -> User)
- preferred_sports (CharField) # JSON array
- preferred_cities (CharField) # JSON array
- preferred_skill_levels (CharField) # JSON array
- preferred_gender (CharField, nullable)
- preferred_points_range (CharField, nullable) # NEW
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
- `GET /matching/browse/`
- `GET /matching/smart-matches/`
- `POST /matching/connect/<user_id>/`
- `POST /matching/skip/<user_id>/`
- `GET /matching/connections/`
- `DELETE /matching/connections/<connection_id>/`
- `GET /matching/requests/`
- `PUT /matching/requests/<connection_id>/accept/`
- `PUT /matching/requests/<connection_id>/reject/`
- `GET /matching/search/?q=<query>`
- `GET /matching/statistics/`

---

### Modul 3: Event Discovery & Participation
**PIC: [Nama Anggota 3]**

**Tanggung Jawab:**
- Display & browse semua event
- Join event sebagai participant
- Manajemen participant dari sisi user
- Event recommendations

**Fitur:**
- Event Listing
  - List view dengan pagination
  - Card view dengan thumbnail
  - Map view
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
  - By availability status
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
- Event Calendar View

**Models & Atribut:**

**Event**
```python
- organizer_id (IntegerField) # Reference to User ID
- title (CharField)
- description (TextField)
- sport_type (CharField, choices)
- event_type (CharField, choices: casual, competitive, training)
- skill_level_required (CharField, choices)
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
- event_id (IntegerField)
- user_id (IntegerField)
- status (CharField, choices: joined, waitlist, confirmed, cancelled, rejected)
- join_timestamp (DateTimeField)
- payment_status (CharField, choices: pending, confirmed, refunded)
- payment_proof (ImageField, nullable)
- is_organizer (BooleanField, default=False)
- notes (TextField, nullable)
- priority_score (DecimalField, nullable)
- updated_at (DateTimeField)
```

**EventCategory**
```python
- name (CharField)
- slug (SlugField, unique)
- description (TextField, nullable)
- icon (CharField, nullable)
- is_active (BooleanField, default=True)
```

**API Endpoints:**
- `GET /events/`
- `GET /events/<event_id>/`
- `GET /events/filter/`
- `GET /events/search/`
- `POST /events/<event_id>/join/`
- `DELETE /events/<event_id>/leave/`
- `GET /events/my-events/`
- `GET /events/recommendations/`
- `GET /events/calendar/`

---

### Modul 4: Event Management & Organization
**PIC: [Nama Anggota 4]**

**Tanggung Jawab:**
- Create & manage event (CRUD)
- Manajemen participants dari sisi organizer
- Invitation system
- Event updates & announcements

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
- Duplicate Event
- Event Announcements

**Models & Atribut:**

**EventInvitation**
```python
- event_id (IntegerField)
- from_user_id (IntegerField)
- to_user_id (IntegerField)
- status (CharField, choices: pending, accepted, declined, expired)
- message (TextField, nullable)
- sent_at (DateTimeField)
- responded_at (DateTimeField, nullable)
- expires_at (DateTimeField)
```

**EventUpdate**
```python
- event_id (IntegerField)
- author_id (IntegerField)
- title (CharField)
- message (TextField)
- is_important (BooleanField, default=False)
- created_at (DateTimeField)
```

**EventPayment**
```python
- event_id (IntegerField)
- participant_id (IntegerField)
- amount (DecimalField)
- payment_method (CharField, nullable)
- payment_proof (ImageField)
- verification_status (CharField, choices: pending, verified, rejected)
- verified_by_id (IntegerField, nullable)
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
- `POST /events/<event_id>/duplicate/`

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
  - Multi-criteria rating
- Review & Feedback
  - Write review dengan foto
  - Edit/delete own review
  - Report inappropriate review
- Badge System
  - Display earned badges di profile
  - Badge progress tracking
  - Badge descriptions & requirements
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
  - Points earned notifications
  - Mark as read
  - Notification preferences
- Review Statistics
  - Average ratings
  - Review sentiment analysis

**Models & Atribut:**

**Rating**
```python
- event_id (IntegerField)
- from_user_id (IntegerField)
- to_user_id (IntegerField)
- overall_score (DecimalField)
- punctuality_score (IntegerField, 1-5)
- skill_score (IntegerField, 1-5)
- attitude_score (IntegerField, 1-5)
- communication_score (IntegerField, 1-5)
- created_at (DateTimeField)
- updated_at (DateTimeField)
```

**Review**
```python
- rating_id (IntegerField)
- comment (TextField)
- images (ImageField, nullable)
- is_public (BooleanField, default=True)
- helpful_count (IntegerField, default=0)
- is_reported (BooleanField, default=False)
- report_reason (TextField, nullable)
- created_at (DateTimeField)
- updated_at (DateTimeField)
```

**Badge**
```python
- code (CharField, unique)
- name (CharField)
- description (TextField)
- icon (CharField)
- category (CharField, choices)
- requirement_type (CharField)
- requirement_value (IntegerField)
- points_bonus (IntegerField) # NEW: Points given when earned
- is_active (BooleanField, default=True)
```

**UserBadge**
```python
- user_id (IntegerField)
- badge_id (IntegerField)
- earned_at (DateTimeField)
- progress (IntegerField, default=0)
- is_displayed (BooleanField, default=True)
```

**Achievement**
```python
- user_id (IntegerField)
- achievement_type (CharField)
- title (CharField)
- description (TextField)
- points_earned (IntegerField) # NEW
- earned_at (DateTimeField)
- related_event_id (IntegerField, nullable)
```

**Notification**
```python
- user_id (IntegerField)
- notification_type (CharField, choices)
- title (CharField)
- message (TextField)
- related_event_id (IntegerField, nullable)
- related_user_id (IntegerField, nullable)
- action_url (CharField, nullable)
- is_read (BooleanField, default=False)
- is_sent (BooleanField, default=False)
- scheduled_at (DateTimeField, nullable)
- created_at (DateTimeField)
- read_at (DateTimeField, nullable)
```

**NotificationPreference**
```python
- user_id (IntegerField)
- email_notifications (BooleanField, default=True)
- push_notifications (BooleanField, default=True)
- event_reminders (BooleanField, default=True)
- connection_requests (BooleanField, default=True)
- event_invitations (BooleanField, default=True)
- event_updates (BooleanField, default=True)
- badge_earned (BooleanField, default=True)
- rating_received (BooleanField, default=True)
- points_earned (BooleanField, default=True) # NEW
```

**API Endpoints:**
- `POST /ratings/create/`
- `GET /ratings/user/<user_id>/`
- `GET /reviews/event/<event_id>/`
- `POST /reviews/create/`
- `PUT /reviews/<review_id>/update/`
- `DELETE /reviews/<review_id>/`
- `POST /reviews/<review_id>/report/`
- `GET /badges/`
- `GET /badges/user/<user_id>/`
- `GET /achievements/user/<user_id>/`
- `GET /notifications/`
- `PUT /notifications/<notification_id>/read/`
- `PUT /notifications/mark-all-read/`
- `GET /notifications/preferences/`
- `PUT /notifications/preferences/update/`

---

## 🎯 Sistem Points

### Formula Perhitungan Points

**Base Points per Activity:**

| Activity | Points | Description |
|----------|--------|-------------|
| **Event Join** | +10 | Bergabung dengan event |
| **Event Complete** | +50 | Menyelesaikan event (hadir) |
| **Event Organize** | +100 | Berhasil mengorganisir event (min 5 participants) |
| **Connection Made** | +5 | Membuat koneksi baru (accepted) |
| **Rating Received (5.0)** | +20 | Mendapat perfect rating |
| **Rating Received (4.0-4.9)** | +10 | Mendapat rating baik |
| **Review Given** | +5 | Memberikan review |
| **Badge Earned** | +10 to +30 | Tergantung badge (lihat badge system) |
| **Consecutive Attendance** | +25 per streak | Hadir berturut-turut (per 3 events) |


### Leaderboard Ranking System

**Ranking Update:**
- Weekly leaderboard reset (optional)
- Monthly leaderboard
- All-time leaderboard (permanent)

---

## 🧮 Algoritma Smart Matching

### Match Score Formula

```
Match Score = (W1 × Sport Similarity) + (W2 × Location Proximity) + (W3 × Skill Compatibility) + (W4 × Activity Level)

Weights:
W1 = 0.35 (Sport Similarity)
W2 = 0.30 (Location Proximity)
W3 = 0.20 (Skill Compatibility)
W4 = 0.15 (Activity Level)
```

**Components:**

**Sport Similarity:**
```
Sport Similarity = {
  1.0, if primary sports match
  0.7, if any sport matches
  0.3, if same sport category (team/individual)
  0.0, if no match
}
```

**Location Proximity:**
```
Location Proximity = {
  1.0, if same city
  0.0, if different city
}
```

**Skill Compatibility:**
```
Skill Diff = |User1 Skill Level - User2 Skill Level|

Skill Compatibility = {
  1.0, if same level
  0.7, if diff = 1 level
  0.3, if diff = 2 levels
  0.0, if diff ≥ 3 levels
}
```

**Activity Level:**
```
Activity Level = (User's Total Points / 1000) capped at 1.0
```

---

## 🏆 Badge System Details

**Updated Badge Requirements:**

| Badge | Requirement | Points Bonus |
|-------|-------------|--------------|
| 🏃 **Weekend Warrior** | Join 4 weekend events in 1 month | +15 |
| ⭐ **Reliable Player** | 95% attendance (min 10 events) | +20 |
| 🎯 **Perfect Rating** | 5.0 rating average (min 20 reviews) | +30 |
| 👑 **Top Organizer** | 10+ successful events | +25 |
| 🤝 **Social Butterfly** | 50+ connections | +15 |
| 🔥 **On Fire** | 7 consecutive days events | +20 |
| 💎 **Veteran** | 6+ months active | +30 |
| 🌟 **Multi-Sport** | 5+ different sports | +15 |
| 🚀 **Rising Star** | 1000+ points in 1 month | +25 |
| 👊 **Consistency King** | 20+ events without cancellation | +20 |

---

## 📊 Struktur Modul Independence

```
Modul 1 (Profile & Leaderboard)
  ├── Manages: User, Profile, Points, Rankings
  └── Independent: Self-contained point system

Modul 2 (Matching & Social)
  ├── Manages: Connections, Matching
  └── Independent: Uses user_id references

Modul 3 (Event Discovery)
  ├── Manages: Events, Participation
  └── Independent: Event viewing & joining

Modul 4 (Event Management)
  ├── Manages: Event CRUD, Organization
  └── Independent: Event creation & management

Modul 5 (Rating & Gamification)
  ├── Manages: Ratings, Badges, Notifications
  └── Independent: Post-event activities
```

> [!TIP]
> **Inter-Module Communication:**
> - Gunakan ID references (user_id, event_id) bukan ForeignKey direct
> - Setiap modul expose REST API untuk data sharing
> - Async notifications via message queue (optional)

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

2. **Cek branch aktif:**
   ```bash
   git branch
   ```

---

## 💻 Workflow Development

> [!WARNING]
> - **JANGAN commit langsung ke `main`**
> - **SELALU cek branch sebelum commit**

### 📋 Development Checklist

- [ ] Code sudah ditest di lokal
- [ ] Tidak ada conflict dengan branch main
- [ ] Migrations sudah dibuat
- [ ] Requirements.txt sudah diupdate
- [ ] Commit message jelas dan deskriptif
- [ ] API documentation updated

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
| [Nama Anggota 1] | Profile & Leaderboard | [@username1] |
| [Nama Anggota 2] | Matching & Social | [@username2] |
| [Nama Anggota 3] | Event Discovery | [@username3] |
| [Nama Anggota 4] | Event Management | [@username4] |
| [Nama Anggota 5] | Rating & Gamification | [@username5] |

---

**Happy Coding! 🚀**