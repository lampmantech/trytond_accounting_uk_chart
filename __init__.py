# -*- encoding: utf-8 -*-
from trytond.pool import Pool
from .account import *


def register():
    Pool.register(
        PrintAbbrevAcctsStart,
        module='account', type_='model')
    Pool.register(
        PrintAbbrevAccts,
        module='account', type_='wizard')
    Pool.register(
        AbbrevAccts,
        module='account', type_='report')
