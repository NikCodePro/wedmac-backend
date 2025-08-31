# API Testing Documentation for Lead Capping System

This document provides detailed instructions to test the new lead capping system APIs, including payloads and expected responses.

---

## 1. Claim Lead API

**Endpoint:**  
`POST /leads/{lead_id}/claim/`

**Description:**  
Allows an artist to claim a lead. An artist can claim a lead only if the number of claimed artists is less than the lead's `max_claims`.

**Request Headers:**  
- Authorization: Bearer <token>

**Request Payload:**  
No body required.

**Response:**  
- **200 OK**  
```json
{
  "message": "Lead claimed successfully.",
  "lead_id": 123,
  "claimed_count": 2,
  "max_claims": 5
}
```

- **400 Bad Request** (if lead already claimed by max artists)  
```json
{
  "error": "Lead has reached maximum number of claims."
}
```

- **403 Forbidden** (if artist has no available leads)  
```json
{
  "error": "No leads available. Please purchase more leads."
}
```

- **404 Not Found** (if lead does not exist)  
```json
{
  "error": "Lead not found."
}
```

---

## 2. Book Lead API

**Endpoint:**  
`POST /leads/{lead_id}/book/`

**Description:**  
Allows an artist to book a lead they have previously claimed. Deducts one from the artist's available leads.

**Request Headers:**  
- Authorization: Bearer <token>

**Request Payload:**  
No body required.

**Response:**  
- **200 OK**  
```json
{
  "message": "Lead booked successfully.",
  "lead_id": 123,
  "status": "booked",
  "available_leads": 4
}
```

- **400 Bad Request** (if artist has not claimed the lead)  
```json
{
  "error": "You must claim the lead before booking."
}
```

- **403 Forbidden** (if artist has no available leads)  
```json
{
  "error": "No leads available. Please purchase more leads."
}
```

- **404 Not Found** (if lead does not exist)  
```json
{
  "error": "Lead not found."
}
```

---

## 3. Get My Claimed Leads API

**Endpoint:**  
`GET /leads/artist/my-claimed-leads/`

**Description:**  
Fetches all leads claimed by the authenticated artist.

**Request Headers:**  
- Authorization: Bearer <token>

**Response:**  
- **200 OK**  
```json
[
  {
    "id": 123,
    "makeup_types": [...],
    "first_name": "Jane",
    "last_name": "Doe",
    "phone": "1234567890",
    "email": "jane@example.com",
    "event_type": "wedding",
    "requirements": "...",
    "booking_date": "2024-07-01",
    "source": "website",
    "status": "claimed",
    "last_contact": null,
    "notes": "",
    "created_at": "2024-06-01T12:00:00Z",
    "updated_at": "2024-06-10T12:00:00Z",
    "service": "Bridal Makeup",
    "budget_range": "$500-$1000",
    "location": "New York",
    "assigned_to": "Artist Name",
    "requested_artist": null,
    "created_by": "Admin"
  },
  ...
]
```

---

## 4. Get Leads by Status API

**Endpoint:**  
`GET /leads/list/?status=claimed`

**Description:**  
Fetches leads filtered by status. Use `status=all` to fetch all leads.

**Request Headers:**  
- Authorization: Bearer <token>

**Response:**
- **200 OK**
```json
{
  "message": "Fetched claimed leads successfully.",
  "count": 10,
  "leads": [
    {
      "id": 123,
      "makeup_types": [...],
      "first_name": "Jane",
      "last_name": "Doe",
      "phone": "1234567890",
      "email": "jane@example.com",
      "event_type": "wedding",
      "requirements": "...",
      "booking_date": "2024-07-01",
      "source": "website",
      "status": "claimed",
      "last_contact": null,
      "notes": "",
      "created_at": "2024-06-01T12:00:00Z",
      "updated_at": "2024-06-10T12:00:00Z",
      "service": "Bridal Makeup",
      "budget_range": "$500-$1000",
      "location": "New York",
      "assigned_to": "Artist Name",
      "requested_artist": null,
      "max_claims": 5,
      "claimed_count": 3,
      "booked_count": 1
    }
  ]
}
```

---

## 5. Update Lead API

**Endpoint:**
`PUT /leads/{lead_id}/update/`

**Description:**
Update lead details including status, soft delete, assigned artist, etc.

**Request Headers:**
- Authorization: Bearer <token>

**Request Payload Example:**
```json
{
  "status": "booked"
}
```

**Response:**
- **200 OK**
```json
{
  "message": "Lead updated successfully.",
  "lead": { ... }
}
```

---

## 6. Set Max Claims API (Admin Only)

**Endpoint:**
`PUT /leads/{lead_id}/set-max-claims/`

**Description:**
Admin-only endpoint to set the maximum number of artists that can claim a specific lead.

**Request Headers:**
- Authorization: Bearer <admin_token>

**Request Payload:**
```json
{
  "max_claims": 5
}
```

**Response:**
- **200 OK**
```json
{
  "message": "Max claims updated successfully.",
  "lead_id": 123,
  "max_claims": 5,
  "current_claimed_count": 2
}
```

- **400 Bad Request** (invalid max_claims value)
```json
{
  "error": "max_claims must be a positive integer."
}
```

- **400 Bad Request** (current claims exceed new limit)
```json
{
  "error": "Cannot set max_claims to 3. Lead currently has 4 claimed artists."
}
```

- **403 Forbidden** (non-admin user)
```json
{
  "error": "Authentication credentials were not provided."
}
```

- **404 Not Found** (lead does not exist)
```json
{
  "error": "Lead not found."
}
```

---

## 7. Get Max Claims Info API (Admin Only)

**Endpoint:**
`GET /leads/{lead_id}/set-max-claims/`

**Description:**
Admin-only endpoint to get current max_claims information for a specific lead.

**Request Headers:**
- Authorization: Bearer <admin_token>

**Response:**
- **200 OK**
```json
{
  "lead_id": 123,
  "max_claims": 5,
  "current_claimed_count": 3,
  "available_slots": 2
}
```

---

## 8. Bulk Set Max Claims API (Admin Only)

**Endpoint:**
`PUT /leads/bulk-set-max-claims/`

**Description:**
Admin-only endpoint to set the maximum number of artists that can claim ALL leads at once.

**Request Headers:**
- Authorization: Bearer <admin_token>

**Request Payload:**
```json
{
  "max_claims": 5
}
```

**Response:**
- **200 OK**
```json
{
  "message": "Max claims updated successfully for 25 leads.",
  "max_claims": 5,
  "total_leads_updated": 25
}
```

- **400 Bad Request** (invalid max_claims value)
```json
{
  "error": "max_claims must be a positive integer."
}
```

- **400 Bad Request** (some leads have more claimed artists than new limit)
```json
{
  "error": "Cannot set max_claims to 3. The following leads have more claimed artists:",
  "problematic_leads": [
    {
      "lead_id": 123,
      "current_claimed_count": 4
    },
    {
      "lead_id": 456,
      "current_claimed_count": 5
    }
  ]
}
```

- **403 Forbidden** (non-admin user)
```json
{
  "error": "Authentication credentials were not provided."
}
```

- **404 Not Found** (no leads found)
```json
{
  "error": "No leads found to update."
}
```

---

## 9. Get Bulk Max Claims Statistics API (Admin Only)

**Endpoint:**
`GET /leads/bulk-set-max-claims/`

**Description:**
Admin-only endpoint to get statistics about max_claims across all leads.

**Request Headers:**
- Authorization: Bearer <admin_token>

**Response:**
- **200 OK**
```json
{
  "total_leads": 50,
  "leads_with_max_claims": 45,
  "leads_without_max_claims": 5,
  "max_claims_distribution": {
    "3": 10,
    "5": 25,
    "10": 10
  },
  "total_claimed_artists": 120,
  "total_booked_artists": 45,
  "average_claims_per_lead": 2.4
}
```

---

## Notes

- All endpoints require authentication.
- Replace `{lead_id}` with the actual lead ID.
- Use appropriate authentication tokens in the Authorization header.
- Ensure the artist has sufficient available leads before claiming or booking.
- The `claimed_count` and `max_claims` fields are returned in claim responses to help clients track claim limits.
- **Admin-only endpoints** require admin user authentication (user.is_staff = True).
- The Set Max Claims API includes validation to prevent setting a limit lower than the current number of claimed artists.

---

This documentation should help you test the new lead capping system APIs effectively. If you need a Postman collection or curl commands, please let me know.
