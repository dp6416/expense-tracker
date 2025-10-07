from fastapi import FastAPI, Depends, HTTPException, Query, Form
from sqlalchemy.orm import Session
from . import database, models, schemas
import uvicorn
from passlib.context import CryptContext
from .auth import create_access_token, get_current_user


#Create ALL DB tables:
models.Base.metadata.create_all(bind=database.engine)

#user security and protocols
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    #hash the plain password
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    #Verify a plain password against the hashed one ( we can still get to the original normal password via the hash due to Salt -> the random variable in the hashed password)
    return pwd_context.verify(plain_password,hashed_password)
    print("Stored hash:", user.hashed_password)



app = FastAPI(title="Expense Tracker API")

#GET Welcome message
@app.get("/")
def root():
    return {"message": "Welcome to the Expense Tracker API! Visit /docs for API docs."}

#GET Health
@app.get("/health")
def health():
    return {"status": "ok"}

#POST TOKEN
@app.post("/token")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    #Login and get JWT token#
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(data={"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

#POST EXPENSE
@app.post("/expenses",response_model=schemas.ExpenseRead)
def create_expense(exp: schemas.ExpenseCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    
    db_exp = models.Expense(**exp.model_dump(), user_id=current_user.id) 
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    return db_exp

#GET EXPENSE
@app.get("/expenses", response_model=list[schemas.ExpenseRead])
def list_expenses( current_user: models.User = Depends(get_current_user), db:Session = Depends(database.get_db)): # ADJUSTED – added user_id
    user = db.query(models.User).filter(models.User.id==current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found") 
    return db.query(models.Expense).filter(models.Expense.user_id == current_user.id).all()

# #GET all expenses => security flaw!!
# @app.get("/expenses/all", response_model=list[schemas.ExpenseRead])
# def list_expenses(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)): # ADJUSTED – added user_id
#     expense = db.query(models.Expense).filter(models.Expense.user_id == current_user.id).first()
#     if not expense:
#         raise HTTPException(status_code=404, detail="There are no expenses in the datatable")
#     return db.query(models.Expense).all()

#FILTER For Expenses 
@app.get("/expenses/filter", response_model=list[schemas.ExpenseRead])
def filter_expenses(
    category: str | None = Query(default=None),
    min_amount: float | None = Query(default=None),
    max_amount: float | None = Query(default=None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user) #can filter is
):
    query = db.query(models.Expense).filter(models.Expense.user_id == current_user.id)

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


@app.get("/users", response_model=list[schemas.UserRead])
def list_users(current_user: models.User = Depends(get_current_user), db:Session = Depends(database.get_db)):
    return db.query(models.User).all()


# #run Main


# if __name__ == "__main__":
#     uvicorn.run(
#         "app.main:app",   # module path to your FastAPI app
#         host="127.0.0.1",
#         port=8000,
#         reload=True       # automatically reloads on code changes
#     )



