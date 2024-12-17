from xrpl.wallet import Wallet
from xrpl.constants import CryptoAlgorithm

def main():
    seed = input("Seed: ")

    algorithms = {"1": CryptoAlgorithm.SECP256K1, "2": CryptoAlgorithm.ED25519}
    print("\nAlgorithms:")
    for key in algorithms:
        print(f"{key}: {algorithms[key]}")
    print("")

    while True:
        algorithm = input("Select:").strip()

        if not algorithm in algorithms:
            print("Error: Invalid choice.\n")
            continue

        algorithm = algorithms[algorithm]
        break

    wallet = Wallet.from_seed(seed=seed, algorithm=algorithm)
    
    print(f"Wallet Information:\nAddress: {wallet.address}\nPublic Key: {wallet.public_key}\nPrivate Key: {wallet.private_key}")

if __name__ == "__main__":
    main()
