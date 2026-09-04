from config import db, app
import os

def populate_yoga_data():
    """Execute the yoga_data.sql file to populate the database with yoga asana data."""

    sql_file_path = os.path.join(os.path.dirname(__file__), 'yoga_data.sql')

    try:
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()

        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]

        with app.app_context():
            for statement in sql_statements:
                if statement:
                    db.session.execute(db.text(statement))

            db.session.commit()
            print("✅ Yoga data successfully populated!")

    except FileNotFoundError:
        print("❌ Error: yoga_data.sql file not found!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error populating data: {str(e)}")

if __name__ == "__main__":
    populate_yoga_data()
