import sys
sys.path.append(".")

from blockchain.blockchain import Blockchain
from wallet.wallet import Wallet
from wallet.transaction_pool import TransactionPool
from p2p.p2pserver import P2pServer
from screens.background import Background
import threading
import os
import io
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

    
def main():
    agent_session = AgentSession()
    initialise_agent(agent_session)
    
    # Content to be uploaded
    file_content = """Liverpool are reportedly one of several European clubs interested in Juventus defender Dean Huijsen. The 19-year-old spent last season on loan at Roma and could be set to leave for a permanent exit this summer as the Serie A giants look to raise funds.That's according to Tuttosport, who report that the Reds - along with Bayern Munich, RB Leipzig, Newcastle United and Paris Saint-Germain - have asked for further information on the defender. It is claimed that Huijsen could depart Juventus as they look to raise funds for the acquisition of Teeun Koopmeiners from Atalanta.The report from Tuttosport adds that none of the reported parties have discussed a possible deal with Juventus or made a formal offer, with the Serie A side holding out for roughly £25m. Liverpool are expected to be in the market for a central defender this summer as one of several clubs who explored a deal for Leny Yoro before he signed for Manchester United for an initial £52m earlier this week.Meanwhile, one defender who could leave the club this summer is Sepp van den Berg, who has spent the last three seasons on loan at Preston North End, Schalke 04 and Mainz 05. Earlier this summer, Van den Berg hit out at Liverpool and the transfer fee they were seeking for his services, with Mainz 05, Brentford and Southampton all interested in the Dutchman."You (Liverpool) didn't exude confidence in me all this time, but you do want to hinder my future," Van den Berg told De Telegraaf. "I want to keep playing every week and develop myself further. In Germany, I enjoy Dortmund away with 70,000 people, Bayern Munich away against Harry Kane, Stuttgart, Leipzig, Leverkusen, against clubs like that I am challenged every week." """
    
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
            pass
    except KeyboardInterrupt:
        print("Shutting down agent...")
        if hasattr(agent_session, "p2pserver"):
            agent_session.p2pserver.stop()
        if hasattr(agent_session, "background"):
            agent_session.background.stop()
        print("Agent shut down successfully")

if __name__ == "__main__":
    main()