from tinydb import TinyDB, Query
import jsonpickle as jsonify
import sys

sys.path.append("..")

class DB():
    def __init__(self, db_path):
        self.db = TinyDB(db_path)

    def reset(self):
        # Dont release
        self.db.purge()

    def get(self, indexing_id):
        RootObj = Query()


        if not isinstance(indexing_id, str):
            indexing_id = str(indexing_id)

        objs = self.db.search(RootObj.ttrpg_id == indexing_id)
        if objs == []:
            return None
        # print(f"** Got {type(self)} Settings **", objs[0])
        return objs[0]

    def save(self, indexing_id, info):
        
        if not isinstance(indexing_id, str):
            indexing_id = str(indexing_id)

        assert(isinstance(info, dict))
        
        info["ttrpg_id"] = indexing_id

        if self.get(indexing_id) is None:
            self.db.insert(info)
        else:
            self.db.update(info)
        # print(f"** Saved {type(self)} Settings **", self.db.all())



class PlayerDB(DB):
    def __init__(self):
        super().__init__('player.json')

    def save(self, indexing_id, user_icon):
        attrs = {}
        attrs["icon"] = user_icon
        super().save(indexing_id, attrs)



class GameDB(DB):
    def __init__(self):
        super().__init__('game.json')

    def save(self, indexing_id, dungeon, players, start_time, end_time):
        attrs = {}
        if dungeon is not None: attrs["dungeon"] = jsonify.encode(dungeon)
        if players is not None: attrs["players"] = players
        if start_time is not None: attrs["start_time"] = start_time
        if end_time is not None: attrs["end_time"] = end_time
        super().save(indexing_id, attrs)

    def get(self, indexing_id):
        obj = super().get(indexing_id)
        if obj is not None:
            d = obj["dungeon"]
            if isinstance(d, str):
                obj["dungeon"] = jsonify.decode(d)
        return obj