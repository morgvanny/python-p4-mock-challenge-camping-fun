from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    # Add relationship

    signups = db.relationship(
        "Signup", cascade="all, delete-orphan", back_populates="activity"
    )

    campers = association_proxy("signups", "camper")

    # Add serialization rules

    serialize_rules = ("-signups",)

    def __repr__(self):
        return f"<Activity {self.id}: {self.name}>"


class Camper(db.Model, SerializerMixin):
    __tablename__ = "campers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

    # Add relationship

    signups = db.relationship(
        "Signup", cascade="all, delete-orphan", back_populates="camper"
    )

    serialize_rules = ("-signups",)

    activities = association_proxy("signups", "activity")

    @validates("name")
    def validate_name(self, key, name):
        if not name:
            raise ValueError("Campers must have a name.")
        return name

    @validates("age")
    def validate_age(self, key, age):
        if age not in range(8, 19):
            raise ValueError("Campers must be between 8 and 18.")
        return age

    def __repr__(self):
        return f"<Camper {self.id}: {self.name}>"


class Signup(db.Model, SerializerMixin):
    __tablename__ = "signups"

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    camper_id = db.Column(db.Integer, db.ForeignKey("campers.id"))
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"))

    # Add relationships

    activity = db.relationship("Activity", back_populates="signups")

    camper = db.relationship("Camper", back_populates="signups")

    # Add serialization rules

    serialize_rules = ("-activity", "-camper")

    @validates("time")
    def validate_time(self, key, time):
        if time not in range(0, 24):
            raise ValueError("Time must be between 0 and 23.")
        return time

    @validates("camper_id")
    def validate_camper_id(self, key, camper_id):
        camper = Camper.query.get(camper_id)
        if not camper:
            raise ValueError("Camper id must reference an existing camper.")
        return camper_id

    @validates("activity_id")
    def validate_activity_id(self, key, activity_id):
        activity = Activity.query.get(activity_id)
        if not activity:
            raise ValueError("Activity id must reference an existing activity.")
        return activity_id

    def __repr__(self):
        return f"<Signup {self.id}>"


# add any models you may need.
