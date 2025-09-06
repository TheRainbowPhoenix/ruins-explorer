# main.py
# This file contains the complete port of the "Promenad" game to the cpgame engine.
# The original code has been refactored to fit the engine's scene-based, non-blocking architecture.
# All dependencies on the 'ion' module have been removed and replaced with the engine's input manager.

from cpgame.engine.game import Game
from cpgame.engine.scene import Scene
import gint
from time import sleep
from random import randint

# --- Asset Placeholders ---
# In a real project, these would be loaded from sprite files.
# Here, we create dummy 1x1 images to ensure the code runs without errors.
# The 'profile' and other arguments are based on the gint.image signature.
def create_dummy_image(width=1, height=1):
    """Creates a minimal gint.image object."""
    return gint.image(
        profile=gint.IMAGE_P4_RGB565A, color_count=1, width=width, height=height, stride=1,
        data=b'\x00', palette=b'\xff\xff' # White pixel
    )

from cpgame.game_assets.promenad_data import sentier, fond4, decor_champi, decor_fougere, points_de_vie, objets_precieux, objet_coffre_envahi, objet_rocher, objet_panneau, panneau_morceaux, ennemi_arbre_1, ennemi_arbre_2, ennemi_arbre_3, corbeau_walk, bouleau



# --- Game Constants ---
LL = 396  # Screen width
HH = 224  # Screen height
Arbres = [10, 35, 80, 135, 160, 220, 270, 300, 320, 340, 390, 410, 445, 480]
clr_fond = gint.C_RGB(20, 10, 5)
largeur_niveau = 792 + 396  # Image width + screen width

# --- Helper Functions ---
def fill_rect(x, y, l, h, clr):
    gint.drect(x, y, x + l, y + h, clr)

# --- Game Object Classes ---

class Objets:
    def __init__(self, x, y, Type, NivEnvahissement=2, contenu=""):
        self.x = x
        self.y = y
        self.Type = Type  # "rocher", "coffre", "panneau", "feuille", "buisson"
        self.lu = False
        self.contenu = ""
        self.texte = ""
        self.NivEnvahissement = 0

        if self.Type in ("coffre", "buisson"):
            self.NivEnvahissement = NivEnvahissement
            if self.Type == "coffre":
                self.contenu = contenu
        elif self.Type == "panneau":
            self.texte = NivEnvahissement
        elif self.Type == "feuille":
            self.Tic = 300
        
        sprite_map = {
            "rocher": objet_rocher,
            "coffre": objet_coffre_envahi,
            "panneau": objet_panneau,
            "feuille": points_de_vie,
            "buisson": (decor_fougere, decor_champi)[randint(0, 1)]
        }
        self.sprite = sprite_map[self.Type]

    def update(self, scene):
        """Handles logic for the object, like timers or giving items."""
        if self.Type == "coffre" and self.contenu != "" and self.NivEnvahissement == 0:
            scene.Objets_recuperes.append(self.contenu)
            scene.Vie_max = 10 + 2 * scene.Objets_recuperes.count("Vie+")
            scene.Attaque = 5 + 3 * scene.Objets_recuperes.count("Atq+")
            # In a real game, you might want to show the item before it disappears
            # For this port, we instantly grant it. The original sleep(2) is removed.
            self.contenu = ""

        if self.Type == "feuille":
            self.Tic -= 1
            if self.Tic <= 0 and self in scene.Liste_feuilles:
                scene.Liste_feuilles.remove(self)

    def draw(self, scene):
        """Draws the object on the screen."""
        dX = 1 + 41 * 2 * (self.Type == "rocher")
        dY = 1
        h = 40 - 10 * (self.Type == "buisson")
        l = 40 - 10 * (self.Type == "buisson")

        # Calculate scrolled position
        if scene.xJ < LL // 2:
            posX = self.x
        elif scene.xJ > largeur_niveau - LL // 2:
            posX = LL - largeur_niveau + self.x
        else:
            posX = LL // 2 + (self.x - scene.xJ)

        if self.Type == "coffre":
            gint.dsubimage(posX, self.y, self.sprite, dX + 41 * (4 - self.NivEnvahissement), dY, l, h)
            if self.contenu != "" and self.NivEnvahissement == 0:
                # This part of the original code had logic; now it just draws.
                # The item granting logic is in the update method.
                item_index = ["Vie+", "Atq+", "CleB", "Vit+"].index(self.contenu)
                gint.dsubimage(posX + 10, self.y + 5, objets_precieux, dX + 21 * item_index, dY, 20, 20)
        elif self.Type == "feuille":
            if self.Tic > 100 or (self.Tic // 10) % 2 == 0:
                gint.dsubimage(posX, self.y, self.sprite, dX + 21 * 3, 1, 20, 20)
        elif self.Type == "panneau":
            gint.dsubimage(posX, self.y, self.sprite, dX + 41 * (2 - self.lu), dY, l, h)
        else:
            gint.dsubimage(posX, self.y, self.sprite, dX, dY, l, h)

    def draw_panel_content(self):
        """Draws the panel UI and text."""
        # Draw frame
        Qx = (LL - 41 - 40) // 18
        Rx = (LL - 41 - 40) % 18
        Qy = (HH - 41 - 40) // 18
        Ry = (HH - 41 - 40) % 18
        gint.dsubimage(Rx // 2, Ry // 2, panneau_morceaux, 1, 1, 41, 41)
        gint.dsubimage(Rx // 2 + 18 * Qx + 41, Ry // 2, panneau_morceaux, 64, 1, 40, 41)
        gint.dsubimage(Rx // 2, Ry // 2 + 18 * Qy + 41, panneau_morceaux, 1, 64, 41, 40)
        gint.dsubimage(Rx // 2 + 18 * Qx + 41, Ry // 2 + 18 * Qy + 41, panneau_morceaux, 64, 64, 40, 40)
        for k in range(Qx):
            gint.dsubimage(Rx // 2 + 18 * k + 41, Ry // 2, panneau_morceaux, 44, 1, 18, 41)
            gint.dsubimage(Rx // 2 + 18 * k + 41, Ry // 2 + 18 * Qy + 41, panneau_morceaux, 44, 63, 18, 41)
        for k in range(Qy):
            gint.dsubimage(Rx // 2, Ry // 2 + 18 * k + 41, panneau_morceaux, 1, 44, 41, 18)
            gint.dsubimage(Rx // 2 + 18 * Qx + 41, Ry // 2 + 18 * k + 41, panneau_morceaux, 63, 44, 41, 18)
        
        # Draw text
        for k in range(len(self.texte)):
            gint.dtext(60, 60 + 20 * k, gint.C_RGB(25, 20, 5), self.texte[k])
        gint.dtext(150, HH - 10 - 41 - 10, gint.C_RGB(30, 15, 0), "-- EXE pour continuer --")

class Ennemis:
    def __init__(self, x, y, vie, atq, Type=-1):
        self.x = x
        self.y = y
        self.vie = vie
        self.direction = 2 * randint(0, 1) - 1
        self.atq = atq
        self.xi = x
        self.tic = 0
        self.ticHumeur = 0
        self.Humeur = "neutral"
        self.Type = randint(0, 2) if Type == -1 else Type
        self.sprite = (ennemi_arbre_1, ennemi_arbre_2, ennemi_arbre_3)[self.Type]

    def update(self):
        """Handles enemy logic like movement and timers."""
        self.tic = (self.tic + 1) % 30
        self.ticHumeur = max(0, self.ticHumeur - 1)
        if self.ticHumeur == 0:
            self.Humeur = "neutral"
        
        if not self.xi - 50 <= self.x <= self.xi + 50:
            self.direction = (self.x < self.xi - 50) - (self.x > self.xi + 50)
        
        self.x += self.direction

    def draw(self, scene):
        """Draws the enemy on the screen."""
        decalage = self.tic // 5
        dX = 1 + 41 * decalage
        dY = 1
        h = 40
        l = 40

        if scene.xJ < LL // 2:
            posX = self.x
        elif scene.xJ > largeur_niveau - LL // 2:
            posX = LL - largeur_niveau + self.x
        else:
            posX = LL // 2 + (self.x - scene.xJ)

        gint.dsubimage(posX, self.y, self.sprite, dX, dY, l, h)

        if self.ticHumeur > 0:
            if self.Humeur == "sad":
                if self.Type == 0:
                    gint.dsubimage(posX + 13, self.y + 13 + 1 * (decalage in (2, 5)) + 2 * (decalage in (3, 4)), self.sprite, 260, 15, 14, 5)
                    gint.dsubimage(posX + 13, self.y + 19 + 1 * (decalage in (2, 5)) + 2 * (decalage in (3, 4)), self.sprite, 260, 25, 14, 6)
                elif self.Type == 1:
                    gint.dsubimage(posX + 12, self.y + 15 + 1 * (decalage in (1, 4)) + 2 * (decalage in (2, 3)), self.sprite, 255, 15, 16, 6)
                    gint.dsubimage(posX + 12, self.y + 23 + 1 * (decalage in (1, 4)) + 2 * (decalage in (2, 3)), self.sprite, 255, 25, 16, 4)
                elif self.Type == 2:
                    gint.dsubimage(posX + 14, self.y + 16 + 1 * (decalage in (1, 4)) + 2 * (decalage in (2, 3)), self.sprite, 260, 15, 12, 7)
            elif self.Humeur == "happy":
                if self.Type == 0:
                    gint.dsubimage(posX + 13, self.y + 19 + 1 * (decalage in (2, 5)) + 2 * (decalage in (3, 4)), self.sprite, 260, 35, 14, 6)
                elif self.Type == 1:
                    gint.dsubimage(posX + 12, self.y + 23 + 1 * (decalage in (1, 4)) + 2 * (decalage in (2, 3)), self.sprite, 255, 35, 16, 4)

    def on_defeat(self, scene):
        """Called when the enemy's health reaches zero."""
        if randint(1, 5) == 1:
            scene.Liste_feuilles.append(Objets(self.x, self.y, "feuille"))


# --- Main Game Scene ---

class PromenadScene(Scene):
    def create(self):
        """Initializes the game state when the scene starts."""
        self.game_state = "intro" # "intro", "playing", "panel", "game_over", "level_complete"
        self.Niveau = 0
        
        # Intro text setup
        self.intro_textes = [
            ("Bienvenue dans l'aventure :", "     Promenade en Foret"),
            ("Connais-tu l'histoire de la foret des", "Carpettes ?", "Non ?", "Eh bien moi non plus."),
            ("Mais ce n'est pas le sujet, en fait.", "Je vais te raconter l'histoire", "de la foret de Brosse&Viande"),
            ("Il y a bien longtemps, le seigneur", "Brosse, avec ses cheveux coiffes en...", "- enfin bref - ", "etait un grand mangeur de viande."),
            ("Il aimait se promener en foret", "pour rapporter de quoi satisfaire", "son tres grand appetit."),
            ("Mais un jour, une mysterieuse", "malediction s'abatit sur sa foret", "preferee et... il devint chauve ! ", "Ah non, c'est pas ca. Je m'egare."),
            ("Donc, je disais : une malediction", "s'abatit sur sa foret preferee et", "les animaux qui y vivaient", "furent transformes en creatures", "hostiles et aggressives !"),
            ("Allons voir de quoi il s'agit !", "Au fait, si tu t'aventures dans cette", "mysterieuse foret, tu pourrais bien", "etre tranforme toi aussi...", "Prends garde !")
        ]
        self.current_intro_panel = 0
        self.active_panel = Objets(0, 0, "panneau", self.intro_textes[0])

        self.load_level(self.Niveau)

    def load_level(self, level_num):
        """Sets up all entities and player state for a given level."""
        self.xJ, self.yJ = 20, 170

        if level_num == 0:
            self.Liste_ennemis = [Ennemis(x, HH - 50, 20 + 5 * (x > 1000), 1) for x in [200, 820, 870, 900, 950, 990, 1050, 1100, 1150]]
            self.Liste_rochers = [Objets(570, HH - 70, "rocher")]
            self.Liste_coffres = [Objets(x, HH - 80, "coffre", NivEnv, Contenu) for (x, NivEnv, Contenu) in [(330, 0, ""), (380, 2, "Vie+"), (430, 4, "Atq+")]]
            textes = (("Ceci est un panneau...", "Utilise les fleches pour te deplacer"), ("Oh, une creature hostile !", "Appuie sur SHIFT pour attaquer."), ("Si l'ennemi te touche, tu perds de la vie.",), ("Les coffres sont parfois pleins...",), ("Un rocher bloque le passage !", "Un appui sur ALPHA permet de sauter."), ("Lors d'un saut, on peut attaquer vers le bas.",), ("Elimine tous les ennemis pour continuer.",))
            self.Liste_panneaux = [Objets(x, HH-90, "panneau", texte) for (x,texte) in [(70,textes[0]), (120,textes[1]), (250,textes[2]), (300,textes[3]), (500,textes[4]), (650,textes[5]), (750,textes[6])]]
        elif level_num == 1:
            self.Liste_ennemis = [Ennemis(x, HH-50, 20+5*(x//100), 1) for x in [80,120,200,350,400,450,700,720,740,820,950,990,1050,1100,1150]]
            self.Liste_rochers = [Objets(x, HH-70, "rocher") for x in [260,510,600,880]]
            self.Liste_coffres = [Objets(x, HH-80, "coffre", NivEnv, Contenu) for (x,NivEnv,Contenu) in [(30,0,""),(160,3,"Vie+"),(430,4,"Atq+"),(550,2,"Atq+"),(710,4,"Atq+"),(1020,2,"Vie+")]]
            self.Liste_panneaux = [Objets(1130, HH-90, "panneau", ("Il n'y avait rien...", "Poursuivons."))]
        elif level_num == 2:
            self.Liste_ennemis = [Ennemis(100+50*randint(1,20), HH-50, 20+5*((100+50*k)//100), 1) for k in range(12)]
            self.Liste_rochers = [Objets(200+80*randint(1,12), HH-70, "rocher") for k in range(5)]
            self.Liste_coffres = [Objets(x, HH-80, "coffre", NivEnv, Contenu) for (x,NivEnv,Contenu) in [(30,0,""),(160,3,"Vie+"),(430,4,"Atq+"),(710,4,"Atq+"),(1020,2,"Vie+")]]
            self.Liste_panneaux = [Objets(1130, HH-90, "panneau", ("C'etait le dernier niveau...", "Merci d'avoir joue !"))]

        self.Liste_buissons = [Objets(x, HH-30, "buisson", randint(0,1)) for x in [10,40,65,80,105,130,145,160,170,200,215,240,265,280,310,320,350,380,400]]
        self.Liste_feuilles = []
        
        # Player and game state
        self.Objets_recuperes = []
        self.Vie = 10
        self.Vie_max = 10
        self.Attaque = 5
        self.Direction = 1
        self.immunite = 0
        self.Tic = 0
        self.saut_en_cours = False
        self.mode_montee = False
        self.hauteur_initiale = 0
        self.delta_hauteur = 0
        self.appui_permis = False
        self.attack_en_cours = False
        self.attack_low_en_cours = False
        self.attack_timer = 0
    
    def update(self, dt):
        """Handles all game logic for one frame."""
        # State machine for game flow
        if self.game_state == "intro":
            self.update_intro()
            return
        if self.game_state == "panel":
            self.update_panel()
            return
        if self.game_state in ["game_over", "level_complete"]:
            # Could add logic to restart or go to next level
            return
        
        # --- Main Gameplay Update ("playing" state) ---
        self.Tic = (self.Tic + 1) % 30
        if self.attack_timer > 0:
            self.attack_timer -= 1
            if self.attack_timer == 0:
                self.attack_en_cours = False
                self.attack_low_en_cours = False
        
        # Player Movement
        chg = gint.keydown(gint.KEY_RIGHT) - gint.keydown(gint.KEY_LEFT)
        if chg != 0:
            self.xJ = max(5, min(self.xJ + 2 * chg, largeur_niveau - 15))
            self.Direction = chg
            # Collision with rocks
            for rocher in self.Liste_rochers:
                if -40 < rocher.x - self.xJ < 42 and rocher.y - self.yJ < 28:
                    self.xJ = rocher.x - 42 if self.Direction == 1 else rocher.x + 42
        
        # Player Actions (Attack/Jump)
        self.handle_input()
        
        # Update Jump Physics
        self.update_jump()
        
        # Update Entities
        for ennemi in self.Liste_ennemis:
            ennemi.update()
        for obj in self.Liste_coffres + self.Liste_feuilles:
            obj.update(self)

        # Collision Checks
        self.check_collisions()

        # Update timers
        if self.immunite > 0:
            self.immunite -= 1

        # Check Win/Loss Conditions
        if self.Vie <= 0:
            self.game_state = "game_over"
        if not self.Liste_ennemis and self.xJ > largeur_niveau - 30:
            self.Niveau += 1
            if self.Niveau < 3:
                self.load_level(self.Niveau)
            else:
                self.game_state = "level_complete" # Or game win

    def update_intro(self):
        """Handle the intro text sequence."""
        if self.input.interact: # Use engine's one-shot input
            self.current_intro_panel += 1
            if self.current_intro_panel >= len(self.intro_textes):
                self.game_state = "playing"
            else:
                self.active_panel = Objets(0, 0, "panneau", self.intro_textes[self.current_intro_panel])

    def update_panel(self):
        """Handle waiting for input when a panel is shown."""
        if self.input.interact:
            self.game_state = "playing"
            self.active_panel = None

    def handle_input(self):
        # Attack
        if gint.keydown(gint.KEY_SHIFT) and not self.attack_en_cours and not self.attack_low_en_cours:
            self.attack_timer = 12 # Corresponds to original Tic check
            if self.saut_en_cours and gint.keydown(gint.KEY_DOWN):
                self.attack_low_en_cours = True
                self.Tic = 0
                for ennemi in self.Liste_ennemis:
                    if -40 < ennemi.x - self.xJ < 42 and -10 <= ennemi.y - (self.yJ + 40) < 20:
                        ennemi.vie -= int(3/5 * self.Attaque)
                        ennemi.Humeur, ennemi.ticHumeur = "sad", 100
                        self.hauteur_initiale, self.delta_hauteur, self.mode_montee = 30, 30, True
                        if ennemi.vie <= 0:
                            ennemi.on_defeat(self)
                            self.Liste_ennemis.remove(ennemi)
            else:
                self.attack_en_cours = True
                self.Tic = 0
                for ennemi in self.Liste_ennemis:
                    if -15 + 45 * self.Direction < ennemi.x - self.xJ < 15 + 45 * self.Direction and -40 < ennemi.y - self.yJ < 20:
                        ennemi.x += 10 * self.Direction
                        ennemi.vie -= self.Attaque
                        ennemi.Humeur, ennemi.ticHumeur = "sad", 100
                        if ennemi.vie <= 0:
                            ennemi.on_defeat(self)
                            self.Liste_ennemis.remove(ennemi)
                for coffre in self.Liste_coffres:
                    if -15 + 45 * self.Direction < coffre.x - self.xJ < 15 + 45 * self.Direction:
                        coffre.NivEnvahissement = max(0, coffre.NivEnvahissement - 1)
        # Jump
        if gint.keydown(gint.KEY_ALPHA):
            if not self.saut_en_cours:
                self.saut_en_cours, self.mode_montee, self.appui_permis, self.hauteur_initiale = True, True, True, 0
            elif self.appui_permis and self.hauteur_initiale < 40:
                self.hauteur_initiale += 4
                self.delta_hauteur = self.hauteur_initiale
        elif self.saut_en_cours and self.appui_permis:
            self.appui_permis = False
            self.delta_hauteur = self.hauteur_initiale

    def update_jump(self):
        if not self.saut_en_cours and not any(-40 < r.x - self.xJ < 42 for r in self.Liste_rochers):
             self.saut_en_cours = True
             self.mode_montee = False
             self.appui_permis = False
             self.hauteur_initiale = (170 - self.yJ)//2
             self.delta_hauteur = 0.8
        
        if self.saut_en_cours:
            if self.appui_permis:
                self.yJ = 170 - 2 * self.hauteur_initiale + self.delta_hauteur
            else:
                if self.mode_montee:
                    if self.delta_hauteur > 6: self.delta_hauteur *= 0.85
                    else: self.mode_montee = False
                else:
                    self.delta_hauteur /= 0.85
                
                if self.delta_hauteur > 2 * self.hauteur_initiale:
                    self.saut_en_cours = False
                    self.yJ = 170
                else:
                    self.yJ = 170 - 2 * self.hauteur_initiale + self.delta_hauteur
            
            on_rock = False
            for rocher in self.Liste_rochers:
                if -40 < rocher.x - self.xJ < 42 and rocher.y > self.yJ and rocher.y - self.yJ < 42:
                    self.yJ = rocher.y - 30
                    self.saut_en_cours = False
                    on_rock = True
                    break
            if not on_rock and self.yJ > 170:
                 self.yJ = 170
                 self.saut_en_cours = False

    def check_collisions(self):
        # Panels
        for panneau in self.Liste_panneaux:
            if abs(self.xJ - panneau.x) < 5 and not panneau.lu:
                self.game_state = "panel"
                self.active_panel = panneau
                panneau.lu = True
                break
        
        # Leaves
        for feuille in self.Liste_feuilles:
            if -40 < feuille.x - self.xJ < 20 and feuille.y - self.yJ < 40:
                self.Liste_feuilles.remove(feuille)
                self.Vie = min(self.Vie_max, self.Vie + 2)
                break
        
        # Enemies
        if self.immunite < 1:
            for ennemi in self.Liste_ennemis:
                if -40 < ennemi.x - self.xJ < 42 and ennemi.y - self.yJ < 40:
                    self.Vie -= ennemi.atq
                    ennemi.Humeur, ennemi.ticHumeur = "happy", 100
                    self.immunite = 50
                    recoil_dir = 1 if ennemi.x < self.xJ else -1
                    self.xJ += 6 * recoil_dir
                    # Check if pushed into rock
                    for rocher in self.Liste_rochers:
                        if -40 < rocher.x - self.xJ < 42 and rocher.y - self.yJ < 28:
                            self.xJ = rocher.x + 42 if recoil_dir == -1 else rocher.x - 42
                    break
    
    def draw(self, frame_time_ms):
        """Renders the entire game world."""
        gint.dclear(clr_fond)

        if self.game_state == "intro" or self.game_state == "panel":
            if self.active_panel:
                self.active_panel.draw_panel_content()
            return

        # --- Gameplay Drawing ---
        self.draw_arriere_plan()
        self.draw_arbres()
        
        # Draw all objects
        all_objects = self.Liste_coffres + self.Liste_rochers + self.Liste_panneaux + self.Liste_feuilles
        for obj in sorted(all_objects, key=lambda o: o.y):
             if -LL < obj.x - self.xJ < LL:
                obj.draw(self)

        for ennemi in self.Liste_ennemis:
            if -LL - 30 < ennemi.x - self.xJ < LL + 30:
                ennemi.draw(self)

        self.draw_joueur()
        self.draw_avant_plan()
        self.draw_vie()

        # Game Over / Win messages
        if self.game_state == "game_over":
            gint.dtext(LL//2 - 40, HH//2, gint.C_RED, "GAME OVER")
        elif self.game_state == "level_complete":
            gint.dtext(LL//2 - 50, HH//2, gint.C_GREEN, "LEVEL COMPLETE")


    def draw_arriere_plan(self):
        coeff = 0.5
        gint.dimage(0, 161, sentier)
        if self.xJ < LL // 2:
            gint.dsubimage(0, 0, fond4, 0, 0, 396, 161)
        elif self.xJ > largeur_niveau - LL // 2:
            gint.dsubimage(0, 0, fond4, 792 - 396, 0, 396, 161)
        else:
            gint.dsubimage(0, 0, fond4, int(coeff * (self.xJ - LL // 2)), 0, 396, 161)

    def draw_arbres(self):
        coeff = 1
        for posX in Arbres:
            if -LL * 2 < coeff * (2 * posX + LL // 2 - self.xJ) < LL * 2:
                if self.xJ < LL // 2:
                    gint.dimage(int(coeff * 2 * posX), 0, bouleau)
                elif self.xJ > largeur_niveau - LL // 2:
                    gint.dimage(int(coeff * (2 * posX + LL - largeur_niveau)), 0, bouleau)
                else:
                    gint.dimage(int(coeff * (2 * posX + LL // 2 - self.xJ)), 0, bouleau)

    def draw_avant_plan(self):
        coeff = 4
        h, l = 30, 30
        for buisson in self.Liste_buissons:
            if self.xJ < LL // 2:
                posX = coeff * 2 * buisson.x
            elif self.xJ > largeur_niveau - LL // 2:
                posX = coeff * (LL - largeur_niveau + 2 * buisson.x)
            else:
                posX = coeff * (LL // 2 + (2 * buisson.x - self.xJ))
            gint.dsubimage(posX, HH - 30, buisson.sprite, 1 + 31 * buisson.NivEnvahissement, 1, l, h)

    def draw_joueur(self):
        dX, dY, l, h = 1, 44, 42, 42 # Default to idle
        
        if self.attack_low_en_cours:
            dX, dY, l, h = 1 + 43 * (self.Tic // 2), 259, 42, 60
        elif self.attack_en_cours:
            dX, dY, l, h = 1 + 61 * ((self.Tic // 2) % 3), 130 + 43 * ((self.Tic // 2) > 2), 60, 42
        elif self.saut_en_cours:
            dX, dY, l, h = 1 + 43 * (self.Tic // 5), 216, 42, 42
        elif gint.keydown(gint.KEY_LEFT) or gint.keydown(gint.KEY_RIGHT): # "move" action
            dX, dY, l, h = 1 + 43 * (self.Tic // 5), 1, 42, 42
        else: # idle
            dX, dY, l, h = 1 + 43 * (self.Tic // 5), 44, 42, 42

        if self.immunite > 0 and (self.Tic // 5) % 3 == 0:
            dX, dY, l, h = 87, 87, 42, 42
        
        if self.xJ < LL // 2:
            posX = self.xJ
        elif self.xJ > largeur_niveau - LL // 2:
            posX = LL - largeur_niveau + self.xJ
        else:
            posX = LL // 2
        
        offset_x = -20 * (self.attack_en_cours and self.Direction == -1 and not (self.immunite > 0 and (self.Tic // 5) % 3 == 0))
        gint.dsubimage(posX + offset_x, int(self.yJ), corbeau_walk, dX, dY + 321 * (self.Direction == -1), l, h)

    def draw_vie(self):
        for i in range(2, self.Vie_max + 1, 2):
            if i <= self.Vie:
                gint.dsubimage(10 * i, 20, points_de_vie, 1, 22, 20, 20)
            elif i == self.Vie + 1:
                gint.dsubimage(10 * i, 20, points_de_vie, 22, 22, 20, 20)
            else:
                gint.dsubimage(10 * i, 20, points_de_vie, 43, 22, 20, 20)
        
        for i in range(self.Objets_recuperes.count("Atq+")):
            gint.dsubimage(20 + 25 * i, 45, objets_precieux, 22, 1, 20, 20)
        for i in range(self.Objets_recuperes.count("CleB")):
            gint.dsubimage(20 + 25 * i, 65, objets_precieux, 43, 1, 20, 20)
        for i in range(self.Objets_recuperes.count("Vit+")):
            gint.dsubimage(20 + 25 * i, 85, objets_precieux, 64, 1, 20, 20)

# --- Game Entry Point ---

def main():
    """Initializes and runs the game."""
    game = Game()
    game.start(PromenadScene)

