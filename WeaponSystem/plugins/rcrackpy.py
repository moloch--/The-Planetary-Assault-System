from plugins.PluginBases import *


class RCrackMD5Plugin(MD5Plugin):

    def activate(self):
        ''' Setup '''
        self.rainbow_tables = self.__tables__()

    def deactivate(self):
        ''' Tear-down '''
        pass

    @property
    def is_precomputation(self):
        ''' Uses computation or precomputaiton to crack hashes '''
        return True

    def crack_md5(self, hashes, threads):
        tables = self.rainbow_tables[algorithm]
        logging.info("Recieved new assignment, now targeting %d hashes with %d thread(s)" % (
            len(hashes), self.threads,
        ))
        ascii_hashes = [hsh.encode('ascii', 'ignore') for hsh in hashes]
        results = RainbowCrack.hash_list(
            ascii_hashes, 
            tables, 
            maxThreads=self.threads, 
            debug=self.debug
        )

    def __tables__(self):
        pass


class RCrackLMPlugin(LMPlugin):

    def activate(self):
        ''' Setup '''
        self.rainbow_tables = self.__tables__()

    def deactivate(self):
        ''' Tear-down '''
        pass

    @property
    def is_precomputation(self):
        ''' Uses computation or precomputaiton to crack hashes '''
        return True

    def crack_lm(self, hashes, threads):
        tables = self.rainbow_tables[algorithm]
        logging.info("Recieved new assignment, now targeting %d hashes with %d thread(s)" % (
            len(hashes), self.threads,
        ))
        ascii_hashes = [hsh.encode('ascii', 'ignore') for hsh in hashes]
        results = RainbowCrack.hash_list(
            ascii_hashes, 
            tables, 
            maxThreads=self.threads, 
            debug=self.debug
        )

    def __tables__(self):
        pass


class RCrackNTLMPlugin(NTLMPlugin):

    def activate(self):
        ''' Setup '''
        self.rainbow_tables = self.__tables__()

    def deactivate(self):
        ''' Tear-down '''
        pass

    @property
    def is_precomputation(self):
        ''' Uses computation or precomputaiton to crack hashes '''
        return True

    def crack_ntlm(self, hashes, threads):
        tables = self.rainbow_tables[algorithm]
        logging.info("Recieved new assignment, now targeting %d hashes with %d thread(s)" % (
            len(hashes), self.threads,
        ))
        ascii_hashes = [hsh.encode('ascii', 'ignore') for hsh in hashes]
        results = RainbowCrack.hash_list(
            ascii_hashes, 
            tables, 
            maxThreads=self.threads, 
            debug=self.debug
        )

    def __tables__(self):
        pass


