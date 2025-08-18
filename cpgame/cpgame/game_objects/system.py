
from cpgame.systems.jrpg import JRPG

class GameSystem:
    def __init__(self):
        self.save_disabled = False           # save forbidden
        self.menu_disabled = False           # menu forbidden
        self.encounter_disabled = False      # encounter forbidden
        self.formation_disabled = False      # formation change forbidden
        self.battle_count = 0                # battle count
        self._save_count = 0                 # save count (private)
        self._version_id = 0                 # game version ID (private)
        self._window_tone = None             # custom window tone
        self._battle_bgm = None              # custom battle BGM
        self._battle_end_me = None           # custom battle end ME
        self._saved_bgm = None               # BGM saved before battle
        self._frames_on_save = 0             # frame count at save
        self._bgm_on_save = None             # BGM at time of save
        self._bgs_on_save = None             # BGS at time of save

    def japanese(self):
        if JRPG.data and JRPG.data.system:
            return JRPG.data.system.get_or("japanese", False)
        return False
    
    @property
    def window_tone(self):
        if self._window_tone is not None:
            return self._window_tone
        # Fallback to global data system
        if JRPG.data and JRPG.data.system:
            return JRPG.data.system.get_or("window_tone", None)
        return None

    @window_tone.setter
    def window_tone(self, tone):
        self._window_tone = tone
    
    @property
    def battle_bgm(self):
        if self._battle_bgm is not None:
            return self._battle_bgm
        if JRPG.data and JRPG.data.system:
            return JRPG.data.system.get_or("battle_bgm", None)
        return None

    @battle_bgm.setter
    def battle_bgm(self, bgm):
        self._battle_bgm = bgm

    @property
    def battle_end_me(self):
        if self._battle_end_me is not None:
            return self._battle_end_me
        if JRPG.data and JRPG.data.system:
            return JRPG.data.system.get_or("battle_end_me", None)
        return None

    @battle_end_me.setter
    def battle_end_me(self, me):
        self._battle_end_me = me

    def on_before_save(self):
        self._save_count += 1
        if JRPG.data and JRPG.data.system:
            self._version_id = JRPG.data.system.get_or("version_id", 0)
        else:
            self._version_id = 0
        
        # Save current frame count and last played BGM/BGS
        self._frames_on_save = 0 # Graphics.frame_count()
        self._bgm_on_save = 0 # RPG.BGM.last()
        self._bgs_on_save = 0 # RPG.BGS.last()

    def on_after_load(self):
        # Restore frame count and replay saved music
        # Graphics.set_frame_count(self._frames_on_save)
        # if self._bgm_on_save:
        #     self._bgm_on_save.play()
        # if self._bgs_on_save:
        #     self._bgs_on_save.play()
        pass

    def playtime(self):
        return 42 # TODO: use time counter ? 
        # return Graphics.frame_count() / Graphics.frame_rate()

    def playtime_s(self):
        total_seconds = int(self.playtime())
        hour = total_seconds // 3600
        minute = (total_seconds % 3600) // 60
        second = total_seconds % 60
        return "{:02d}:{:02d}:{:02d}".format(hour, minute, second)
        # Alternatively: f"{hour:02d}:{minute:02d}:{second:02d}" if using f-strings

    def save_bgm(self):
        self._saved_bgm = None # RPG.BGM.last()

    def replay_bgm(self):
        if self._saved_bgm:
            self._saved_bgm.replay()

    @property
    def save_count(self):
        return self._save_count

    @property
    def version_id(self):
        return self._version_id
    
    # TODO: def to_dict(self) -> Dict[str, Dict] and def from_dict(self, data: Dict[str, Dict])