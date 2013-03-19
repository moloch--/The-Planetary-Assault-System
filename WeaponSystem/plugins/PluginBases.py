from yapsy.IPlugin import IPlugin

class MD5Plugin(IPlugin):

    def crack_md5(self):
        pass

    @property
    def is_precomputation(self):
        pass


class SHA1Plugin(IPlugin):

    def crack_sha1(self):
        pass

    @property
    def is_precomputation(self):
        pass


class SHA256Plugin(IPlugin):

    def crack_sha1(self):
        pass

    @property
    def is_precomputation(self):
        pass


class SHA512Plugin(IPlugin):

    def crack_sha1(self):
        pass

    @property
    def is_precomputation(self):
        pass


class LMPlugin(IPlugin):

    def crack_lm(self):
        pass

    @property
    def is_precomputation(self):
        pass


class NTLMPlugin(IPlugin):

    def crack_ntlm(self):
        pass

    @property
    def is_precomputation(self):
        pass


class PBKDF2Plugin(IPlugin):

    def crack_sha1(self):
        pass

    @property
    def is_precomputation(self):
        pass