from miscreant.aes.siv import SIV

import os
import json
import base64


class Enc:
    """
    Encrypt data and write generated ciphertext to file
    """

    def __init__(self, file_path):

        self.file_path = file_path

    @staticmethod
    def _gen_key():
        """
        Generate key, initialize SIV object, and return relevant data
        """

        k = SIV.generate_key()
        siv = SIV(k)

        ret = {
            "k": k,
            "siv": siv,
            "nonce": os.urandom(16)
        }

        return ret

    def enc_file(self):
        """
        Encrypt file, return dict with ciphertext and key data
        """

        key_data = self._gen_key()

        with open(self.file_path, 'r') as f:
            data = f.read().encode('utf-8')
            ct = key_data["siv"].seal(data, [key_data["nonce"]])

            ret = {
                "k": key_data["k"],
                "nonce": key_data["nonce"],
                "ct": key_data["nonce"] + ct
            }

            return ret

    def enc_and_write(self, output_dir):
        """
        Encrypt a file
        Write ciphertext to one file and associated key data to another
        """

        enc_data = self.enc_file()

        os.makedirs(output_dir, exist_ok=True)

        base = os.path.basename(self.file_path)
        filename = os.path.splitext(base)[0]

        jf = dict()
        jf["k"] = base64.encodebytes(enc_data["k"]).decode()
        jf["nonce"] = base64.encodebytes(enc_data["nonce"]).decode()

        with open("{0}/{1}.json".format(output_dir, filename), 'w', encoding='utf-8') as j:
            j.write(json.dumps(jf, indent=4))

        with open("{0}/{1}".format(output_dir, filename), 'wb') as f:
            f.write(enc_data["ct"])


class Dec:
    """
    Decrypt data and write plaintext to file
    """

    def __init__(self, input_file, dec_conf):

        self.input_file = input_file
        self.dec_conf = dec_conf
        self.k = None
        self.nonce = None

        self.setup_dec_params()

    def setup_dec_params(self):
        """
        Read AES key and nonce from file
        """

        if isinstance(self.dec_conf, str):

            with open(self.dec_conf, 'r') as in_json:
                data = json.load(in_json)

                self.k = base64.decodebytes(data["k"].encode())
                self.nonce = base64.decodebytes(data["k"].encode())

        elif isinstance(self.dec_conf, dict):

            self.k = self.dec_conf["k"]
            self.nonce = self.dec_conf["nonce"]

        return self

    def dec_file(self):
        """
        Decrypt file and return plaintext
        """

        with open(self.input_file, 'rb') as f:
            data = f.read()
            siv = SIV(self.k)
            nonce = data[:16]
            pt = siv.open(data[16:], [nonce])

            return pt.decode()

    def dec_and_write(self, output_path):
        """
        Decrypt data, write plaintext to file
        """

        pt = self.dec_file()

        with open(output_path, 'w') as f:
            f.write(pt)