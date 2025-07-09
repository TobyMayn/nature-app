from sqlmodel import Field, SQLModel, create_engine, text


class Users(SQLModel, table=True):
    user_id: int = Field(primary_key=True)
    username: str = Field(max_length=25)
    password_hash: str = Field(max_length=30)
    email: str | None = Field(default=None, max_length=30)
    municipality: str | None = Field(default=None, max_length=40)


async def get_db():
    mysql_url="mysql+pymysql://apiuser_test:test_password@130.226.56.134:3306/nature_app"
    engine = create_engine(mysql_url, echo=True)
    conn = engine.connect()
    
    return [{"text": f"Engine created {conn.execute(text("show tables;")).all()}"}]