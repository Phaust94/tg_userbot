from __future__ import annotations

import dataclasses
import datetime
import os.path
import pickle
import typing
import math

import monobank
from iso4217 import Currency

from bot_secrets import USER_TO_ACCOUNT_ID, MONO_API_KEY, ACCOUNT_CACHE_TIME_SECONDS, EARN_PER_WEEK_PLN


__all__ = [
    "MonoHelper",
]

DATA_DIR = os.path.abspath(os.path.join(__file__, '..', 'data'))


@dataclasses.dataclass
class AccountStatus:
    user_info: dict[str, typing.Any]
    requested_at: datetime.datetime

    @property
    def is_stale(self) -> bool:
        return (datetime.datetime.utcnow() - self.requested_at).seconds >= ACCOUNT_CACHE_TIME_SECONDS

    def raise_if_stale(self) -> None:
        if self.is_stale:
            raise StaleError()
        return None

    def convert(self, curr_conv: CurrencyRate) -> None:
        curr_conv_di = curr_conv.conv_di
        for acc in self.user_info['accounts']:
            cb = (acc['balance'] - acc['creditLimit']) / 100
            if acc['currency'] is Currency.uah:
                cb_pln = cb / curr_conv_di[(Currency.pln, Currency.uah)]
            else:
                cb_pln = cb * curr_conv_di[(acc['currency'], Currency.uah)] / curr_conv_di[(Currency.pln, Currency.uah)]
            acc['balance_pln'] = cb_pln
        return None

    @classmethod
    def from_api(cls) -> AccountStatus:
        mono = monobank.Client(MONO_API_KEY)
        nw = datetime.datetime.utcnow()
        user_info = mono.get_client_info()
        for acc in user_info['accounts']:
            acc['currency'] = get_currency(acc['currencyCode'])
        inst = cls(user_info, requested_at=nw)
        inst.to_file()
        return inst

    def to_file(self) -> None:
        fn = os.path.join(DATA_DIR, 'user_info.pcl')
        with open(fn, 'wb') as f:
            pickle.dump(self, f)
        return None

    @classmethod
    def from_api_cached(cls) -> AccountStatus:
        try:
            fn = os.path.join(DATA_DIR, 'user_info.pcl')
            with open(fn, 'rb') as f:
                acc_status: AccountStatus = pickle.load(f)
            acc_status.raise_if_stale()
        except (FileNotFoundError, StaleError):
            acc_status = cls.from_api()
        return acc_status

    def get_balance_pln(self, account_id: str) -> float:
        acc = [
            ta
            for ta in self.user_info['accounts']
            if ta['id'] == account_id
        ][0]
        return acc['balance_pln']


class StaleError(ValueError):
    pass


@dataclasses.dataclass
class CurrencyRate:
    conv_di: dict[tuple[Currency, Currency], float]
    requested_at: datetime.datetime

    def to_file(self) -> None:
        fn = os.path.join(DATA_DIR, 'currency_conv.pcl')
        with open(fn, 'wb') as f:
            pickle.dump(self, f)
        return None

    @classmethod
    def from_api(cls):
        mono = monobank.Client(MONO_API_KEY)
        nw = datetime.datetime.utcnow()
        curr_conv = mono.get_currency()
        curr_conv_di = {}
        for conv in curr_conv:
            try:
                conv['currencyA'] = get_currency(conv['currencyCodeA'])
                conv['currencyB'] = get_currency(conv['currencyCodeB'])
            except ValueError:
                continue
            if conv['currencyB'] is not Currency.uah:
                continue
            curr_conv_di[
                (conv['currencyA'], conv['currencyB'])
            ] = conv['rateCross'] if 'rateCross' in conv else conv['rateSell']
        inst = cls(curr_conv_di, nw)
        inst.to_file()
        return inst

    @staticmethod
    def from_file() -> CurrencyRate:
        fn = os.path.join(DATA_DIR, 'currency_conv.pcl')
        with open(fn, 'rb') as f:
            inst: CurrencyRate = pickle.load(f)
        if inst.requested_at.date() < datetime.date.today():
            raise StaleError()
        return inst

    @classmethod
    def from_api_cached(cls) -> CurrencyRate:
        try:
            inst = cls.from_file()
        except (FileNotFoundError, StaleError):
            inst = cls.from_api()
        return inst


@dataclasses.dataclass
class MonoHelper:
    user_id: int

    def reply(self, ask: float) -> str:
        bal = self.get_balance_pln()
        is_enough = ask <= bal
        if is_enough:
            how_much = math.floor(bal / ask)
        else:
            how_much = math.ceil((ask - bal) / EARN_PER_WEEK_PLN)
        ok_msg = "✔" if is_enough else "❌"
        msg = f"{ok_msg}   {how_much}"
        return msg

    def get_balance_pln(self) -> float:
        acc_id = USER_TO_ACCOUNT_ID[self.user_id]
        info = AccountStatus.from_api_cached()
        curr = CurrencyRate.from_api_cached()
        info.convert(curr)
        balance = info.get_balance_pln(acc_id)
        return balance


def get_currency(id_: int) -> Currency:
    res = [c for c in Currency if c.number == id_]
    if not res:
        raise ValueError(f"Unknown currency: {id_}")
    return res[0]
