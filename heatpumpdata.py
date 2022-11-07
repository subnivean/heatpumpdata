from datetime import datetime
import paramiko

class HeatPumpData():
    def __init__(self, which, ip, user="pi", key="./id_rsa_rpi", channel=4):
        """Connect to a Raspberry Pi that is reading
        heat pump current settings via a CT HAT to
        get useful data about the heat pump state.
        """
        self.key = key
        self.user = user
        self.ip = ip
        self.channel = channel
        self.which = which

        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file(self.key)

        dbpath = "/home/pi/ctreader-docker/data/heatpumpctdata.db"
        sql = f"SELECT * FROM {which}ctdata ORDER BY DateTime DESC LIMIT 1;"
        self._lastdatacmd = (f"sqlite3 -separator ' ' {dbpath} '{sql}'")

        self.client.connect(self.ip, username=self.user, pkey=pkey)

        # Fill in data properties
        self.get_latest_data()

        self.client.close()

    def get_latest_data(self):
        stdin, stdout, stderr = self.client.exec_command(self._lastdatacmd)
        self.record = stdout.read().decode()
        self.datetimestr = self.record.split()[0]
        self.datetime = datetime.fromisoformat(self.datetimestr.split('.')[0])
        self.watts = float(self.record.split()[self.channel])

    def __str__(self):
        return (f"IP: {self.ip}, Which: {self.which}, "
                f"Date: {self.datetimestr.split('.')[0]}, "
                f"Watts: {self.watts}, "
                f"Timedelta: {self.timedelta}")

    @property
    def is_on(self):
        pass

    @property
    def timedelta(self):
        return (datetime.now() - self.datetime).seconds

    @property
    def is_defrosting(self):
        pass

if __name__ == "__main__":
    which = 'house'
    ip = "192.168.1.9"
    key = "../id_rsa_rpi"
    hp = HeatPumpData(which, ip, key=key)
    #print(f"{hp.timedelta=}, {hp.watts=}")
    print(hp)
