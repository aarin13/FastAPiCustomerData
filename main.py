from fastapi import FastAPI
import pandas as pd
from pydantic import BaseModel, Field
from datetime import datetime



data = pd.read_excel(r"C:\Users\HP\Desktop\Bajaj_Assignment1\Data.xlsx", sheet_name=None)
accounts = data['Accounts'][['AccountId', 'Name', 'Age', 'City', 'State', 'Pincode']] 
claims = data['Claims'][['Id', 'CreatedDate', 'CaseNumber','HAN', 'BillAmount', 'Status', 'AccountId']] 
policies = data['Policies'][['HAN', 'Policy Name']]



history = pd.DataFrame(columns=["Table", "PrimaryKey", "Action", "Timestamp", "OldValue", "NewValue"])

app = FastAPI()


class Account(BaseModel):
    AccountId: str = Field(min_length=1)
    Name: str = Field(min_length=1)
    Age: int
    City: str = Field(min_length=1)
    State: str = Field(min_length=1)
    Pincode: int

class Claim(BaseModel):
    Id: str = Field(min_length=1)
    CreatedDate: str
    CaseNumber : str
    HAN: str
    BillAmount: float
    Status: str = Field(min_length=1)
    AccountId: str = Field(min_length=1)

class Policy(BaseModel):
    HAN: str = Field(min_length=1)
    PolicyName: str = Field(min_length=1)

@app.get("/")
def read_root():
    return "Root"

@app.get("/cus_info")
async def cus_info(account_id: str):
    try:
        global accounts, claims, policies
        cus_data = accounts[accounts['AccountId'] == account_id]
        cus_claims = claims[claims['AccountId'] == account_id]
        cus_policies = policies[policies['HAN'].isin(cus_claims['HAN'].unique())]

        return {
            "Customer": cus_data.to_dict(orient='records'),
            "Claims": cus_claims.to_dict(orient='records'),
            "Policies": cus_policies.to_dict(orient='records')
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/claim_details")
async def claim_details(claim_id: str):
    try:
        claim = claims[claims['Id'] == claim_id]
        account_id = claim['AccountId'].iloc[0]
        details = accounts[accounts['AccountId'] == account_id]
        return {
            'Claims': claim.to_dict(orient='records'),
            'Customer': details.to_dict(orient='records')
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/add_account")
async def add_account(account: Account):
    global accounts
    new_account = pd.DataFrame([account.model_dump()])
    accounts = pd.concat([accounts, new_account], ignore_index=True)
    log_history("Accounts", account.AccountId, "Create", None, new_account.to_dict(orient='records'))
    save_to_excel()
    return {"message": "Account created successfully", "Account": new_account.to_dict(orient='records')}

@app.delete("/delete_account")
async def delete_account(account_id: str):
    global accounts, claims
    account_data = accounts[accounts['AccountId'] == account_id]
    if account_data.empty:
        return {"error": "Account not found"}

    accounts = accounts[accounts['AccountId'] != account_id]
    claims = claims[claims['AccountId'] != account_id]

    log_history("Accounts", account_id, "Delete", account_data.to_dict(orient='records'), None)
    save_to_excel()
    return {"message": "Account deleted successfully"}

@app.post("/add_claim")
async def add_claim(claim: Claim):
    global claims
    new_claim = pd.DataFrame([claim.model_dump()])
    claims = pd.concat([claims, new_claim], ignore_index=True)
    log_history("Claims", claim.Id, "Create", None, new_claim.to_dict(orient='records'))
    save_to_excel()
    return {"message": "Claim added successfully", "Claim": new_claim.to_dict(orient='records')}

@app.delete("/delete_claim")
async def delete_claim(claim_id: str):
    global claims
    claim_data = claims[claims['Id'] == claim_id]
    if claim_data.empty:
        return {"error": "Claim not found"}

    claims = claims[claims['Id'] != claim_id]
    log_history("Claims", claim_id, "Delete", claim_data.to_dict(orient='records'), None)
    save_to_excel()
    return {"message": "Claim deleted successfully"}

def log_history(table, primary_key, action, old_value, new_value):
    global history
    history = pd.concat([history,pd.DataFrame(
                {
                    "Table": [table],
                    "PrimaryKey": [primary_key],
                    "Action": [action],
                    "Timestamp": [datetime.now()],
                    "OldValue": [old_value],
                    "NewValue": [new_value],
                }
            ),
        ],
        ignore_index=True,
    )

def save_to_excel():
    with pd.ExcelWriter(r"C:\Users\HP\Desktop\Bajaj_Assignment1\Data.xlsx", engine="openpyxl", mode="w") as writer:
        accounts.to_excel(writer, sheet_name="Accounts", index=False)
        claims.to_excel(writer, sheet_name="Claims", index=False)
        policies.to_excel(writer, sheet_name="Policies", index=False) 
        history.to_excel(writer, sheet_name="History", index=False) 
