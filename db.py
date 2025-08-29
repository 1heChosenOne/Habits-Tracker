from sqlalchemy import create_engine
engine=create_engine("sqlite:///database1.db",echo=True)

def get_conn():
    with engine.begin() as conn:
            yield conn