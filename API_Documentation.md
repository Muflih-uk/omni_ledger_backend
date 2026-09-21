# Omni Ledger — API Documentation

A complete billing system for shop owners, built with **FastAPI**, **SQLAlchemy**, and **JWT** authentication.

- **Base URL:** `http://localhost:8000` (configurable)
- **API Version:** `1.0.0`
- **Interactive Docs:** FastAPI auto-generates Swagger UI at `/docs` and ReDoc at `/redoc`
- **OpenAPI JSON:** `/openapi.json`

---

## Table of Contents

- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Root](#root)
  - [Authentication](#authentication-endpoints)
  - [Items](#items)
  - [Bills](#bills)
- [Data Models](#data-models)
- [Known Caveats & Notes](#known-caveats--notes)

---

## Authentication

The API uses **JWT (JSON Web Token)** bearer authentication.

1. Register an account (`POST /auth/register`), then log in (`POST /auth/login`) to obtain a token.
2. Include the token in every protected request:

```
Authorization: Bearer <access_token>
```

All protected endpoints (Items & Bills) require a **user** token. There are no admin roles.

---

## Error Handling

All errors return a JSON body:

```json
{
  "detail": "Human-readable error message"
}
```

| Status Code | Meaning | Common Causes |
|---|---|---|
| `400` | Bad Request | Duplicate phone number on registration |
| `401` | Unauthorized | Missing/invalid credentials, invalid/expired token |
| `403` | Forbidden | Deactivated account |
| `404` | Not Found | Item or bill does not exist / not owned by the caller |

---

## Endpoints

### Root

#### `GET /`

Health check. Returns a simple welcome message.

**Auth required:** No

**Response `200 OK`**

```json
{
  "message": "Billing System API is running 🚀"
}
```

---

### Authentication Endpoints

#### `POST /auth/register`

Registers a new user by name, phone number, and password. The password is hashed with bcrypt before storing.

**Auth required:** No

**Request Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | Full name |
| `phone` | string | yes | Unique phone number (acts as the username) |
| `password` | string | yes | Plain-text password (hashed before storage) |

```json
{
  "name": "John Doe",
  "phone": "9876543210",
  "password": "secret123"
}
```

**Response `200 OK`** — the created user:

```json
{
  "id": 1,
  "name": "John Doe",
  "phone": "9876543210",
  "is_active": true,
  "created_at": "2026-09-20T12:00:00Z"
}
```

**Errors**

| Code | Detail |
|---|---|
| `400` | `Phone number already registered` |

---

#### `POST /auth/login`

Logs in a **user** by phone number and password. Returns a JWT access token.

**Auth required:** No

**Request Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `phone` | string | yes | Registered phone number |
| `password` | string | yes | Account password |

```json
{
  "phone": "9876543210",
  "password": "secret123"
}
```

**Response `200 OK`**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "user"
}
```

**Errors**

| Code | Detail |
|---|---|
| `401` | `Phone number not registered` |
| `401` | `Incorrect password` |
| `403` | `Account is deactivated` |

---

### Items

All endpoints in this section require a **user** bearer token:

```
Authorization: Bearer <user_access_token>
```

> Missing/invalid tokens receive `401 Invalid or expired token`.

#### `POST /items`

Creates a new item.

**Auth required:** User

**Request Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | Item name |
| `unit_price` | number (float) | yes | Price per unit |

```json
{
  "name": "Milk Packet",
  "unit_price": 45.0
}
```

**Response `200 OK`**

```json
{
  "id": 1,
  "name": "Milk Packet",
  "unit_price": 45.0,
  "created_at": "2026-09-20T12:00:00Z"
}
```

---

#### `GET /items`

Lists **all** items across every user.

**Auth required:** User

**Response `200 OK`**

```json
[
  {
    "id": 1,
    "name": "Milk Packet",
    "unit_price": 45.0,
    "created_at": "2026-09-20T12:00:00Z"
  }
]
```

> ⚠️ **Note:** Items are **not scoped to the owning user** — this endpoint returns items created by all users.

---

#### `PUT /items/{item_id}`

Updates an existing item's name and/or unit price.

**Auth required:** User

**Path Parameters**

| Parameter | Type | Description |
|---|---|---|
| `item_id` | integer | ID of the item |

**Request Body** (all fields optional; omit fields you don't want to change)

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | no | New name |
| `unit_price` | number (float) | no | New unit price |

```json
{
  "name": "Milk Packet 1L",
  "unit_price": 50.0
}
```

**Response `200 OK`**

```json
{
  "id": 1,
  "name": "Milk Packet 1L",
  "unit_price": 50.0,
  "created_at": "2026-09-20T12:00:00Z"
}
```

**Errors**

| Code | Detail |
|---|---|
| `404` | `Item not found` |

---

#### `DELETE /items/{item_id}`

Deletes an item by ID.

**Auth required:** User

**Path Parameters**

| Parameter | Type | Description |
|---|---|---|
| `item_id` | integer | ID of the item |

**Response `200 OK`**

```json
{
  "message": "Item removed"
}
```

**Errors**

| Code | Detail |
|---|---|
| `404` | `Item not found` |

---

### Bills

All endpoints in this section require a **user** bearer token.

```
Authorization: Bearer <user_access_token>
```

> ⚠️ **Note:** Bills are **not scoped to the owning user** — like Items, all bills are visible to any authenticated user regardless of which account created them (`owner_id` is still recorded on the bill).

#### `POST /bills`

Creates a bill. Prices are computed server-side from each item's `unit_price × quantity`.

**Auth required:** User

**Request Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `customer_name` | string | yes | Customer name |
| `customer_phone` | string | yes | Customer phone number |
| `items` | array of `{item_id, quantity}` | yes | At least one item |
| `payment_status` | enum `paid` / `unpaid` | no | Defaults to `unpaid` |

```json
{
  "customer_name": "Alice",
  "customer_phone": "9123456780",
  "items": [
    { "item_id": 1, "quantity": 2 },
    { "item_id": 2, "quantity": 1 }
  ],
  "payment_status": "unpaid"
}
```

**Response `200 OK`**

```json
{
  "id": 5,
  "customer_name": "Alice",
  "customer_phone": "9123456780",
  "total_amount": 140.0,
  "payment_status": "unpaid",
  "created_at": "2026-09-20T12:00:00Z",
  "items": [
    {
      "id": 11,
      "item_id": 1,
      "item_name": "Milk Packet",
      "quantity": 2,
      "price": 90.0
    },
    {
      "id": 12,
      "item_id": 2,
      "item_name": "Bread",
      "quantity": 1,
      "price": 50.0
    }
  ]
}
```

**Errors**

| Code | Detail |
|---|---|
| `404` | `Item {item_name} not found` |

---

#### `GET /bills`

Lists all bills belonging to the authenticated user.

**Auth required:** User

**Response `200 OK`**

```json
[
  {
    "id": 5,
    "customer_name": "Alice",
    "customer_phone": "9123456780",
    "total_amount": 140.0,
    "payment_status": "unpaid",
    "created_at": "2026-09-20T12:00:00Z",
    "items": []
  }
]
```

---

#### `GET /bills/paid`

Lists bills with `payment_status = "paid"` for the authenticated user.

**Auth required:** User

**Response `200 OK`** — array of `BillResponse` objects (same shape as `GET /bills`).

---

#### `GET /bills/unpaid`

Lists bills with `payment_status = "unpaid"` for the authenticated user.

**Auth required:** User

**Response `200 OK`** — array of `BillResponse` objects (same shape as `GET /bills`).

> ⚠️ **Note:** `/bills/paid` and `/bills/unpaid` are declared **before** `/bills/{bill_id}` in the router so they are matched first. Order is intentional — do not reorder.

---

#### `GET /bills/{bill_id}`

Fetches a single bill owned by the authenticated user.

**Auth required:** User

**Path Parameters**

| Parameter | Type | Description |
|---|---|---|
| `bill_id` | integer | ID of the bill |

**Response `200 OK`**

```json
{
  "id": 5,
  "customer_name": "Alice",
  "customer_phone": "9123456780",
  "total_amount": 140.0,
  "payment_status": "unpaid",
  "created_at": "2026-09-20T12:00:00Z",
  "items": [
    {
      "id": 11,
      "item_id": 1,
      "item_name": "Milk Packet",
      "quantity": 2,
      "price": 90.0
    }
  ]
}
```

**Errors**

| Code | Detail |
|---|---|
| `404` | `Bill not found` |

---

#### `PATCH /bills/{bill_id}/payment-status`

Toggles a bill's payment status between `paid` and `unpaid`.

**Auth required:** User

**Path Parameters**

| Parameter | Type | Description |
|---|---|---|
| `bill_id` | integer | ID of the bill |

**Request Body:** none

**Response `200 OK`** — the bill with updated `payment_status`:

```json
{
  "id": 5,
  "customer_name": "Alice",
  "customer_phone": "9123456780",
  "total_amount": 140.0,
  "payment_status": "paid",
  "created_at": "2026-09-20T12:00:00Z",
  "items": []
}
```

**Errors**

| Code | Detail |
|---|---|
| `404` | `Bill not found` |

---

#### `POST /bills/{bill_id}/send-sms`

Sends the bill details to the customer's phone number as an SMS via **Twilio**.

**Auth required:** User

**Path Parameters**

| Parameter | Type | Description |
|---|---|---|
| `bill_id` | integer | ID of the bill |

**Request Body:** none

**Response `200 OK`**

On success:

```json
{
  "message": "SMS sent successfully (SID: SMxxxxxxxxxxxxxxxx)"
}
```

On failure (e.g., invalid Twilio config):

```json
{
  "message": "SMS failed"
}
```

**Errors**

| Code | Detail |
|---|---|
| `404` | `Bill not found` |

---

## Data Models

### User

| Field | Type | Description |
|---|---|---|
| `id` | integer | Primary key |
| `name` | string | Full name |
| `phone` | string | Unique phone number (indexed) |
| `password_hash` | string | bcrypt hash (never returned by API) |
| `is_active` | boolean | Whether the account is active |
| `created_at` | datetime | UTC creation timestamp |

### Item

| Field | Type | Description |
|---|---|---|
| `id` | integer | Primary key |
| `name` | string | Item name |
| `unit_price` | float | Price per unit |
| `is_active` | boolean | Defaults to `true` (not exposed via API) |
| `created_at` | datetime | UTC creation timestamp |

### Bill

| Field | Type | Description |
|---|---|---|
| `id` | integer | Primary key |
| `customer_name` | string | Customer name |
| `customer_phone` | string | Customer phone |
| `total_amount` | float | Computed total (`Σ unit_price × quantity`) |
| `payment_status` | enum | `paid` or `unpaid` |
| `created_at` | datetime | UTC creation timestamp |
| `owner_id` | integer (FK) | The user who owns the bill |

### BillItem

| Field | Type | Description |
|---|---|---|
| `id` | integer | Primary key |
| `bill_id` | integer (FK) | Parent bill |
| `item_id` | integer (FK) | Purchased item |
| `quantity` | integer | Quantity (default `1`) |
| `price` | float | Line total (`unit_price × quantity`) |

### `PaymentStatus` Enum

| Value | Description |
|---|---|
| `paid` | Bill is paid |
| `unpaid` | Bill is pending payment |

---

## Known Caveats & Notes

1. **Token expiry mislabeled.** `create_access_token` actually signs the token with `timedelta(weeks=ACCESS_TOKEN_EXPIRE_MINUTES)` (it uses **weeks**, not minutes) despite the environment variable being named `ACCESS_TOKEN_EXPIRE_MINUTES`. With the default value of `60`, the token lives ~60 weeks, not 60 minutes.

2. **Items are not ownership-scoped.** `GET /items` returns every item in the table regardless of which user created it.

3. **Bills are not ownership-scoped.** `GET /bills` (and `/paid`, `/unpaid`, `/{bill_id}`, payment toggle, and SMS endpoints) operate on every bill in the table, not just those created by the logged-in user. `owner_id` is still recorded when a bill is created but is not used to filter reads.

4. **Enum values are lowercase strings.** `payment_status` uses `"paid"` / `"unpaid"` (not capitalized).

5. **SMS is a best-effort call.** `send_bill_sms` catches all exceptions and returns `"SMS failed"` with HTTP `200` — check the `message` field to detect failure.

6. **Register does not auto-login.** `POST /auth/register` returns the user object only; call `POST /auth/login` afterwards to receive an access token.

7. **CORS is wide open.** All origins, methods, and headers are allowed (`allow_origins=["*"]`), which is fine for development but should be tightened for production.