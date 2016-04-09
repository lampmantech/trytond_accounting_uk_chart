# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""
This a starting point for a Companies House filing of the
summary of Abbreviated Accounts. Look in  abbrev_accts.odt for the template. 

Right now it's just a cut-n-paste of the Trial Balance from Tryton's
3.6.3 account module, but it serves as a point to wire up an abbreviated
accounts report.

"""
from decimal import Decimal
import datetime
import operator
from itertools import izip, groupby

from trytond.model import ModelView, ModelSQL, fields
from trytond.wizard import Wizard, StateView, StateAction, StateTransition, \
    Button
from trytond.report import Report
from trytond.pyson import Eval, PYSONEncoder, Date
from trytond.transaction import Transaction
from trytond.pool import Pool

__all__ = ['PrintAbbrevAcctsStart', 'PrintAbbrevAccts', 'AbbrevAccts',]

class PrintAbbrevAcctsStart(ModelView):
    'Print Abbrev Accts'
    __name__ = 'accounting_uk_chart.print_abbrev_accts.start'
    fiscalyear = fields.Many2One('account.fiscalyear', 'Fiscal Year',
        required=True)
    start_period = fields.Many2One('account.period', 'Start Period',
        domain=[
            ('fiscalyear', '=', Eval('fiscalyear')),
            ('start_date', '<=', (Eval('end_period'), 'start_date'))
            ],
        depends=['end_period', 'fiscalyear'])
    end_period = fields.Many2One('account.period', 'End Period',
        domain=[
            ('fiscalyear', '=', Eval('fiscalyear')),
            ('start_date', '>=', (Eval('start_period'), 'start_date'))
            ],
        depends=['start_period', 'fiscalyear'])
    company = fields.Many2One('company.company', 'Company', required=True)
    posted = fields.Boolean('Posted Move', help='Show only posted move')
    empty_account = fields.Boolean('Empty Account',
            help='With account without move')

    @staticmethod
    def default_fiscalyear():
        FiscalYear = Pool().get('account.fiscalyear')
        return FiscalYear.find(
            Transaction().context.get('company'), exception=False)

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @staticmethod
    def default_posted():
        return False

    @staticmethod
    def default_empty_account():
        return False

    @fields.depends('fiscalyear')
    def on_change_fiscalyear(self):
        self.start_period = None
        self.end_period = None


class PrintAbbrevAccts(Wizard):
    'Print Abbrev Accts'
    __name__ = 'accounting_uk_chart.print_abbrev_accts'
    start = StateView('accounting_uk_chart.print_abbrev_accts.start',
        'accounting_uk_chart.print_abbrev_accts_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Print', 'print_', 'tryton-print', default=True),
            ])
    print_ = StateAction('accounting_uk_chart.report_abbrev_accts')

    def do_print_(self, action):
        if self.start.start_period:
            start_period = self.start.start_period.id
        else:
            start_period = None
        if self.start.end_period:
            end_period = self.start.end_period.id
        else:
            end_period = None
        data = {
            'company': self.start.company.id,
            'fiscalyear': self.start.fiscalyear.id,
            'start_period': start_period,
            'end_period': end_period,
            'posted': self.start.posted,
            'empty_account': self.start.empty_account,
            }
        return action, data

    def transition_print_(self):
        return 'end'


class AbbrevAccts(Report):
    __name__ = 'accounting_uk_chart.abbrev_accts'

    @classmethod
    def get_context(cls, records, data):
        report_context = super(AbbrevAccts, cls).get_context(records, data)

        pool = Pool()
        Account = pool.get('account.account')
        Period = pool.get('account.period')
        Company = pool.get('company.company')

        company = Company(data['company'])

        accounts = Account.search([
                ('company', '=', data['company']),
                ('kind', '!=', 'view'),
                ])

        start_periods = []
        if data['start_period']:
            start_period = Period(data['start_period'])
            start_periods = Period.search([
                    ('fiscalyear', '=', data['fiscalyear']),
                    ('end_date', '<=', start_period.start_date),
                    ])

        if data['end_period']:
            end_period = Period(data['end_period'])
            end_periods = Period.search([
                    ('fiscalyear', '=', data['fiscalyear']),
                    ('end_date', '<=', end_period.start_date),
                    ])
            end_periods = list(set(end_periods).difference(
                    set(start_periods)))
            if end_period not in end_periods:
                end_periods.append(end_period)
        else:
            end_periods = Period.search([
                    ('fiscalyear', '=', data['fiscalyear']),
                    ])
            end_periods = list(set(end_periods).difference(
                    set(start_periods)))

        start_period_ids = [p.id for p in start_periods] or [0]
        end_period_ids = [p.id for p in end_periods]

        with Transaction().set_context(
                fiscalyear=data['fiscalyear'],
                periods=start_period_ids,
                posted=data['posted']):
            start_accounts = Account.browse(accounts)

        with Transaction().set_context(
                fiscalyear=None,
                periods=end_period_ids,
                posted=data['posted']):
            in_accounts = Account.browse(accounts)

        with Transaction().set_context(
                fiscalyear=data['fiscalyear'],
                periods=start_period_ids + end_period_ids,
                posted=data['posted']):
            end_accounts = Account.browse(accounts)

        to_remove = set()
        if not data['empty_account']:
            for account in in_accounts:
                if account.debit == Decimal('0.0') \
                        and account.credit == Decimal('0.0'):
                    to_remove.add(account)

        accounts = []
        for start_account, in_account, end_account in izip(
                start_accounts, in_accounts, end_accounts):
            if in_account in to_remove:
                continue
            accounts.append({
                    'code': start_account.code,
                    'name': start_account.name,
                    'start_balance': start_account.balance,
                    'debit': in_account.debit,
                    'credit': in_account.credit,
                    'end_balance': end_account.balance,
                    })

        periods = end_periods

        report_context['accounts'] = accounts
        periods.sort(key=operator.attrgetter('start_date'))
        report_context['start_period'] = periods[0]
        periods.sort(key=operator.attrgetter('end_date'))
        report_context['end_period'] = periods[-1]
        report_context['company'] = company
        report_context['digits'] = company.currency.digits
        report_context['sum'] = \
            lambda accounts, field: cls.sum(accounts, field)

        return report_context

    @classmethod
    def sum(cls, accounts, field):
        amount = Decimal('0.0')
        for account in accounts:
            amount += account[field]
        return amount

