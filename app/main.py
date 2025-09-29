from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from . import database, models, schemas
import uvicorn
from passlib.context import CryptContext


#Create ALL DB tables:
models.Base.metadata.create_all(bind=database.engine)

#user security and protocols
pwd_context = CryptContext(schemas=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    #hash the plain password
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    #Verify a plain password against the hashed one ( we can still get to the original normal password via the hash due to Salt -> the random variable in the hashed password)
    return pwd_context.verify(plain_password,hashed_password)










app = FastAPI(title="Expense Tracker API")

#GET Welcome message
@app.get("/")
def root():
    return {"message": "Welcome to the Expense Tracker API! Visit /docs for API docs."}

#GET Health
@app.get("/health")
def health():
    return {"status": "ok"}

#####################################################################################

#POST expenses by User ID @ is a Decorator and automatically assumes the function underneath as a wrapper
@app.post("/expenses",response_model=schemas.ExpenseRead)
def create_expense(exp: schemas.ExpenseCreate, user_id:int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()  # NEW – validate user exists
    if not user:  # NEW
        raise HTTPException(status_code=404, detail="User not found")
    
    db_exp = models.Expense(**exp.model_dump(), user_id=user.id) #** unpacks dictionary as keyword arguments. So id etc are like variables
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    return db_exp

#GET all expenses by UserID e.g. http://127.0.0.1:8000/expenses?user_id=1
@app.get("/expenses", response_model=list[schemas.ExpenseRead])
def list_expenses(user_id:int, db:Session = Depends(database.get_db)): # ADJUSTED – added user_id
    user = db.query(models.User).filter(models.User.id==user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found") 
    return db.query(models.Expense).filter(models.Expense.user_id == user.id).all()

#GET all expenses 
@app.get("/expenses/all", response_model=list[schemas.ExpenseRead])
def list_expenses(db:Session = Depends(database.get_db)): # ADJUSTED – added user_id
    expense = db.query(models.Expense).filter(models.User.id==user_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="There are no expenses in the datatable")
    return db.query(models.Expense).all()

#FILTER For Expenses => You can now call /expenses/filter?user_id=1&category=food&min_amount=5
@app.get("/expenses/filter", response_model=list[schemas.ExpenseRead])
def filter_expenses(
    user_id: int,
    category: str | None = Query(default=None),
    min_amount: float | None = Query(default=None),
    max_amount: float | None = Query(default=None),
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Expense).filter(models.Expense.user_id == user_id)

    if category:
        query = query.filter(models.Expense.category == category)
    if min_amount:
        query = query.filter(models.Expense.amount >= min_amount)
    if max_amount:
        query = query.filter(models.Expense.amount <= max_amount)

    return query.all()



 #POST New User and password 
@app.post("/users",response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    existing_user=db.query(models.User).filter(models.User.username==user.username).first() #check duplicate username
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = get_password_hash(user.password) #  – placeholder for password hashing
    db_user = models.User(username=user.username, hashed_password = hashed_password)
    db.add(db_user) #  – add to session
    db.commit()#  – save to DB 
    db.refresh(db_user) # – get ID
    return db_user #return created user 

#GET list of users
@app.get("/users", response_model=list[schemas.UserRead])
def list_users(db:Session = Depends(database.get_db)):
    return db.query(models.User).all()





# #run Main


# if __name__ == "__main__":
#     uvicorn.run(
#         "app.main:app",   # module path to your FastAPI app
#         host="127.0.0.1",
#         port=8000,
#         reload=True       # automatically reloads on code changes
#     )



