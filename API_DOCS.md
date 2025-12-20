# Sigma App - API Documentation

**Base URL:** `https://farrell-bagoes-sigmaapp.pbp.cs.ui.ac.id`  
**Authentication:** Session-based (Django CSRF + Session Cookie)

---

## Authentication

### Register
**POST** `/auth/register/`

**Request Body:**
```json
{
  "username": "string",
  "password1": "string",
  "password2": "string",
  "full_name": "string",
  "city": "string"  // See CITY_CHOICES
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Registration successful",
  "redirect_url": "/profile/"
}
```

**Response (400):**
```json
{
  "success": false,
  "errors": {
    "username": ["This field is required."],
    "password1": ["Password too short."]
  }
}
```

---

### Login
**POST** `/auth/login/`

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "redirect_url": "/profile/"
}
```

**Response (400):**
```json
{
  "success": false,
  "errors": {
    "username": ["Invalid credentials."]
  }
}
```

---

### Logout
**POST** `/auth/logout/`

**Response:** Redirect to `/auth/login/`

---

## Profile

### Get Own Profile
**GET** `/profile/`  
**Auth:** Required

**Response (200):** HTML page

---

### Get User Profile
**GET** `/profile/<user_id>/`  
**Auth:** Required

**Response (200):** HTML page

---

### Update Profile
**POST** `/profile/update/`  
**Auth:** Required

**Request Body:**
```json
{
  "full_name": "string",
  "bio": "string",
  "city": "string",
  "profile_image_url": "string (URL)"
}
```

**Response:** Redirect to `/profile/`

---

### Get Sport Preferences
**GET** `/profile/sports/`  
**Auth:** Required

**Response (200):** HTML page

---

### Delete Sport Preference
**DELETE** `/profile/sports/<sport_id>/`  
**Auth:** Required

**Response:** Redirect

---

## Partner Matching

### Browse Users (API)
**GET** `/partner-matching/browse-users-api/`  
**Auth:** Required

**Query Parameters:**
- `search` (optional): Search by username or full_name
- `city` (optional): Filter by city
- `sport` (optional): Filter by sport_type
- `skill` (optional): Filter by skill_level

**Response (200):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "string",
      "full_name": "string",
      "city": "string",
      "profile_picture_url": "string",
      "sports": "Football (Advanced), Basketball (Intermediate)"
    }
  ]
}
```

---

### Connection Request
**POST** `/partner-matching/connection/<action>/<user_id>/`  
**Auth:** Required

**Actions:** `send`, `accept`, `reject`, `remove`

**Response (200):**
```json
{
  "success": true,
  "message": "Connection request sent"
}
```

**Response (400):**
```json
{
  "success": false,
  "error": "Cannot connect with yourself"
}
```

---

### Get Connections
**GET** `/partner-matching/connections/`  
**Auth:** Required

**Response (200):** HTML page with connections list

---

### Get Public Connections
**GET** `/partner-matching/profile/<user_id>/connections/`
**Auth:** Required

**Response (200):** HTML page

---

## Event Discovery

### Browse Events (HTML)
**GET** `/event-discovery/events/`
**Auth:** Not required

**Response (200):** HTML page with event listing and filters

---

### Get All Events (JSON)
**GET** `/event-discovery/events/json/`
**Auth:** Not required

**Description:** Returns all upcoming events (future events or events happening today that haven't started yet), ordered by date and time.

**Response (200):**
```json
[
  {
    "id": "1",
    "organizer": "username",
    "title": "string",
    "description": "string",
    "thumbnail": "string (URL)",
    "sport_type": "football",
    "event_date": "2024-12-31",
    "start_time": "10:00:00",
    "end_time": "12:00:00",
    "city": "jakarta_selatan",
    "location_name": "string",
    "max_participants": 10,
    "current_participants": 5,
    "status": "open",
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
  }
]
```

---

### Get Event Detail (HTML)
**GET** `/event-discovery/events/<id>/`
**Auth:** Not required

**Response (200):** HTML page with event details

---

### Get Event Detail (JSON)
**GET** `/event-discovery/events/<id>/json/`
**Auth:** Not required

**Response (200):**
```json
{
  "id": "1",
  "organizer": "username",
  "title": "string",
  "description": "string",
  "thumbnail": "string (URL)",
  "sport_type": "football",
  "event_date": "2024-12-31",
  "start_time": "10:00:00",
  "end_time": "12:00:00",
  "city": "jakarta_selatan",
  "location_name": "string",
  "max_participants": 10,
  "current_participants": 5,
  "status": "open",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

**Response (404):**
```json
{
  "error": "Event not found"
}
```

---

### Join Event
**POST** `/event-discovery/events/<id>/join/`
**Auth:** Required
**CSRF:** Exempt

**Response (201):**
```json
{
  "message": "Joined"
}
```

**Response (400):**
```json
{
  "message": "Event is full"
}
```
or
```json
{
  "message": "Could not join"
}
```

---

### Leave Event
**POST** `/event-discovery/events/<id>/leave/`
**Auth:** Required
**CSRF:** Exempt

**Response (201):**
```json
{
  "message": "Left"
}
```

**Response (404):**
```json
{
  "message": "Not Found"
}
```

---

### Get My Joined Events (HTML)
**GET** `/event-discovery/events/my-joined/`
**Auth:** Required

**Response (200):** HTML page with user's joined events

---

### Get My Joined Events (JSON)
**GET** `/event-discovery/events/my-joined/json/`
**Auth:** Required

**Description:** Returns all events the current user has joined as a participant.

**Response (200):**
```json
[
  {
    "id": "1",
    "organizer": "username",
    "title": "string",
    "description": "string",
    "thumbnail": "string (URL)",
    "sport_type": "football",
    "event_date": "2024-12-31",
    "start_time": "10:00:00",
    "end_time": "12:00:00",
    "city": "jakarta_selatan",
    "location_name": "string",
    "max_participants": 10,
    "current_participants": 5,
    "status": "open",
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
  }
]
```

---

### Get Event Participant Status
**GET** `/event-discovery/events/<id>/participant-status/`
**Auth:** Required

**Description:** Check if the current user is participating in the event and their participation status.

**Response (200):**
```json
{
  "status": "joined"
}
```
or
```json
{
  "status": "attended"
}
```
or
```json
{
  "status": "not_participating"
}
```

**Note:** Possible status values: `joined`, `attended`, `cancelled`, `not_participating`

---

### Check Event Has Attended Participants
**GET** `/event-discovery/events/<id>/has-attended-participants/`
**Auth:** Required

**Description:** Check if the event has any attended participants (excluding the current user). Used to determine if reviews can be submitted.

**Response (200):**
```json
{
  "has_attended_participants": true
}
```

---

### Check User Has Reviewed Event
**GET** `/event-discovery/events/<id>/user-has-reviewed/`
**Auth:** Required

**Description:** Check if the current user has already submitted reviews for participants in this event.

**Response (200):**
```json
{
  "has_reviewed": true
}
```

---

### Proxy Image
**GET** `/event-discovery/proxy-image/?url=<image_url>`
**Auth:** Not required

**Description:** Proxy endpoint to fetch and serve external images (used for event thumbnails).

**Query Parameters:**
- `url` (required): The external image URL to fetch

**Response (200):** Image content with appropriate Content-Type header

**Response (400):**
```
No URL provided
```

**Response (500):**
```
Error fetching image: <error_message>
```

---

## Event Management

### Create Event
**POST** `/event-management/create/`
**Auth:** Required

**Request Body (JSON):**
```json
{
  "title": "string",
  "description": "string",
  "thumbnail": "string (URL)",
  "sport_type": "football",
  "event_date": "2024-12-31",
  "start_time": "10:00:00",
  "end_time": "12:00:00",
  "city": "jakarta_selatan",
  "location_name": "string",
  "max_participants": 10
}
```

**Response (200):**
```json
{
  "success": true,
  "redirect_url": "/event-management/my-events/",
  "message": "Event created successfully!"
}
```

**Response (400):**
```json
{
  "success": false,
  "errors": {
    "title": ["This field is required."]
  }
}
```

---

### Get My Events
**GET** `/event-management/my-events/`
**Auth:** Required

**Response (200):** HTML page with upcoming and past events

---

### Update Event
**PUT** `/event-management/<event_id>/edit/`
**Auth:** Required (must be organizer)

**Request Body (JSON):**
```json
{
  "title": "string",
  "description": "string",
  "thumbnail": "string (URL)",
  "sport_type": "football",
  "event_date": "2024-12-31",
  "start_time": "10:00:00",
  "end_time": "12:00:00",
  "city": "jakarta_selatan",
  "location_name": "string",
  "max_participants": 10
}
```

**Response (200):**
```json
{
  "success": true,
  "redirect_url": "/event-management/my-events/",
  "message": "Event updated successfully!"
}
```

---

### Delete Event
**DELETE** `/event-management/<event_id>/delete/`
**Auth:** Required (must be organizer)

**Response (200):**
```json
{
  "success": true,
  "event_id": 1,
  "message": "Event deleted successfully."
}
```

---

### Cancel Event
**POST** `/event-management/<event_id>/cancel/`
**Auth:** Required (must be organizer)

**Response (200):**
```json
{
  "success": true,
  "event_id": 1,
  "message": "Event has been cancelled."
}
```

---

### Get Event Participants
**GET** `/event-management/<event_id>/participants/`
**Auth:** Required (must be organizer)

**Response (200):** HTML page with participants list

---

### Manage Participants
**POST** `/event-management/<event_id>/participants/`
**Auth:** Required (must be organizer)

**Request Body (JSON):**
```json
{
  "action": "remove",  // or "mark_attended"
  "user_id": 1
}
```

**Response (200):**
```json
{
  "success": true,
  "action": "remove",
  "user_id": 1,
  "message": "Participant removed successfully."
}
```

---

## Reviews & Rating

### Create Event Reviews (AJAX)
**POST** `/reviews/ajax/event/<event_id>/create/`
**Auth:** Required

**Request Body (Form Data):**
```
rating_<user_id>=5
comment_<user_id>=Great player!
rating_<user_id2>=4
comment_<user_id2>=Good teamwork
```

**Response (200):**
```json
{
  "ok": true,
  "created": [
    {
      "id": 1,
      "to_user": "username",
      "rating": 5,
      "comment": "Great player!",
      "event_title": "Event Title",
      "created_at": "2024-01-01 10:00"
    }
  ],
  "skipped": [2, 3]
}
```

---

### Get Event Reviews
**GET** `/reviews/<event_id>/`
**Auth:** Required

**Response (200):** HTML page with reviews for event

---

### Get User Reviews (Received)
**GET** `/reviews/user/<user_id>/`
**Auth:** Required

**Response (200):** HTML page with reviews received by user

---

### Get User Written Reviews
**GET** `/reviews/written/<user_id>/`
**Auth:** Required

**Response (200):** HTML page with reviews written by user

---

### Update Review (AJAX)
**POST** `/reviews/ajax/review/<review_id>/update/`
**Auth:** Required (must be review author)

**Request Body:**
```json
{
  "rating": 5,
  "comment": "Updated comment"
}
```

**Response (200):**
```json
{
  "ok": true,
  "review": {
    "id": 1,
    "to_user": "username",
    "event_title": "Event Title",
    "rating": 5,
    "comment": "Updated comment",
    "created_at": "2024-01-01 10:00"
  }
}
```

**Response (403):**
```json
{
  "ok": false,
  "error": "Forbidden"
}
```

---

### Delete Review (AJAX)
**POST** `/reviews/ajax/review/<review_id>/delete/`
**Auth:** Required (must be review author)

**Response (200):**
```json
{
  "ok": true,
  "deleted_id": 1
}
```

---

## Leaderboard

### Get Leaderboard (API)
**GET** `/leaderboard/api/leaderboard/`
**Auth:** Not required

**Query Parameters:**
- `period` (optional): `all_time`, `weekly`, `monthly` (default: `all_time`)
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)

**Response (200):**
```json
{
  "success": true,
  "users": [
    {
      "rank": 1,
      "user_id": 1,
      "username": "string",
      "full_name": "string",
      "profile_picture_url": "string",
      "total_points": 500,
      "total_events": 10
    }
  ],
  "total_count": 100,
  "page": 1,
  "per_page": 20,
  "current_user_rank": 5
}
```

---

### Get Points Dashboard
**GET** `/leaderboard/points/dashboard/`
**Auth:** Required

**Response (200):** HTML page with points breakdown

---

### Get Points History
**GET** `/leaderboard/points/history/`
**Auth:** Required

**Response (200):** HTML page with point transactions

---

### Get Achievements
**GET** `/leaderboard/achievements/`
**Auth:** Required

**Response (200):** HTML page with user achievements

---

## Constants & Enums

### CITY_CHOICES
```
ambon, banda_aceh, bandar_lampung, bandung, banjar, banjarbaru,
banjarmasin, batu, batam, baubau, bekasi, bengkulu, bima, binjai,
bitung, blitar, bogor, bontang, bukittinggi, cilegon, cimahi,
cirebon, denpasar, depok, dumai, gorontalo, gunungsitoli,
jakarta_barat, jakarta_pusat, jakarta_selatan, jakarta_timur,
jakarta_utara, jambi, jayapura, kediri, kendari, kotamobagu,
kupang, langsa, lhokseumawe, lubuk_linggau, madiun, magelang,
makassar, malang, manado, mataram, medan, metro, mojokerto,
nusantara, padang, padang_panjang, padangsidimpuan, pagar_alam,
palangka_raya, palembang, palopo, palu, pangkalpinang, pariaman,
parepare, pasuruan, payakumbuh, pekalongan, pekanbaru,
pematangsiantar, pontianak, prabumulih, probolinggo, sabang,
salatiga, samarinda, sawahlunto, semarang, serang, sibolga,
singkawang, solok, sorong, subulussalam, sukabumi, sungai_penuh,
surabaya, surakarta, tangerang, tangerang_selatan, tanjungbalai,
tanjungpinang, tarakan, tasikmalaya, tebing_tinggi, tegal,
ternate, tidore_kepulauan, tomohon, tual, yogyakarta
```

### SPORT_CHOICES
```
football, basketball, badminton, tennis, running, cycling,
swimming, volleyball
```

### SKILL_CHOICES
```
beginner, intermediate, advanced
```

### EVENT_STATUS
```
open, full, completed, cancelled
```

### PARTICIPANT_STATUS
```
joined, attended, cancelled
```

### CONNECTION_STATUS
```
pending, accepted, rejected
```

---

## Authentication Notes

1. **Session-based Auth**: All authenticated endpoints require valid Django session cookie
2. **CSRF Token**: POST/PUT/DELETE requests require CSRF token in headers or form data
3. **AJAX Requests**: Set header `X-Requested-With: XMLHttpRequest` for JSON responses
4. **Error Handling**:
   - 401: Unauthorized (not logged in)
   - 403: Forbidden (no permission)
   - 404: Not found
   - 400: Bad request (validation errors)

---

## Data Models

### User
```json
{
  "id": 1,
  "username": "string",
  "email": "string"
}
```

### UserProfile
```json
{
  "user": 1,
  "full_name": "string",
  "bio": "string",
  "city": "string",
  "profile_image_url": "string",
  "total_points": 0,
  "total_events": 0,
  "created_at": "2024-01-01T10:00:00Z"
}
```

### SportPreference
```json
{
  "id": 1,
  "user": 1,
  "sport_type": "football",
  "skill_level": "intermediate",
  "created_at": "2024-01-01T10:00:00Z"
}
```

### Event
```json
{
  "id": 1,
  "organizer": 1,
  "title": "string",
  "description": "string",
  "thumbnail": "string",
  "sport_type": "football",
  "event_date": "2024-12-31",
  "start_time": "10:00:00",
  "end_time": "12:00:00",
  "city": "jakarta_selatan",
  "location_name": "string",
  "max_participants": 10,
  "current_participants": 5,
  "status": "open",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### EventParticipant
```json
{
  "id": 1,
  "event": 1,
  "user": 1,
  "status": "joined",
  "joined_at": "2024-01-01T10:00:00Z"
}
```

### Connection
```json
{
  "id": 1,
  "from_user": 1,
  "to_user": 2,
  "status": "pending",
  "message": "string",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### Review
```json
{
  "id": 1,
  "event": 1,
  "from_user": 1,
  "to_user": 2,
  "rating": 5,
  "comment": "string",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### PointTransaction
```json
{
  "id": 1,
  "user": 1,
  "activity_type": "event_join",
  "points": 10,
  "description": "string",
  "related_event": 1,
  "created_at": "2024-01-01T10:00:00Z"
}
```

### Achievement
```json
{
  "id": 1,
  "user": 1,
  "achievement_code": "first_event",
  "title": "First Event",
  "description": "string",
  "bonus_points": 50,
  "earned_at": "2024-01-01T10:00:00Z"
}
```

---

## Points System

| Activity | Points | Trigger |
|----------|--------|---------|
| Join Event | +10 | EventParticipant created |
| Complete Event | +30 | EventParticipant status = 'attended' |
| Organize Event | +50 | Event status = 'completed' |
| Give Review | +5 | Review created |
| Get 5-star Review | +10 | Review with rating = 5 received |

---

## Achievement Codes

- `first_event`: First Event (Join first event)
- `ten_events`: 10 Events (Complete 10 events)
- `organizer`: Organizer (Organize 5 events)
- `highly_rated`: Highly Rated (Get 10 five-star reviews)
- `social_butterfly`: Social Butterfly (Make 20 connections)
- `early_bird`: Early Bird (Join 5 morning events)