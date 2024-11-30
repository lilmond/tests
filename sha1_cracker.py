import itertools
import hashlib
import string

data = "6111f4500df391c730476350e79f9ecf5b0e84c3"

length = 1
checks = 0

while True:
    chars = list(string.printable.strip())
    combinations = itertools.product(chars, repeat=length)

    for combo in combinations:
        combo = ''.join(combo)

        hashed_combo = hashlib.sha1(combo.encode()).hexdigest()

        checks += 1
        
        if hashed_combo == data:
            print(f"SHA-512 cracked!\nPlain Text: {combo}\nHash: {hashed_combo}")
            exit()
        else:
            print(f"{checks}: {combo}: {hashed_combo}")
    
    length += 1
