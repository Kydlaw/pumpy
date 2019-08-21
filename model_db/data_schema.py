from marshmallow import Schema, fields, ValidationError, EXCLUDE

# TODO: pass twitter data extracted from the API to the different schemas to check if they are valid
# TODO: validate the whole Schema


class Data(object):
    """Correspond to a Data object in the database model. 
    It handles the metadata/annotations associated with the tweet.
    tweet is a Tweet object described below.
    
    """

    def __init__(self, tweet, data_source, info_source, info_type, info_rmativeness):
        self.tweet = tweet
        self.data_source = data_source
        self.info_source = info_source
        self.info_type = info_type
        self.info_rmativeness = info_rmativeness


class Tweet(object):
    """Correspond to a Tweet object in the database model. 
    user and entities are objects described below.
    
    """

    def __init__(
        self,
        id_str,
        coordinates,
        created_at,
        entities,
        favorite_count,
        favorited,
        geo,
        in_reply_to_status_id_str,
        in_reply_to_user_id_str,
        is_quote_status,
        lang,
        place,
        retweet_count,
        retweeted,
        source,
        text,
        user,
    ):
        self.id_str = id_str
        self.coordinates = coordinates
        self.created_at = created_at
        self.entities = entities
        self.favorite_count = favorite_count
        self.favorited = favorited
        self.geo = geo
        self.in_reply_to_status_id_str = in_reply_to_status_id_str
        self.in_reply_to_user_id_str = in_reply_to_user_id_str
        self.is_quote_status = is_quote_status
        self.lang = lang
        self.place = place
        self.retweet_count = retweet_count
        self.retweeted = retweeted
        self.source = source
        self.text = text
        self.user = user


class User(object):
    """Correspond to a User object in the database model.
    User refers to a user and his data. User is an entity found in a tweet.
    entities are objects described below.
    
    """

    def __init__(
        self,
        id_str,
        created_at,
        default_profile,
        default_profile_image,
        description,
        entities,
        favourites_count,
        followers_count,
        friends_count,
        geo_enabled,
        lang,
        listed_count,
        location,
        profile_user_background_image,
        statuses_count,
        time_zone,
        utc_offset,
        verified,
    ):
        self.id_str = id_str
        self.created_at = created_at
        self.default_profile = default_profile
        self.default_profile_image = default_profile_image
        self.description = description
        self.entities = entities
        self.favourites_count = favourites_count
        self.followers_count = followers_count
        self.friends_count = friends_count
        self.geo_enabled = geo_enabled
        self.lang = lang
        self.listed_count = listed_count
        self.location = location
        self.profile_user_background_image = profile_user_background_image
        self.statuses_count = statuses_count
        self.time_zone = time_zone
        self.utc_offset = utc_offset
        self.verified = verified


class Entities(object):
    """Correspond to a the various entities which can be found in a User profile
    description or in a tweet.
    
    """

    def __init__(self, hashtags, media, url, user_mentions, symbols):
        self.hashtags = hashtags
        self.media = media
        self.url = url
        self.user_mentions = user_mentions
        self.symbols = symbols


class Hashtags(object):
    """Sub entity
    Hashtags '#' used in the text.
    
    """

    def __init__(self, indices, text):
        self.indices = indices
        self.text = text


class Media(object):
    """Sub entity
    Media used in the text (photos, videos...).
    
    """

    def __init__(self, indices, type):
        self.indices = indices
        self.type = type


class Urls(object):
    """Sub entity
    Urls used in the text.
    
    """

    def __init__(self, indices):
        self.indices = indices


class UserMentions(object):
    """Sub entity
    User mentioned in the text.
    They are identified through their id's.

    """

    def __init__(self, indices, id_str):
        self.indices = indices
        self.id_str = id_str


class Symbols(object):
    """Sub entity
    Symbols '$' used in the text.
    
    """

    def __init__(self, indices, text):
        self.indices = indices
        self.text = text


class Geo(object):
    def __init__(self, type, coordinates):
        self.type = type
        self.coordinates = coordinates


class Bounding_box(object):
    def __init__(self, type, coordinates):
        self.type = type
        self.coordinates = coordinates


class Place(object):
    def __init__(
        self,
        id,
        place_type,
        url,
        name,
        full_name,
        country_code,
        country,
        bounding_box,
        attributes,
    ):
        self.id = id
        self.place_type = place_type
        self.url = url
        self.name = name
        self.full_name = full_name
        self.country_code = country_code
        self.country = country
        self.bounding_box = bounding_box


class Coordinates(object):
    def __init__(self, coordinates, type):
        self.coordinates = coordinates
        self.type = type


class HashtagsSchema(Schema):
    indices = fields.List(fields.Integer())
    text = fields.String()


class MediaSchema(Schema):
    indices = fields.List(fields.Integer())
    type = fields.String()


class UrlsSchema(Schema):
    indices = fields.List(fields.Integer())


class UserMentionsSchema(Schema):
    id_str = fields.String()
    text = fields.String()


class SymbolsSchema(Schema):
    indices = fields.List(fields.Integer())
    text = fields.String()


class EntitiesSchema(Schema):
    hashtags = fields.List(fields.Nested(HashtagsSchema))
    media = fields.List(fields.Nested(MediaSchema))
    url = fields.List(fields.Nested(UrlsSchema))
    user_mentions = fields.List(fields.Nested(UserMentionsSchema))
    symbols = fields.List(fields.Nested(SymbolsSchema))


class UserSchema(Schema):
    id_str = fields.String()
    created_at = fields.String()
    default_profile = fields.Boolean()
    default_profile_image = fields.Boolean()
    description = fields.String()
    entities = fields.Nested(EntitiesSchema)
    favourites_count = fields.Integer()
    followers_count = fields.Integer()
    friends_count = fields.Integer()
    geo_enabled = fields.Boolean()
    lang = fields.String()
    listed_count = fields.Integer()
    location = fields.String()
    profile_user_background_image = fields.Boolean()
    statuses_count = fields.Integer()
    time_zone = fields.String()
    utc_offset = fields.String()
    verified = fields.Boolean()


class TweetSchema(Schema):
    id_str = fields.String()
    coordinates = fields.Nested(GeoSchema)
    created_at = fields.String()
    entities = fields.Nested(EntitiesSchema)
    favorite_count = fields.Integer()
    favorited = fields.Boolean()
    geo = fields.Nested(GeoSchema)
    in_reply_to_status_id_str = fields.String()
    in_reply_to_user_id_str = fields.String()
    is_quote_status = fields.Boolean()
    lang = fields.String()
    place = fields.Nested(GeoSchema)
    retweet_count = fields.Integer()
    retweeted = fields.Boolean()
    source = fields.String()
    text = fields.String()
    user = fields.Nested(UserSchema)


class GeoSchema(Schema):
    type = fields.String()
    coordinates = fields.List(fields.Float())


class BoundingBoxSchema(Schema):
    type = fields.String()
    coordinates = fields.List(fields.Float())


class PlaceSchema(Schema):
    id = fields.Integer()
    place_type = fields.String()
    url = fields.Url()
    name = fields.String()
    full_name = fields.String()
    country_code = fields.String()
    country = fields.String()
    bounding_box = fields.Nested(BoundingBoxSchema)


class CoordinatesSchema(Schema):
    coordinates = fields.List(fields.Float())
    type = fields.String()


class DataSchema(Schema):
    tweet = fields.Nested(TweetSchema)
    data_source = fields.String()
    info_source = fields.String()
    info_type = fields.String()
    info_rmativeness = fields.String()
