from database import engine
import models

models.Base.metadata.create_all(bind=engine)
print("DB 연결 및 테이블 생성 완료")
