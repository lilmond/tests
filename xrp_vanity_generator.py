from xrpl.wallet import Wallet
from xrpl.constants import CryptoAlgorithm
import threading
import time

THREADS = 30
vanities = ["poly", "morphic", "polymorphic"]
generated_wallets = 0
found_wallets = 0

def generate_wallet():
    global generated_wallets
    global found_wallets

    while True:
        wallet = Wallet.create(algorithm=CryptoAlgorithm.SECP256K1)

        generated_wallets += 1
        if (generated_wallets % 1000 == 0):
            print(f"Generated Wallets: {generated_wallets} | Threads: {threading.active_count()} Found Wallets: {found_wallets}")

        for vanity in vanities:
            if (vanity in wallet.address.lower()):
                log_text = f"{vanity} | {wallet.address} | {wallet.seed}"
                print(log_text)
                with open("vanities.txt", "a") as file:
                    file.write(f"{log_text}\n")
                    file.close()
                found_wallets += 1

def handler():
    while True:
        generator_threads = threading.active_count() - 2
        if generator_threads >= THREADS:
            time.sleep(0.1)
            continue
        threading.Thread(target=generate_wallet, daemon=True).start()
        
def main():
    try:
        threading.Thread(target=handler, daemon=True).start()
        input()
    except KeyboardInterrupt:
        return
    
if __name__ == "__main__":
    main()
