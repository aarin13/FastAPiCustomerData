from fastapi import FastAPI
import pandas as pd

data = pd.read_excel(r"C:\Users\HP\Desktop\Bajaj_Assignment1\Data.xlsx", sheet_name= None)
accounts = data['Accounts']
claims = data['Claims']
policies = data['Policies']
accounts.drop('Unnamed: 0', axis = 1, inplace=True)
claims.drop('Unnamed: 0', axis = 1, inplace=True)
policies.drop('Unnamed: 0', axis = 1, inplace=True)

app = FastAPI()


@app.get("/")
def read_root():
    return 'Root'

@app.get("/account_details")
def account_details(account_id):
    details = accounts[accounts['AccountId'] == account_id]
    claim = claims[claims['AccountId'] == account_id]
    details = details.to_dict(orient = 'records')
    claimed = claim.to_dict(orient = 'records')

    return{'Account' : details, 'Claims': claimed}

@app.get("/claim_details")
def claim_details(claim_id):
    try:
        claim = claims[claims['Id'] == claim_id]
        account_id = claim['AccountId'][0] 
        details = accounts[accounts['AccountId'] == account_id]
        details = details.to_dict(orient = 'records')
        claimed = claim.to_dict(orient = 'records')

        return{ 'Claims': claimed, 'Account' : details}
    except Exception as e:
        print(e)
        return{ 'an error occured, please refer the terminal' }
    