from generator import Generator
from mnemonic import Mnemonic
import segwit_addr
import hashlib
import base58
import binascii


class MnAddress:

    def accepted_addresses(self):
        """
            This method returns which addresses are accepted
            p2pkh: pay to public key hash
            p2sh: pay to script hash
            p2wpkh: pay to witness public key hash
            p2wsh: pay to witness script hash
            p2tr: pay to taproot

        Returns
        -------
        tuple
            Returned current accepted addresses
        """
        accepted_addresses_formats = ("p2pkh", "p2sh", "p2wpkh", "p2wsh", "p2tr")
        return accepted_addresses_formats

    def decode_address(self, address: str, theme: str):
        """
            This method identifies which address is given to be turned into phrases in Formosa standard

        Parameters
        ----------
        address : str
            The string containing the bitcoin address in the accepted forms
        theme : str
            The theme desired to be used in Formosa standard

        Returns
        -------
        list
            Returned list of words which can be concatenated into phrases in the Formosa standard
        """
        theme = "finances" if theme is None else theme
        address = address.replace(" ", "").replace("\n", "")
        if (address[0:2] == "bc" or address[0:2] == "tb") and (14 <= len(address) <= 74):
            if address[3] == "q" and len(address) < 62:
                addr_type = "p2wpkh"
            elif address[3] == "q" and len(address) == 62:
                addr_type = "p2wsh"
            elif address[3] == "p" and len(address) > 42:
                addr_type = "p2tr"
            else:
                raise ValueError("Not a compatible address format")
            header = ["btc", addr_type, theme]
            ret = self.decode_bech32(address.lower(), theme)
        elif address[0] == "1" or address[0] == "3":
            addr_type = "p2pkh" if address[0] == "1" else "p2sh"
            header = ["btc", addr_type, theme]
            ret = self.decode_base58(address, theme)
        else:
            return None
        ret = header + ret
        return ret

    def encode_address(self, mnemonic):
        """
            This method receives a mnemonic in Formosa standard as str or list
            to encode to one of accepted bitcoin addresses

        Parameters
        ----------
        mnemonic :
            The mnemonic is the list or string of words that forms phrases in Formosa standard

        Returns
        -------
        str
            Returns the bitcoin address with the given format given by the mnemonic header
        """
        mn_list = []
        # if type(mnemonic) is str:
        if isinstance(mnemonic, str):
            mn_list = [each_word for each_word in [
                each_line.split(" ") for each_line in mnemonic.split("\n")] if each_word != [""]]
        # elif type(mnemonic) is list:
        elif isinstance(mnemonic, list) or isinstance(mnemonic, tuple):
            mn_list = [mnemonic[0:3]]
            if len(mnemonic[3]) >= 18:
                for i in range(len(mnemonic[4:]) // 6):
                    mn_list.append(mnemonic[6 * i + 4:6 * (i + 1) + 4])
            else:
                for word_index in range(len(mnemonic[3:]) // 6):
                    mn_list.append(mnemonic[6 * word_index + 3:6 * (word_index + 1) + 3])
        else:
            error_message = "A valid mnemonic format is needed, the mnemonic type given is %s" % type(mnemonic)
            raise ValueError(error_message)
        if mn_list[0][0] != "btc" or len(mn_list) < 2 or (
                sum([len(phrases.split(" ")) for phrases in mn_list[len(mn_list) - 1]]) % 6 != 0):
            return None
        encoding = mn_list[0][1]
        theme = mn_list[0][2]
        phrase_start_index = 1 if len(mn_list[1]) > 1 else 2
        phrases = " ".join([" ".join(each_word
                                     for each_word in phrase_list)
                            for phrase_list in mn_list[phrase_start_index:]]
                           )
        p2pkh = ("p2pkh", "legacy")
        p2sh = ("p2sh", "compatibility", "compatible")
        p2wpkh = ("p2wpkh", "segwit")
        p2wsh = ("p2wsh")
        p2tr = ("p2tr", "taproot", "tr")
        address_entropy = self.mnemonic_to_integer(phrases, theme)

        if encoding in p2pkh:
            ret = self.encode_p2pkh(address_entropy)
        elif encoding in p2sh:
            ret = self.encode_p2sh(address_entropy)
        elif encoding in p2wpkh:
            ret = self.encode_p2wpkh(address_entropy)
        elif encoding in p2wsh:
            ret = self.encode_p2wsh(address_entropy)
        elif encoding in p2tr:
            ret = self.encode_p2tr(address_entropy)
        else:
            error_message = "A valid encoding type to address is needed, the encoding type given is %s" % encoding
            raise ValueError(error_message)
        return ret

    def mnemonic_to_integer(self, address: str, theme: str):
        """
            This method calls the object Mnemonic which returns the entropy number
            from a given bitcoin address

        Parameters
        ----------
        address : str
            The address is the bitcoin address to extract the entropy value
        theme : str
            The theme is the theme used to create the Mnemonic object

        Returns
        -------
        bytearray
            Returns the entropy of a bitcoin address
        """
        m = Mnemonic(theme)
        return m.to_entropy(address)

    def encode_p2pkh(self, address_entropy: bytearray):
        """
            This method encodes an entropy value to a p2pkh bitcoin address format

        Parameters
        ----------
        address_entropy : bytearray
            The value of entropy to be inserted in a bitcoin address

        Returns
        -------
        str
            The bitcoin address in p2pkh standard
        """
        entropy_address = address_entropy[:-4]
        address_hex = "".join([hex(each_value)[2:].zfill(2) for each_value in entropy_address])
        addr_v = "00"
        address_version = bytearray(binascii.unhexlify(addr_v))
        sha_256_address = hashlib.sha256(address_version + entropy_address).digest()
        sha_256_address = hashlib.new("sha256", sha_256_address).hexdigest()
        addr_p_sha = addr_v + address_hex + sha_256_address[:8]
        encoded_address = base58.b58encode(binascii.unhexlify(addr_p_sha)).decode()
        return encoded_address

    def encode_p2sh(self, address_entropy: bytearray):
        """
            This method encodes an entropy value to a p2sh bitcoin address format

        Parameters
        ----------
        address_entropy : bytearray
            The value of entropy to be inserted in a bitcoin address

        Returns
        -------
        str
            The bitcoin address in p2sh standard
        """
        entropy_address = address_entropy[:-4]
        address_hex = "".join([hex(each_value)[2:].zfill(2) for each_value in entropy_address])
        addr_v = "05"
        address_version = bytearray(binascii.unhexlify(addr_v))
        sha_256_address = hashlib.sha256(address_version + entropy_address).digest()
        sha_256_address = hashlib.new("sha256", sha_256_address).hexdigest()
        addr_p_sha = addr_v + address_hex + sha_256_address[:8]
        encoded_address = base58.b58encode(binascii.unhexlify(addr_p_sha)).decode()
        return encoded_address

    def encode_p2wpkh(self, address_entropy: bytearray):
        """
            This method encodes an entropy value to a p2wpkh bitcoin address format

        Parameters
        ----------
        address_entropy : bytearray
            The value of entropy to be inserted in a bitcoin address

        Returns
        -------
        str
            The bitcoin address in p2wpkh standard
        """
        hrp = "bc"
        data = [address_entropy[value_index] for value_index in range(len(address_entropy) - 4)]
        address_entropy = segwit_addr.encode(hrp, 0, data)
        return address_entropy

    def encode_p2wsh(self, address_entropy: bytearray):
        """
            This method encodes an entropy value to a p2wsh bitcoin address format

        Parameters
        ----------
        address_entropy : bytearray
            The value of entropy to be inserted in a bitcoin address

        Returns
        -------
        str
            The bitcoin address in p2wsh standard
        """
        hrp = "bc"
        data = [address_entropy[value_index] for value_index in range(len(address_entropy) - 4)]
        address_entropy = segwit_addr.encode(hrp, 0, data)
        return address_entropy

    def encode_p2tr(self, address_entropy: bytearray):
        """
            This method encodes an entropy value to a p2tr bitcoin address format

        Parameters
        ----------
        address_entropy : bytearray
            The value of entropy to be inserted in a bitcoin address

        Returns
        -------
        str
            The bitcoin address in p2tr standard
        """
        hrp = "bc"
        data = [address_entropy[value_index] for value_index in range(len(address_entropy) - 4)]
        address_entropy = segwit_addr.encode(hrp, 1, data)
        return address_entropy

    def decode_base58(self, address: str, theme: str):
        """
            This method decodes the bitcoin address in base58 to entropy and checksum values
            Then calls the Generator object to generate phrases in Formosa standard

        Parameters
        ----------
        address : str
            The bitcoin address to be translated to Formosa standard
        theme : str
            The theme used in Formosa standard

        Returns
        -------
        list
            The list of words which can be concatenated to form a phrase in Formosa standard
        """
        base_address = base58.b58decode(address)[1:-4]
        sha_256_address = hashlib.sha256(base_address).digest()
        ret = base_address + sha_256_address[:4]
        return self.call_generator(ret, theme)

    def decode_bech32(self, address: str, theme: str):
        """
            This method decodes the bitcoin address in bech32 to entropy and checksum values
            Then calls the Generator object to generate phrases in Formosa standard

        Parameters
        ----------
        address : str
            The bitcoin address to be translated to Formosa standard
        theme : str
            The theme used in Formosa standard

        Returns
        -------
        list
            The list of words which can be concatenated to form a phrase in Formosa standard
        """
        entropy_address = bytearray(segwit_addr.decode(address[:2], address)[1])
        sha256_address = hashlib.sha256(entropy_address).digest()
        ret = entropy_address + sha256_address[:4]
        return self.call_generator(ret, theme)

    def call_generator(self, address_entropy: str, theme: str):
        """
            This method calls the Generator object to generate a list of words
            which can be concatenated in Formosa standard

        Parameters
        ----------
        address_entropy : str
            Bitcoin address value to be translated to Formosa standard
        theme : str
            The theme used in Formosa standard

        Returns
        -------
        list
            The list of words which can be concatenated to form a phrase in Formosa standard

        """
        g = Generator(None, theme, address_entropy)
        phrases = g.show_phrases()
        return phrases
