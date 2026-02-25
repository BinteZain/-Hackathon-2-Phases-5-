recurring-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py             # Task data models
│   │   ├── recurring.py        # Recurring task models
│   │   └── events.py           # Event schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── recurrence.py       # Recurrence calculation logic
│   │   ├── task_creator.py     # Task creation service
│   │   └── event_publisher.py  # Dapr event publishing
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── database.py         # Database connection
│   └── routes/
│       ├── __init__.py
│       ├── health.py           # Health check endpoint
│       └── dapr.py             # Dapr subscription endpoint
├── tests/
│   ├── __init__.py
│   ├── test_recurrence.py
│   └── test_api.py
├── requirements.txt
├── Dockerfile
├── .env.example
├── .gitignore
└── README.md
