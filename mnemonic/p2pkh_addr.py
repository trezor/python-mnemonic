import binascii
import hashlib
import base58


# addapted from
# https://bitcoin.stackexchange.com/questions/19081/parsing-bitcoin-input-and-output-addresses-from-scripts
def p2pkh_to_address(pkscript, istestnet=False):
    pub = pkscript[6:-4]  # get pkhash, inbetween first 3 bytes and last 2 bytes
    p = '00' + pub  # prefix with 00 if it's mainnet
    if istestnet:
        p = '6F' + pub  # prefix with 0F if it's testnet
    h1 = hashlib.sha256(binascii.unhexlify(p))
    h2 = hashlib.new('sha256', h1.digest())
    h3 = h2.hexdigest()
    a = h3[0:8]  # first 4 bytes
    c = p + a  # add first 4 bytes to beginning of pkhash
    d = int(c, 16)  # string to decimal
    b = d.to_bytes((d.bit_length() + 7) // 8, 'big')  # decimal to bytes
    address = base58.b58encode(b)  # bytes to base58
    if not istestnet:
        address = '1' + str(address)  # prefix with 1 if it's mainnet
    return address


if __name__ == "__main__":
    print(p2pkh_to_address(
        "023cba1f4d12d1ce0bced725373769b2262c6daa97be6a0588cfec8ce1a5f0bd09"))
    print(p2pkh_to_address(
        "76a91412ab8dc588ca9d5787dde7eb29569da63c3a238c88ac"))  # 12higDjoCCNXSA95xZMWUdPvXNmkAduhWv
    print(p2pkh_to_address(
        "76a914877fefc337afdc98afe4a4ab1c4e85221292783988ac", True))  # mssQn95JGBtw6Npbt6Z8LoJfK1Buuz6ZHt
    print(p2pkh_to_address(
        "76a914877fefc337afdc98afe4a4ab1c4e85221292783988ac"))  # 1DMTV5zKTATgKGLzAXakWt6LT1bCxsQmGD
    print(p2pkh_to_address(
        "76a91407041f753155ac49978c6d2ad094eede19bb39a088ac", True))  # mgA3xrpGWX96BeGRfDfpcp8SHwWn5pg9uM
    print(p2pkh_to_address(
        "76a914877fefc337afdc98afe4a4ab1c4e85221292783988ac"))  # 1DMTV5zKTATgKGLzAXakWt6LT1bCxsQmGD
