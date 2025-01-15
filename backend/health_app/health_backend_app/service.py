"""This example shows how to deploy a compiled contract to the Stellar network.
"""

from typing import List

from stellar_sdk import Keypair, Network, SorobanServer, scval
from stellar_sdk.contract import ContractClient, exceptions, AssembledTransaction


seller_secret = "SDMO4PRKKYCLJYVEOK56HS7D36DRXSZF7HYGQEBXRHQCFXOGQFIETYRH"      # Seller secret
buyer_secret = "SA42ZZGZODXYKUYKHL4LPFW52AQHIOY57F7VXPOFEPOAZE5MCFBNGKYV"       # Buyer secret
admin_public_key = "GAN4ACK4QRFYZMCXCBXMEBSTK7ARLMMGJ6XHB6BM2SVPFUWJUECD7TBV"   # Admin public key  
rpc_server_url = "https://soroban-testnet.stellar.org:443"
network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE
contract_file_path = "./snowvue_asset.wasm"

soroban_server = SorobanServer(rpc_server_url)


def validate_secret_key(secret_key,public_key):
    try:
        kp = Keypair.from_secret(secret_key)
    except Exception as error:
        return False
    if kp.public_key == public_key:
        return True
    else:
        return False

def get_wasm_bytes(contract,secret_key):
    try:
        print("uploading contract...")
        kp = Keypair.from_secret(secret_key)
        wasm_id = ContractClient.upload_contract_wasm(
            contract, kp.public_key, kp, soroban_server
        )
        print(f"contract wasm id: {wasm_id.hex()}")
        return wasm_id.hex()
    except Exception as error:
        return None

def deploy_contract(wasm_id,secret_key):
    try:
        seller_kp=Keypair.from_secret(secret_key)
        print("creating contract...")
        contract_id = ContractClient.create_contract(wasm_id=wasm_id, source=seller_kp.public_key, signer=seller_kp, soroban_server=soroban_server)
        print(f"contract id: {contract_id}")
        return contract_id
    except Exception as error:
        print(f"Error deploying contract: {error}")
        return None

def get_price(contract_id,data_points,user_id):
    print(f"Invoking  get price on contract {contract_id}...")
    data_points=set(data_points)
    health_data = {
        "height": scval.to_bool(True) if 'height' in data_points else scval.to_bool(False),
        "weight": scval.to_bool(True) if 'weight' in data_points else scval.to_bool(False),
        "weight_type": scval.to_bool(True) if 'weight_type' in data_points else scval.to_bool(False),
        "waist": scval.to_bool(True) if 'waist' in data_points else scval.to_bool(False),
        "waist_choices": scval.to_bool(True) if 'waist_choices' in data_points else scval.to_bool(False),
        "smoking_status": scval.to_bool(True) if 'smoking_status' in data_points else scval.to_bool(False),
        "vaping_status": scval.to_bool(True) if 'vaping_status' in data_points else scval.to_bool(False),
        "blood_pressure": scval.to_bool(True) if 'blood_pressure' in data_points else scval.to_bool(False),
        "a1c_level": scval.to_bool(True) if 'a1c_level' in data_points else scval.to_bool(False),
        "blood_sugar_level": scval.to_bool(True) if 'blood_sugar_level' in data_points else scval.to_bool(False),
        "pregnant": scval.to_bool(True) if 'pregnant' in data_points else scval.to_bool(False),
        "malaria": scval.to_bool(True) if 'malaria' in data_points else scval.to_bool(False),
        "covid": scval.to_bool(True) if 'covid' in data_points else scval.to_bool(False),
        "user_id": scval.to_bool(False),
        "id": scval.to_string(str(user_id))
    }

    # Build a transaction to invoke the function
    try:
        assembled: AssembledTransaction[List[str]] = (
        ContractClient(contract_id, rpc_server_url, network_passphrase)
            .invoke(
                "get_price",
                parameters=[
                    scval.to_struct(health_data)
                ],
                source=admin_public_key,
                parse_result_xdr_fn=lambda x: scval.from_int128(x),
            )
        )
        print(f"Result from simulation: {assembled.result()}")
        return assembled.result()/1000000
    except exceptions.AssembledTransactionError as e:
        print("Transaction failed, check the exception for more details.", e)
        return None

def invoke_initialize_health_data(contract_id,health_data:dict,secret_key):
    transform_data = {
        "height": scval.to_string(str(health_data.get("height"))) if health_data.get("height", None)!=None else scval.to_void(),
        "weight": scval.to_string(str(health_data.get("weight"))) if health_data.get("weight", None)!=None else scval.to_void(),
        "weight_type": scval.to_string(health_data.get("weight_type", None)) if health_data.get("weight_type", None)!=None else scval.to_void(),
        "waist": scval.to_string(str(health_data.get("waist"))) if health_data.get("waist", None)!=None else scval.to_void(),
        "waist_choices": scval.to_string(health_data.get("waist_choices")) if health_data.get("waist_choices", None)!=None else scval.to_void(),
        "smoking_status": scval.to_bool(health_data.get("smoking_status")) if health_data.get("smoking_status", None)!=None else scval.to_void(),
        "vaping_status": scval.to_bool(health_data.get("vaping_status")) if health_data.get("vaping_status", None)!=None else scval.to_void(),
        "blood_pressure": scval.to_string(str(health_data.get("blood_pressure"))) if health_data.get("blood_pressure", None)!=None else scval.to_void(),
        "a1c_level": scval.to_string(str(health_data.get("a1c_level"))) if health_data.get("a1c_level", None)!=None else scval.to_void(),
        "blood_sugar_level": scval.to_string(str(health_data.get("blood_sugar_level"))) if health_data.get("blood_sugar_level", None)!=None else scval.to_void(),
        "pregnant": scval.to_bool(health_data.get("pregnant")) if health_data.get("pregnant", None)!=None else scval.to_void(),
        "malaria": scval.to_bool(health_data.get("malaria")) if health_data.get("malaria", None)!=None else scval.to_void(),
        "covid": scval.to_bool(health_data.get("covid")) if health_data.get("covid", None)!=None else scval.to_void(),
        "user_id": scval.to_void()
    }
    print(f"Invoking initialize_health_data on contract {contract_id}...")
    try:
        seller_kp=Keypair.from_secret(secret_key)
        result = (
        ContractClient(contract_id, rpc_server_url, network_passphrase)
        .invoke(
            "initialize_health_data",
             parameters=[
                scval.to_address(seller_kp.public_key),  
                scval.to_address(admin_public_key),
                scval.to_struct(transform_data)
            ],
            source=seller_kp.public_key,
            parse_result_xdr_fn=lambda x: scval.from_bool(x),
        )
        .sign_and_submit(seller_kp)
        )
        print("Transaction success, result:", result)
        return True
    except exceptions.AssembledTransactionError as e:
        print("Transaction failed, check the exception for more details.", e)
        return None

    
# def get_price(contract_id):
#     print(f"Invoking  get price on contract {contract_id}...")

#     try:
#         assembled: AssembledTransaction[List[str]] = (
#         ContractClient(contract_id, rpc_server_url, network_passphrase)
#             .invoke(
#                 "get_price",
#                 parameters=[],
#                 source=admin_public_key,
#                 parse_result_xdr_fn=lambda x: scval.from_int128(x),
#             )
#         )
#         total_price=assembled.result()
#         print(f"Result from simulation: {total_price}")
#         return total_price
#     except exceptions.AssembledTransactionError as e:
#         print("Transaction failed, check the exception for more details.", e)
#         return None


def transfer(contract_id,buyer_secret,data_points,user_id,seller_public):
    print(f"Invoking transfer on contract {contract_id}...")

    tx_submitter_kp = Keypair.from_secret(
        buyer_secret  
    )
    health_data = {
        "height": scval.to_bool(True) if 'height' in data_points else scval.to_bool(False),
        "weight": scval.to_bool(True) if 'weight' in data_points else scval.to_bool(False),
        "weight_type": scval.to_bool(True) if 'weight_type' in data_points else scval.to_bool(False),
        "waist": scval.to_bool(True) if 'waist' in data_points else scval.to_bool(False),
        "waist_choices": scval.to_bool(True) if 'waist_choices' in data_points else scval.to_bool(False),
        "smoking_status": scval.to_bool(True) if 'smoking_status' in data_points else scval.to_bool(False),
        "vaping_status": scval.to_bool(True) if 'vaping_status' in data_points else scval.to_bool(False),
        "blood_pressure": scval.to_bool(True) if 'blood_pressure' in data_points else scval.to_bool(False),
        "a1c_level": scval.to_bool(True) if 'a1c_level' in data_points else scval.to_bool(False),
        "blood_sugar_level": scval.to_bool(True) if 'blood_sugar_level' in data_points else scval.to_bool(False),
        "pregnant": scval.to_bool(True)  if 'pregnant' in data_points else scval.to_bool(False), 
        "malaria": scval.to_bool(True) if 'malaria' in data_points else scval.to_bool(False),
        "covid": scval.to_bool(True) if 'covid' in data_points else scval.to_bool(False),
        "user_id": scval.to_bool(False),
        "id": scval.to_string(str(user_id))
    }
    try:
        result = (
        ContractClient(contract_id, rpc_server_url, network_passphrase)
        .invoke(
            "transfer",
             parameters=[
                scval.to_address(seller_public),
                scval.to_address(admin_public_key), 
                scval.to_address(tx_submitter_kp.public_key),
                scval.to_address("CDLZFC3SYJYDZT7K67VZ75HPJVIEUVNIXF47ZG2FB2RMQQVU2HHGCYSC"), 
                scval.to_struct(health_data) # XLM contract Id https://stellar.expert/explorer/testnet/contract/CDLZFC3SYJYDZT7K67VZ75HPJVIEUVNIXF47ZG2FB2RMQQVU2HHGCYSC
            ],
            source=tx_submitter_kp.public_key,
            parse_result_xdr_fn=lambda x: scval.from_bool(x),
        )
        .sign_and_submit(tx_submitter_kp)
        )
        print("Transaction success, result:", result)
        return True
    except exceptions.AssembledTransactionError as e:
        print("Transaction failed, check the exception for more details.", e)
        return None

# main code
# contract_id = deploy_contract()

# invoke_initialize_health_data(contract_id)

# get_price(contract_id)

# transfer(contract_id)


# ---------------------------------------- S3 Config -----------------------------------------------------------
import boto3
import uuid , json
from django.conf import settings

def store_s3(data_points):
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    file_id = uuid.uuid4().hex
    file_name = f"data_points/{file_id}.json"
    file_content = json.dumps(data_points, indent=4)

    try:
        # Upload to S3
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_content, ContentType='application/json')
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
        return s3_url
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None


def get_s3_data(s3_url):
    s3_client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,region_name="us-east-1")
    file_key = s3_url.split('s3.amazonaws.com/')[-1]
    try:
        # Download from S3
        response = s3_client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)
        data = json.loads(response['Body'].read().decode('utf-8'))
        return data
    except Exception as e:
        print(f"Error downloading from S3: {e}")
        return None

