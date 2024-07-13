from .wr740n_ import Tplink_WR740N_


class Tplink_C7v2(Tplink_WR740N_):

    def confirm_identity(self):
        self._ensure_www_auth_header('Basic realm="TP-LINK Wireless Dual Band Gigabit Router Archer C7"')
