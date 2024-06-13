
from itertools import combinations, product
from mnemonic import Mnemonic
from embit import bip32
from embit.networks import NETWORKS
from embit.script import p2wpkh
from tqdm import tqdm

# Your mnemonic phrase
mnemonic_words = ['cage', 'chef', 'fog', 'hope', 'join', 'miss', 'nose', 'page', 'pass', 'pipe', 'quit', 'use']

mnemo = Mnemonic("english")

# iterate through all permutations of the mnemonic words
for perm in tqdm(product(mnemonic_words, repeat=len(mnemonic_words))):
    # check if the mnemonic is valid
    perm = " ".join(perm)
    if not mnemo.check(perm):
        continue
    seed = mnemo.to_seed(perm)
    root = bip32.HDKey.from_seed(seed, version=NETWORKS["main"]["xprv"])
    path = "m/84'/0'/0'/0/0"
    child_key = root.derive(path)
    # Generate the Bech32 address
    pubkey = child_key.to_public().key
    address = p2wpkh(pubkey).address(NETWORKS["main"])
    print(f"BIP84 Address: {address}")
    # exit(0)


# # check if the mnemonic is valid
# if not mnemo.check(mnemonic_words):
#     print("Invalid mnemonic")
#     exit(1)

# # Generate seed from mnemonic
# seed = mnemo.to_seed(mnemonic_words)

# # Derive Master Private Key from seed
# root = bip32.HDKey.from_seed(seed, version=NETWORKS["main"]["xprv"])

# # BIP84 derivation path for the first address
# # m / purpose' / coin_type' / account' / change / address_index
# # For Bitcoin mainnet: m/84'/0'/0'/0/0
# path = "m/84'/0'/0'/0/0"
# child_key = root.derive(path)

# # Generate the Bech32 address
# pubkey = child_key.to_public().key
# address = p2wpkh(pubkey).address(NETWORKS["main"])

# print(f"BIP84 Address: {address}")
