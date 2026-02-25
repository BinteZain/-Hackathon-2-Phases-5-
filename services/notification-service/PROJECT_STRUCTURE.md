notification-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── models/
│   │   ├── __init__.py
│   │   ├── events.py           # Event schemas
│   │   └── notification.py     # Notification models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── notification.py     # Notification orchestration
│   │   ├── email_provider.py   # Email delivery
│   │   ├── push_provider.py    # Push notification delivery
│   │   ├── inapp_provider.py   # In-app notification storage
│   │   └── delivery_tracker.py # Track delivery status
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── database.py         # Database connection
│   └── routes/
│       ├── __init__.py
│       ├── health.py           # Health check endpoint
│       ├── dapr.py             # Dapr subscription endpoint
│       └── api.py              # REST API endpoints
├── tests/
│   ├── __init__.py
│   ├── test_providers.py
│   └── test_api.py
├── requirements.txt
├── Dockerfile
├── .env.example
├── .gitignore
└── README.md
