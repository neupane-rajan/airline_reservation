# Airline Reservation System API

A minimalist yet functional API for an airline reservation system built using FastAPI.

## Features

- JWT-based authentication (user registration, login, roles: admin, passenger, staff)
- Passenger management (CRUD for passenger details)
- Flight management module (CRUD for flights, admin access)
- Booking system:
  - Search available flights by date, source, destination
  - Book flight tickets
  - Cancel and view bookings
  - Generate e-tickets
- Mock payment gateway integration
- Admin dashboard endpoints for booking stats and revenue
- Modular design using FastAPI best practices
- PostgreSQL/SQLite support with SQLAlchemy ORM
- Pydantic models for schema validation
- Error handling and logging

## Project Structure

```
airline_reservation/
├── app/
│   ├── __init__.py
│   ├── main.py                # Application entry point
│   ├── database.py            # Database connection and session
│   ├── config.py              # Configuration settings
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   ├── routes/                # API endpoints
│   ├── services/              # Business logic
│   └── utils/                 # Utility functions
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/airline-reservation-system.git
cd airline-reservation-system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following content:
```
SECRET_KEY=your-secret-key-for-jwt
DATABASE_URL=sqlite:///./airline.db
```

## Running the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Documentation is available at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API Endpoints

### Authentication
- **POST /api/auth/register** - Register a new user
- **POST /api/auth/token** - Login and get access token
- **GET /api/auth/me** - Get current user info

### Passengers
- **GET /api/passengers/** - Get all passengers (staff only)
- **GET /api/passengers/{passenger_id}** - Get passenger details
- **PUT /api/passengers/{passenger_id}** - Update passenger details
- **DELETE /api/passengers/{passenger_id}** - Delete passenger (staff only)

### Flights
- **GET /api/flights/** - Get all active flights
- **POST /api/flights/search** - Search flights by criteria
- **GET /api/flights/{flight_id}** - Get flight details
- **POST /api/flights/** - Create new flight (admin only)
- **PUT /api/flights/{flight_id}** - Update flight details (admin only)
- **DELETE /api/flights/{flight_id}** - Soft delete flight (admin only)

### Bookings
- **GET /api/bookings/** - Get user bookings
- **GET /api/bookings/{booking_id}** - Get booking details
- **POST /api/bookings/** - Create a new booking
- **POST /api/bookings/{booking_id}/payment** - Process payment for booking
- **POST /api/bookings/{booking_id}/cancel** - Cancel booking
- **GET /api/bookings/{booking_id}/e-ticket** - Generate e-ticket

### Admin Dashboard
- **GET /api/admin/dashboard/stats** - Get system statistics (admin only)
- **GET /api/admin/revenue/monthly** - Get monthly revenue (admin only)
- **GET /api/admin/popular-routes** - Get most popular routes (admin only)

## User Roles

1. **Admin** - Full access to system, can manage flights, view reports
2. **Staff** - Can view passengers and bookings details
3. **Passenger** - Can book flights, view/cancel own bookings

## Authentication Flow

1. Register a user using `/api/auth/register`
2. Login with username and password at `/api/auth/token`
3. Include the received JWT token in subsequent requests:
   ```
   Authorization: Bearer {your_token}
   ```

## Development Notes

- This is a minimalist implementation suitable for educational purposes
- For production use, additional security measures should be implemented
- The payment gateway is mocked - integrate with a real payment provider for production