from sqlmodel import create_engine

# Create db engine instance
mysql_url="mysql+pymysql://apiuser_test:test_password@130.226.56.134:3306/nature_app"
engine = create_engine(mysql_url, echo=True)
