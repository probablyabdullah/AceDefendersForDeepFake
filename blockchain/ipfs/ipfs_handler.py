import requests
import os
from dotenv import load_dotenv

load_dotenv()
jwt_token=os.getenv('PINATA_JWT_TOKEN')

class IPFSHandler:

    base_url = "https://api.pinata.cloud/pinning"
    auth = {'Authorization':f'Bearer {jwt_token}'}

    # putting data to IPFS and returns a ipfs address
    @staticmethod
    def put_to_ipfs(content):
        url = f"{IPFSHandler.base_url}/pinFileToIPFS"
        files = {"file": content}

        try:
            res = requests.post(url, files=files, headers=IPFSHandler.auth)
            return res.json()['IpfsHash']
        except Exception as e:
            print(e)
            return ""

        # try:
        #     print(res.json())
        #     ipfs_address = res.json()["cid"]
        # except Exception as e:
        #     print("Error: ", e)
        #     return ""

        # '''{'cid': 'bafkreidb6otjwgl5xuwbzzixoc7oz5maojjpj7sfuzrobyawiafwxeo524',
        #     'carCid': 'bagbaieragbvch2fxvhiir3bxiidxa7fxrr5cgobtyqq6o6dy3nnjezbijera'}'''
        # return "bafkreidb6otjwgl5xuwbzzixoc7oz5maojjpj7sfuzrobyawiafwxeo524"


    # fetching from IPFS and returns data
    @staticmethod
    def get_from_ipfs(ipfs_address):
        try:
            res = requests.get(
                f"https://ipfs.io/ipfs/{ipfs_address}", headers=IPFSHandler.auth)
            return res.text
        except Exception as e:
            print(e)
            return ""

        # # RETURN DEMO TEXT
        # with open("nan.txt", "r") as file:
        #     file_content = file.read()
        #     return file_content

        # return """nan
# Did they post their votes for Hillary already?"""


if __name__ == "__main__":
    ipfs_address = 'QmbKdU91G6zto3i99T81uqba6W2XWAnxAJb4pu1HokvGaa'
    print(ipfs_address)
    print(IPFSHandler.get_from_ipfs(ipfs_address))
