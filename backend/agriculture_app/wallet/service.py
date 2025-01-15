from stellar_sdk import Keypair, Server, TransactionBuilder, Operation, Asset, Network, exceptions
import pandas as pd
server = Server("https://horizon-testnet.stellar.org")
def check_balance(public_key: str):
    if public_key is None:
        return None
    try:
        account = server.accounts().account_id(public_key).call()
        balances = account['balances']
        balance_info = []
        for balance in balances:
            asset_type = balance['asset_type']
            balance_amount = balance['balance']
            balance_info.append({"asset_type": asset_type, "balance": balance_amount})
        return balance_info
    except Exception as error:
        print(f"Error checking balance: {error}")
        return None
    
def transfer(from_private_key:str,to_public_key:str,amount:float,public_key:str):
    try:
        source_keypair = Keypair.from_secret(from_private_key)
        if source_keypair.public_key!=public_key:
            return False,{"error_code":"invalid_secret_key","message":"Please enter a valid secret key"}
        source_account = server.load_account(source_keypair.public_key)
        current_balance=check_balance(source_keypair.public_key)
        if current_balance is None:
            return False, {"error_code":'account_not_found',"message":'This account may not exist.'}
        for each_asset in current_balance:
            if each_asset['asset_type'] == 'native':
                balance=float(each_asset['balance'])
        base_fee = server.fetch_base_fee()
        if balance<(amount+base_fee):
            return False, {'error_code':'insufficient_funds','message':'Insufficient funds to cover the transaction.'}
        transaction = (
            TransactionBuilder(
                source_account=source_account,
                network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                base_fee=base_fee,
            )
            .add_text_memo("Transfer from Django app")  
            .append_payment_op(to_public_key, Asset.native(), str(amount))  
            .build()
        )

        transaction.sign(source_keypair)

        response = server.submit_transaction(transaction)
        return True, {'transaction_id':response['id'],'memo':response['memo'],'fee_charged':response['fee_charged'],'created_at':response['created_at']}

    except exceptions.NotFoundError as e:
        return False, {"error_code":'account_not_found',"message":'This account may not exist.'}
    except exceptions.BadRequestError as e:
        return False, {'error_code':'insufficient_funds','message':'Insufficient funds to cover the transaction.'}
    except Exception as e:
        return False, {"error_code":'transaction_error',"message":'Transaction failed. Please try again later.'}
    

# def get_transactions(public_key: str):
#     if public_key is None:
#         return None
#     try:
#         transactions = server.transactions().for_account(public_key).limit(10).order(desc=True).call()
#         transaction_info = []

#         for record in transactions['_embedded']['records']:
#             transaction_details = {
#                 "transaction_id": record['id'],
#                 "created_at": record['created_at'],
#                 "fee_charged": "{:.5f}".format(int(record['fee_charged']) / 10_000_000),
#                 "source_account": record['source_account'],
#                 "operations": []
#             }

#             operations = server.operations().for_transaction(record['id']).call()
#             for op in operations['_embedded']['records']:
#                 operation_details = {
#                     "type": op['type'],
#                     "amount": op.get('amount', None) if op['type'] == 'payment' else op.get('starting_balance', None)  if op['type'] =='create_account' else None,
#                     "destination": op.get('to', None) if op['type'] == 'payment' else op.get('account', None) if op['type'] == 'create_account' else None,
#                     "source_account": op.get('from', record['source_account']) if op['type'] == 'payment' else op.get('funder', None) if op['type'] == 'create_account' else None,
#                 }
#                 transaction_details["operations"].append(operation_details)

#             transaction_info.append(transaction_details)
#         return transaction_info

#     except Exception as error:
#         print(f"Error fetching transactions: {error}")
#         return None



def get_transactions(public_key: str,desc,cursor=None):
    if not public_key:
        return None
    try:
        if cursor:
            operations = server.operations().cursor(str(cursor)).join('transactions').for_account(public_key).include_failed(True).limit(10).order(desc=desc).call()
        else:
            operations = server.operations().join('transactions').for_account(public_key).include_failed(True).limit(10).order(desc=desc).call()
        operation_data = []
        for op in operations['_embedded']['records']:
            operation_details={
                "transaction_id":op['transaction_hash'],
                "created_at":op['created_at'],
                "fee_charged":"{:.5f}".format(int(op['transaction']['fee_charged']) / 10_000_000),
                "type": op['type'],
                "amount": op.get('amount', None) if op['type'] == 'payment' else op.get('starting_balance', None) if op['type'] == 'create_account' else None,
                "destination": op.get('to', None) if op['type'] == 'payment' else op.get('account', None) if op['type'] == 'create_account' else None,
                "source_account":op.get('funder', None) if op['type'] == 'create_account' else op.get('from',op.get('source_account', None) ) ,
                "transaction_successful":op['transaction_successful']
            }
            operation_data.append(operation_details)
        next_cursor=operations['_embedded']['records'][-1]['paging_token'] if operations['_embedded']['records'] else None
        prev_cursor=operations['_embedded']['records'][0]['paging_token'] if operations['_embedded']['records'] else None
        if not desc:
            operation_data.reverse()
            next_cursor,prev_cursor=prev_cursor,next_cursor

        response_data={
            "next": next_cursor,
            "prev":None if cursor is None else prev_cursor,
            "operations":operation_data
        }
        return response_data

    except Exception as error:
        print(f"Error fetching transactions: {error}")
        return None