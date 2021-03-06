# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class AccountCoda(models.Model):
    _name = 'account.coda'
    _description = 'Object to store CODA Data Files'
    _order = 'coda_creation_date desc'

    name = fields.Char(string='CODA Filename', readonly=True)
    coda_data = fields.Binary(string='CODA File', readonly=True)
    coda_statement_ids = fields.One2many(
        'coda.bank.statement', 'coda_id',
        string='Generated CODA Bank Statements', readonly=True)
    bank_statement_ids = fields.One2many(
        'account.bank.statement', 'coda_id',
        string='Generated Bank Statements', readonly=True)
    note = fields.Text(string='Import Log', readonly=True)
    coda_creation_date = fields.Date(
        string='CODA Creation Date', readonly=True)
    date = fields.Date(
        string='Import Date',
        default=lambda self: fields.Date.context_today(self),
        readonly=True)
    user_id = fields.Many2one(
        'res.users', string='User',
        default=lambda self: self.env.user,
        readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done')],
        string='State',
        default='done',
        required=True, readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)

    _sql_constraints = [
        ('coda_uniq', 'unique (name, coda_creation_date)',
         'This CODA has already been imported !')
    ]

    @api.multi
    def unlink(self):
        for coda in self:
            coda.bank_statement_ids.unlink()
        return super(AccountCoda, self).unlink()

    @api.multi
    def set_to_draft(self):
        return self.write({'state': 'draft'})

    @api.multi
    def process(self):
        self.ensure_one()
        wiz_vals = {
            'coda_data': self.coda_data,
            'coda_fname': self.name,
        }
        wizard = self.env['account.coda.import'].create(wiz_vals)
        module = __name__.split('addons.')[1].split('.')[0]
        wiz_view = self.env.ref(
            '%s.account_coda_import_view_form_process' % module)
        return {
            'name': _('Process CODA File'),
            'res_id': wizard.id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': wizard._name,
            'view_id': wiz_view.id,
            'target': 'new',
            'context': dict(self._context, coda_id=self.id),
            'type': 'ir.actions.act_window',
        }
