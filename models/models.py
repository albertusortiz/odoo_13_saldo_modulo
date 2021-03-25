# -*- coding: utf-8 -*-

from odoo import models, fields

class Movimiento(models.Model):
  _name = "sa.movimiento" # sa_movimiento
  _description = "Movimiento"
  _inherit = "mail.thread"

  name = fields.Char(string="Nombre", required=True)
  type_move = fields.Selection(selection=[("ingreso","Ingreso"),("gasto","Gasto")], string="Tipo", default="ingreso", required=True)
  date = fields.Datetime(string="Fecha")
  amount = fields.Float(string="Monto")
  receipt_image = fields.Binary(string="Foto del Recibo")
  notas = fields.Html(string="Notas")

  currency_id = fields.Many2one("res.currency", default=33) # Traemos el ID del modelo res.currency para tener acceso a la tabla de monedas que existe en Odoo

  user_id = fields.Many2one("res.users", string="Usuario") # Campo relacionado con el modelo res.users
  category_id = fields.Many2one("sa.category", string="Categoria") # Campo relacionado con el modelo sa.category

  tag_ids = fields.Many2many("sa.tag","sa_mov_sa_tag_rel","movimiento_id","tag_id") #sa_movimientos


class Category(models.Model):
  _name = "sa.category" # sa_category
  _description = "Categoria"

  name = fields.Char(string="Nombre")


class Tag(models.Model):
  _name = "sa.tag" # sa_tag
  _description = "Tag"

  name = fields.Char(string="Nombre")


class ResUsers(models.Model):
  _inherit = "res.users"
  movimiento_ids = fields.One2many("sa.movimiento","user_id")