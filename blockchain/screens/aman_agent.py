import sys
sys.path.append(".")
import time
from blockchain.blockchain import Blockchain
from wallet.wallet import Wallet
from wallet.transaction_pool import TransactionPool
from p2p.p2pserver import P2pServer
from background import Background
import threading
import os
import io
import pandas as pd
from datetime import datetime
from extra import crypto_logic
from wallet.transaction import Transaction
from ipfs.ipfs_handler import IPFSHandler
class AgentSession:
    def __init__(self):
        self.initialise = False
        self.validator = False
        self.user_type = "Reader"
        self.name = "AutomatedAgent"
        self.email = "agent@example.com"
def get_agent_private_key(key_file="agent_private_key.pem"):
    if os.path.exists(key_file):
        with open(key_file, "r") as file:
            private_key = file.read()
    else:
        # Generate a new private key
        key = crypto_logic.gen_sk()
        private_key = key.export_key().decode()
        # Save the private key
        with open(key_file, "w") as file:
            file.write(private_key)
    return private_key
def run_p2pserver(p2pserver):
    print("Running p2p server")
    p2pserver.start_server()
def run_background_task(background):
    print("Running background block proposer updation")
    background.run_forever()
def initialise_agent(agent_session):
    if not agent_session.initialise:
        private_key = get_agent_private_key()
        # Verify the private key
        verification_result = crypto_logic.verify(private_key)
        if not verification_result[0]:
            raise ValueError(f"Invalid private key: {verification_result[1]}")
        agent_session.blockchain = Blockchain()
        agent_session.transaction_pool = TransactionPool()
        agent_session.wallet = Wallet(
            private_key=verification_result[2],  # Use the RSA key object
            name=agent_session.name,
            email=agent_session.email
        )
        p2pserver = P2pServer(
            blockchain=agent_session.blockchain,
            transaction_pool=agent_session.transaction_pool,
            wallet=agent_session.wallet,
            user_type=agent_session.user_type
        )
        background_task = Background(p2pserver=p2pserver)
        agent_session.p2pserver = p2pserver
        agent_session.background = background_task
        p2p_thread = threading.Thread(
            target=run_p2pserver, args=(agent_session.p2pserver,), daemon=True
        )
        background_thread = threading.Thread(
            target=run_background_task, args=(agent_session.background,), daemon=True
        )
        p2p_thread.start()
        background_thread.start()
        agent_session.initialise = True
        print("AGENT INITIALIZED")
    else:
        print("Agent already initialized")
def upload_file(agent_session, file_content, transaction_fee=0):
    balance = agent_session.blockchain.get_balance(
        agent_session.wallet.get_public_key()
    )
    print(f"Current balance: {balance}")
    if balance >= transaction_fee:
        try:
            # Upload content to IPFS
            ipfs_hash = IPFSHandler.put_to_ipfs(io.BytesIO(file_content.encode()))
            if not ipfs_hash:
                raise Exception("Failed to upload content to IPFS")
            print(f"Content uploaded to IPFS with hash: {ipfs_hash}")
            # Generate transaction
            transaction = Transaction.generate_from_file(
                sender_wallet=agent_session.wallet,
                file=io.BytesIO(file_content.encode()),
                blockchain=agent_session.blockchain,
                fee=transaction_fee,
                )
            # Broadcast transaction
            agent_session.p2pserver.broadcast_transaction(transaction)
            print("BROADCASTED TRANSACTION")
            print("File successfully uploaded and transaction broadcasted.")
            # Verify the upload by fetching the content
            retrieved_content = IPFSHandler.get_from_ipfs(ipfs_hash)
            print(f"Retrieved content from IPFS: {retrieved_content}")
            return True
        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            return False
    else:
        print("Insufficient balance for transaction fee.")
        return False
    
def show_blocks_news(agent_session):
    chain = agent_session.p2pserver.blockchain.chain
    if len(chain) < 2:
        print("The current ledger holds no news. Please return later")
        return
    table_data = []
    for block in chain:
        for transaction in block.transactions:
            percent_fake_votes = 100 * (len(transaction.negative_votes) / (len(transaction.negative_votes) + len(transaction.positive_votes)))
            table_data.append({
                "Percent of Fake Votes": f"{percent_fake_votes:.2f}%",
                "Content URL": f"https://ipfs.io/ipfs/{transaction.ipfs_address}",
                "ID": transaction.id,
            })
    df = pd.DataFrame(table_data)
    print(df.to_string(index=False))

def main():
    agent_session = AgentSession()
    initialise_agent(agent_session)
    # Content to be uploaded
    file_content = "This is the actual content that needs to be uploaded to IPFS and included in the transaction."
    # Set transaction fee (you can adjust this as needed)
    transaction_fee = 0
    # Upload file
    success = upload_file(agent_session, file_content, transaction_fee)
    if success:
        print("Content upload, IPFS storage, and transaction broadcast completed successfully.")
    else:
        print("Content upload failed.")
    # Keep the main thread running
    try:
        while True:
            show_blocks_news(agent_session)
            time.sleep(60)  # Adjust the sleep time as needed
    except KeyboardInterrupt:
        print("Shutting down agent...")
        if hasattr(agent_session, "p2pserver"):
            agent_session.p2pserver.stop()
        if hasattr(agent_session, "background"):
            agent_session.background.stop()
        print("Agent shut down successfully")
if __name__ == "__main__":
    main()