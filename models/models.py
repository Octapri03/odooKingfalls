# -*- coding: utf-8 -*-


from datetime import timedelta, datetime
from email.policy import default
import random
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class player(models.Model):
    _name = 'res.partner'
    _description = 'players of the game'
    _inherit = 'res.partner' 

    name = fields.Char(required=True)
    comarca = fields.Many2one('kingfalls.comarca')
    bando = fields.Many2one('kingfalls.bando', ondelete = "set null")
    poblacion = fields.Integer(default = 100)
    guardias = fields.Integer(default = 10)
    dinero = fields.Integer(default = 1000)
    produccion = fields.Integer(default = 500)
    aliados = fields.Many2many('kingfalls.ciudad', compute='lista_aliados')
    minas = fields.Many2many('kingfalls.mina' , compute='lista_minas')
    num_minas_compradas_bosque = fields.Integer(default = 0, readOnly = True)
    num_minas_compradas_desierto = fields.Integer(default = 0, readOnly = True)
    num_minas_compradas_pantano = fields.Integer(default = 0, readOnly = True)
    is_player = fields.Boolean(default=False)

    @api.depends('bando')
    def lista_aliados(self):
        for c in self:
            c.aliados = self.env['kingfalls.ciudad'].search([( "bando.name", "=", c.bando.name )])
            print(c.aliados)
            print(c.bando)

    @api.depends('dinero')
    def lista_minas(self):
        for c in self:
            c.minas = self.env['kingfalls.mina'].search([( "precio", "<", c.dinero )])
            print(c.minas)
            print(c.dinero)

    @api.constrains('dinero')
    def _check_dinero(self):
        for player in self:
            if player.name == "":
                raise ValidationError("El name no puede ser nulo")

    @api.onchange('dinero')
    def _onchange_dinero(self):
        for c in self:  
            print("patata")
            if self.dinero == 0:
                return {
                    'warning': {
                    'title': "Quiebra",
                    'message': "Has gastado todo tu dinero",
                    }
                }

    def sumar_guardias(self):
        for b in self:
            if b.dinero >= 1000:
                b.guardias += 10
                b.dinero -= 1000

    def show_mines(self):
        view_id = self.env.ref('kingfalls.playerform').id
        return {
            'name': 'player Mines',
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.id,
            'views': [(view_id, 'form')],
            'context': dict(self._context)            
        }

    @api.model
    def produce(self):  # ORM CRON
        self.search([]).produce_dinero()

    def produce_dinero(self):
        for player in self:
            dinero = player.dinero + player.produccion

            player.write({
                "dinero": dinero
            })

class player_modify_wizard(models.TransientModel):
    _name = 'kingfalls.player_modify_wizard'
    _description = 'Modificar player'

    def _get_player(self):
        return self.env['res.partner'].browse(self._context.get('active_id'))
    
    player = fields.Many2one('res.partner', default=_get_player)
    name = fields.Char(required=True)
    comarca = fields.Many2one('kingfalls.comarca', required=True)
    bando = fields.Many2one('kingfalls.bando', required=True)
    poblacion = fields.Integer(default = 100, required=True)
    guardias = fields.Integer(default = 10, required=True)
    dinero = fields.Integer(default = 1000, required=True)
    produccion = fields.Integer(default = 500, required=True)
    is_player = fields.Boolean(default=False)

    def guardar_player(self):
        self.player.write({
            'name': self.name,
            'comarca': self.comarca,
            'bando': self.bando,
            'poblacion': self.poblacion,
            'guardias': self.guardias,
            'dinero': self.dinero,
            'produccion': self.produccion,
            'is_player': self.is_player
        })

class ciudad(models.Model):
    _name = 'kingfalls.ciudad'
    _description = 'ciudad'

    name = fields.Char(required=True)
    descripcion = fields.Char()
    comarca = fields.Many2one('kingfalls.comarca')
    bando = fields.Many2one('kingfalls.bando', ondelete = "set null")
    image = fields.Image(max_width = 500, max_height = 500)
    poblacion = fields.Integer(default = 100)
    guardias = fields.Integer(default = 10)
    defensa = fields.Selection([('1', "Alta"), ('2', "Media"), ('3', "Baja")], default = '3')

class bando(models.Model):
    _name = 'kingfalls.bando'
    _description = 'bando'

    name = fields.Char(required=True)
    descripcion = fields.Char(required=True)
    image = fields.Image(max_width = 250, max_height = 250)

class comarca(models.Model):
    _name = 'kingfalls.comarca'
    _description = 'comarca'

    name = fields.Char(required=True)
    descripcion = fields.Char(required=True)
    image = fields.Image(max_width = 250, max_height = 250)

class raid(models.Model):
    _name = 'kingfalls.raid'
    _description = 'raids'

    name = fields.Char(required=True)
    descripcion = fields.Char()
    image = fields.Image(max_width = 500, max_height = 500)
    amenaza = fields.Selection([('1', "Alta"), ('2', "Media"), ('3', "Baja")], default='1')
    poder = fields.Integer()

class mina(models.Model):
    _name = 'kingfalls.mina'
    _description = 'minas'

    name = fields.Char(required=True)
    descripcion = fields.Char()
    produccion = fields.Integer()
    precio = fields.Integer()
    image = fields.Image(max_width = 250, max_height = 250)
 
    def comprar_mina(self):
        for b in self:
            player = self.env['res.partner'].browse(self.env.context['ctx_player'])[0]
            player.produccion = player.produccion + b.produccion
            player.dinero = player.dinero - b.precio
            if b.name == "Mina del bosque":
                player.num_minas_compradas_bosque += 1
            elif b.name == "Mina del desierto":
                player.num_minas_compradas_desierto += 1
            elif b.name == "Mina del pantano":
                player.num_minas_compradas_pantano += 1


class monstruos(models.Model):
    _name = 'kingfalls.monstruos'
    _description = 'raids'

    name = fields.Char(required=True)
    descripcion = fields.Char()
    image = fields.Image(max_width = 500, max_height = 500)
    fuerza = fields.Integer()
    vida = fields.Integer(default = 50)
    aguante = fields.Integer(default = 75)
    nivel = fields.Integer(default = 1)   

class battle(models.Model):
    _name = 'kingfalls.battle'
    _description = 'Batallas'

    name = fields.Char()
    date_start = fields.Datetime(readonly=True, default=fields.Datetime.now)
    date_end = fields.Datetime(compute='_get_duracion')
    progress = fields.Float()
    player1 = fields.Many2one('res.partner')
    player2 = fields.Many2one('res.partner')
    rondas_ganadas_player1 = fields.Integer(default = 0, readOnly = True)
    rondas_ganadas_player2 = fields.Integer(default = 0, readOnly = True)
    winner = fields.Many2one('res.partner', readOnly = True)
    is_button_used = fields.Boolean(default=False)

    @api.onchange('player1')
    def onchange_eleccion_player1(self):
        self.name = self.player1.name
        return {
            'domain': {
            'player2': [('id', '!=', self.player1.id), ('is_player', '=', True)],
            }
        }

    @api.onchange('player2')
    def onchange_player2(self):
        return {
            'domain': {
            'player1': [('id', '!=', self.player2.id), ('is_player', '=', True)],
            }
        }

    @api.depends('player1', 'player2')
    def _get_duracion(self):
        for b in self:
            if b.player1.comarca != b.player2.comarca:
                time = 5.0
                b.date_end = fields.Datetime.to_string(
                fields.Datetime.from_string(b.date_start) + timedelta(days=time))
            else:
                time = 1.0
                b.date_end = fields.Datetime.to_string(fields.Datetime.from_string(b.date_start) + timedelta(days=time))

    def iniciar_batalla(self):
        if self.is_button_used:
            raise ValidationError("La batalla solo puede ser lanzada una vez")
        else:
            self.is_button_used = True
            b = self
            rondas_ganadas_player1 = 0
            rondas_ganadas_player2 = 0

            for _ in [0, 1, 2, 3, 4]:
                fuerza1 = b.player1.guardias + (b.player1.poblacion/2)
                fuerza2 = b.player2.guardias + (b.player2.poblacion/2)
                fuerza1 = fuerza1 * random.random()
                fuerza2 = fuerza2 * random.random()
                if fuerza1 > fuerza2:
                    b.player1.dinero += b.player2.dinero/20
                    b.player2.dinero -= b.player2.dinero/20
                    rondas_ganadas_player1 += 1
                    b.progress += 20
                else:
                    b.player2.dinero += b.player1.dinero/20
                    b.player1.dinero -= b.player1.dinero/20
                    rondas_ganadas_player2 += 1
                    b.progress += 20

            b.rondas_ganadas_player1 = rondas_ganadas_player1
            b.rondas_ganadas_player2 = rondas_ganadas_player2

            if rondas_ganadas_player1 > rondas_ganadas_player2:
                b.player1.dinero += b.player2.dinero/4
                b.player2.dinero -= b.player2.dinero/4
                b.winner = b.player1
            else:  
                b.player2.dinero += b.player1.dinero/4
                b.player1.dinero -= b.player1.dinero/4
                b.winner = b.player2


class battle_wizard(models.TransientModel):
    _name = 'kingfalls.battle_wizard'
    _description = 'Crear Batallas'

    def _get_player(self):
        return self.env['res.partner'].browse(self._context.get('active_id'))
    
    name = fields.Char()
    date_start = fields.Datetime(readonly=True, default=fields.Datetime.now)
    date_end = fields.Datetime(compute='_get_duracion')
    player1 = fields.Many2one('res.partner', default = _get_player, readOnly = True)
    player1_guardias = fields.Integer(related = 'player1.guardias')
    player1_image = fields.Image(related='player1.image_1920')
    player1_resume = fields.Many2one('res.partner', related = 'player1')
    player2 = fields.Many2one('res.partner')
    player2_guardias = fields.Integer(related = 'player2.guardias')
    player2_image = fields.Image(related='player2.image_1920')
    player2_resume = fields.Many2one('res.partner', related = 'player2')
    state = fields.Selection([('1','player1'),('2','player2'),('3','battle')], default='1')

    @api.depends('player1', 'player2')
    def _get_duracion(self):
        for b in self:
            if b.player1.comarca != b.player2.comarca:
                time = 5.0
                b.date_end = fields.Datetime.to_string(
                fields.Datetime.from_string(b.date_start) + timedelta(days=time))
            else:
                time = 1.0
                b.date_end = fields.Datetime.to_string(fields.Datetime.from_string(b.date_start) + timedelta(days=time))

    @api.onchange('player1')
    def onchange_eleccion_player1(self):
        self.name = self.player1.name
        return {
            'domain': {
            'player2': [('id', '!=', self.player1.id), ('is_player', '=', True)],
            }
        }

    @api.onchange('player2')
    def onchange_player2(self):
        return {
            'domain': {
            'player1': [('id', '!=', self.player2.id), ('is_player', '=', True)],
            }
        }
    
    def button_state_next(self):
        if self.state == '1':
            self.state = '2'
        elif self.state == '2':
            if not self.player2:
                raise ValidationError("Debe rellenar el player 2")
            else:
                self.state  = '3'
        return {
            'name': 'create battle',
            'type': 'ir.actions.act_window',
            'res_model': 'kingfalls.battle_wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': dict(self._context, player1_context=self.player1.id)            
        }

    def button_state_previos(self):
        if self.state == '2':
            self.state = '1'
        elif self.state == '3':
            self.state = '2'
        return{
            'name': 'create battle',
            'type': 'ir.actions.act_window',
            'res_model': 'kingfalls.battle_wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id
        }
    
    def create_battle(self):
        self.env['kingfalls.battle'].create({
            'name': self.name,
            'player1': self.player1.id,
            'player2': self.player2.id         
        })
