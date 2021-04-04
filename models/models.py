# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Movimiento(models.Model):
  _name = "sa.movimiento" # sa_movimiento
  _description = "Movimiento"
  _inherit = "mail.thread"

  name = fields.Char(string="Nombre", required=True)
  type_move = fields.Selection(selection=[("ingreso","Ingreso"),("gasto","Gasto")], string="Tipo", default="ingreso", track_visibility="onchange", required=True)
  date = fields.Datetime(string="Fecha", track_visibility="onchange")
  amount = fields.Float(string="Monto", track_visibility="onchange")
  receipt_image = fields.Binary(string="Foto del Recibo")
  notas = fields.Html(string="Notas")

  currency_id = fields.Many2one("res.currency", default=33) # Traemos el ID del modelo res.currency para tener acceso a la tabla de monedas que existe en Odoo

  user_id = fields.Many2one("res.users", string="Usuario", default=lambda self:self.env.user.id) # Campo relacionado con el modelo res.users
  category_id = fields.Many2one("sa.category", string="Categoria") # Campo relacionado con el modelo sa.category

  tag_ids = fields.Many2many("sa.tag","sa_mov_sa_tag_rel","movimiento_id","tag_id") #sa_movimientos

  email = fields.Char(related="user_id.email", string="Correo Electrónico") # Jalamos el campo email desde el modelo res.users con el campo user_id

  @api.constrains("amount")
  def _check_amount(self):
    if not(self.amount>=0 and self.amount<=100000):
      raise ValidationError("El monto debe encontrarse entre 0 y 100,000.")

  @api.onchange("type_move")
  def onchange_type_move(self):
    if self.type_move == 'ingreso':
      self.name = "Ingreso: "
      self.amount = 100
    elif self.type_move == "gasto":
      self.name = "Gasto: "
      self.amount = 50

  @api.model
  def create(self, vals):
    name = vals.get("name", "-")
    amount = vals.get("amount", "0")
    type_move = vals.get("type_move", "")
    date = vals.get("date", "")

    notas = """<p>Tipo de Movimiento: {}</p><p>Nombre: {}</p><p>Monto: {}</p><p>Fecha: {}</p>"""
    vals["notas"] = notas.format(type_move, name, amount, date)
    return super(Movimiento,self).create(vals)

  def unlink(self): # Condicionando acciones durante el evento de eliminar un registro
    for record in self:
      if record.amount >= 50:
        raise ValidationError("Movimientos con montos mayores a 50 no podran ser eliminados.")
    return super(Movimiento,self).unlink()


class Category(models.Model):
  _name = "sa.category" # sa_category
  _description = "Categoria"

  name = fields.Char(string="Nombre")
  type_move = fields.Selection(selection=[("ingreso","Ingreso"),("gasto","Gasto")], string="Tipo", default="ingreso", required=True)

  def ver_movimientos(self):
    return {
      "type":"ir.actions.act_window", #Accion de abrir nueva ventana
      "name":"Movimientos de categoria: " + self.name,
      "res_model":"sa.movimiento", #Modelo a la ventana que voy a mostrar
      "views":[[False,"tree"]], #Definimos que vista que se va a visualizar y sera una de tipo lista. El false es un ID donde podremos hacer referencia a una vista.
      "target":"self", #Como queremos ver la nueva vista, si dentro de la vista actual (self) o en una nueva vista flotante (new).
      "domain":[["category_id","=",self.id]]
    }


class Tag(models.Model):
  _name = "sa.tag" # sa_tag
  _description = "Tag"

  name = fields.Char(string="Nombre")
  type_move = fields.Selection(selection=[("ingreso","Ingreso"),("gasto","Gasto")], string="Tipo", default="ingreso", required=True)


class ResUsers(models.Model):
  _inherit = "res.users"
  movimiento_ids = fields.One2many("sa.movimiento","user_id")
  total_ingresos = fields.Float(string="Total de Ingresos", compute="_compute_movimientos")
  total_gastos = fields.Float(string="Total de Gastos", compute="_compute_movimientos")

  @api.depends("movimiento_ids")
  def _compute_movimientos(self):
    for record in self:
      record.total_ingresos = sum(record.movimiento_ids.filtered(lambda r:r.type_move=='ingreso').mapped("amount"))
      record.total_gastos = sum(record.movimiento_ids.filtered(lambda r:r.type_move=='gasto').mapped("amount"))

  def mi_cuenta(self): #Devolviendo una accion de ventana
    return {
      "type": "ir.actions.act_window",
      "name": "Mi cuenta",
      "res_model": "res.users",
      "res_id": self.env.user.id,
      "target": "self",
      "views": [(False,"form")]
    }