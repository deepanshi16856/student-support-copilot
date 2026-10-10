
import sqlite3

DATABASE_NAME = "tickets.db"


def initialize_db():
    """Create the ticket table if it does not exist."""
    with sqlite3.connect(DATABASE_NAME) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                recommended_action TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def add_analysis_method_column():
    """Add the analysis method column if it does not exist."""
    with sqlite3.connect(DATABASE_NAME) as connection:
        columns = [
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(tickets)"
            ).fetchall()
        ]

        if "analysis_method" not in columns:
            connection.execute("""
                ALTER TABLE tickets
                ADD COLUMN analysis_method TEXT
                DEFAULT 'Rule-based'
            """)


def save_ticket(result, analysis_method="Rule-based"):
    """Save an analyzed ticket and return its ID."""
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.execute("""
            INSERT INTO tickets (
                ticket, category, priority,
                recommended_action, analysis_method
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            result["ticket"],
            result["category"],
            result["priority"],
            result["recommended_action"],
            analysis_method
        ))

        return cursor.lastrowid


def get_all_tickets():
    """Retrieve all saved tickets, newest first."""
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.execute("""
            SELECT id, ticket, category, priority,
                   recommended_action, status, created_at,
                   analysis_method
            FROM tickets
            ORDER BY id DESC
        """)

        columns = [column[0] for column in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


def update_ticket_status(ticket_id, new_status):
    """Update the status of an existing ticket."""
    allowed_statuses = ["Open", "In Progress", "Resolved"]

    if new_status not in allowed_statuses:
        raise ValueError("Invalid ticket status.")

    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.execute(
            "UPDATE tickets SET status = ? WHERE id = ?",
            (new_status, ticket_id)
        )

        return cursor.rowcount > 0


if __name__ == "__main__":
    initialize_db()
    add_analysis_method_column()
    print("Database initialized successfully!")