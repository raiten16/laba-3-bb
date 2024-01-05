from marshmallow import Schema, fields, validate

class Us_Sch(Schema):
    u_name = fields.String(required=True)
    curr_id = fields.Int(required=False)

class Cat_Sch(Schema):
    name = fields.String(required=True)

class Rec_Sch(Schema):
    cat_id = fields.Integer(required=True, validate=validate.Range(min=0))
    u_id = fields.Integer(required=True, validate=validate.Range(min=0))
    am = fields.Float(required=True, validate=validate.Range(min=0.0))
    curr_id = fields.Int(required=False)

class Curr_Sch(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    symbol = fields.Str(required=True)
