from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///catalogemenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create quest user
guest = User(name="quest", email="guest@catalog.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(guest)
session.commit()

# Catalog for Soccer
category1 = Category(user_id=1, name="Soccer")

session.add(category1)
session.commit()

item1 = Item(user_id=1, name="ball", description="A ball is a round object with various uses. It is used in ball games",
             category=category1)

session.add(item1)
session.commit()

item2 = Item(user_id=1, name="T-shirt", description="A T-shirt is a style of unisex fabric shirt named after the T shape of its body and sleeves",
             category=category1)

session.add(item2)
session.commit()

item3 = Item(user_id=1, name="boots", description="called cleats or soccer shoes in North America, are an item of footwear worn when playing football",
             category=category1)

session.add(item3)
session.commit()

# catalog for Baseball
category2 = Category(user_id=1, name="Basketball")

session.add(category2)
session.commit()

item1 = Item(user_id=1, name="ball", description="A ball is a round object with various uses. It is used in ball games",
             category=category2)

session.add(item1)
session.commit()

item2 = Item(user_id=1, name="T-shirt", description="A T-shirt is a style of unisex fabric shirt named after the T shape of its body and sleeves",
             category=category2)

session.add(item2)
session.commit()

item3 = Item(user_id=1, name="sneakers", description="are shoes primarily designed for sports or other forms of physical exercise",
             category=category2)

session.add(item3)
session.commit()

#catalog for Baseball
category3 = Category(user_id=1, name="Baseball")

session.add(category3)
session.commit()

item1 = Item(user_id=1, name="baseball bat", description="A baseball bat is a smooth wooden or metal club used in the sport of baseball to hit the ball after it is thrown by the pitcher.",
             category=category3)

session.add(item1)
session.commit()

item2 = Item(user_id=1, name="baseball cap", description="A baseball cap is a type of soft cap with a rounded crown and a stiff peak projecting in front.",
             category=category3)

session.add(item2)
session.commit()

item3 = Item(user_id=1, name="T-shirt", description="A T-shirt is a style of unisex fabric shirt named after the T shape of its body and sleeves",
             category=category3)

session.add(item3)
session.commit()


print "added menu items!"
