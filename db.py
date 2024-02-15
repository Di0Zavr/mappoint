import mongoengine as me


class Tag(me.Document):
    name = me.StringField(required=1)


class User(me.Document):
    nickname = me.StringField(required=1)
    email = me.EmailField(required=1)


class Town(me.Document):
    name = me.StringField(required=True)
    description = me.StringField()
    image_path = me.URLField()


class PointOfInterest(me.Document):
    title = me.StringField(required=1)
    subtitle = me.StringField()
    description = me.StringField()
    coordinates = me.GeoPointField(required=1)
    image_path = me.URLField()
    town = me.ReferenceField(Town)


class PointTag(me.Document):
    point = me.ReferenceField(PointOfInterest)
    tag = me.ReferenceField(Tag)


class Favourite(me.Document):
    point = me.ReferenceField(PointOfInterest)
    user = me.ReferenceField(User)
