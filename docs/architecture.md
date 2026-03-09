# Architecture

```mermaid
graph TD
    U[User in Telegram] -->|message/callback| BOT[aiogram Bot]
    BOT --> MW[DB Session Middleware]
    MW --> R{Router}
    R --> H1[start handler]
    R --> H2[catalog handler]
    R --> H3[booking handler - FSM]
    R --> H4[admin handler]

    H1 --> DB[(SQLite / PostgreSQL)]
    H2 --> DB
    H3 --> DB
    H4 --> DB

    H3 -->|notification| ADMIN[Admin Chat]
    H4 -->|broadcast| USERS[All Users]

    subgraph "Data Layer"
        DB
        SEED[seed.json] -->|on startup| DB
    end
```

## Components

**Handlers** - aiogram routers, each responsible for a feature (menu, catalog, booking, admin).

**FSM** - Finite State Machine for multi-step booking form. States: service -> name -> phone -> date -> confirm.

**Middleware** - injects async SQLAlchemy session into every handler via `data["session"]`.

**Repositories** - async CRUD functions. No ORM queries in handlers.

**Services** - business logic (phone validation, notification formatting, catalog seeding).
