#!/usr/bin/env python3
""" Change school topics
"""

def update_topics(mongo_collection, name, topics):
    """ update_topics.
    """
    query = {"name": name}
    new_values = {"$set": {"topics": topics}}
    mongo_collection.update_many(query, new_values)
