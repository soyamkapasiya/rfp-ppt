from sqlalchemy import create_engine


def get_engine(url: str):
    return create_engine(url, pool_pre_ping=True)
