from hacker_game_support import *
import tkinter as tk
import random
from PIL import Image, ImageTk
from tkinter import messagebox, filedialog

MINUTE_TO_SECOND = 60
MIN_XCOORD = 0
MIN_YCOORD = 0
YCOORD_BOUND = 1
X_ROTATE = 1
FILE_INDEX = -1
BAR_RATIO = 3

class Entity(object):
    """An abstract class used to represent any element that can appear on the 
    game's grid."""

    def display(self) -> str:
        """
        (str): Return character used to represent the entity in text-based grid
        """
        raise NotImplementedError() 
    
    def __repr__(self) -> str:
        """(str): Return a representation of this Entity."""
        return f'{self.__class__.__name__}()'


class Player(Entity):
    """A subclass of Entity representing a Player within the game."""

    def display(self) -> str:
        """(str): Return the character representing a player."""
        return PLAYER


class Destroyable(Entity):
    """A subclass of Entity representing a Destroyable within the game. It can 
    be destroyed by the player but not collected."""

    def display(self) -> str:
        """(str): Return the character representing a destroyable."""
        return DESTROYABLE


class Collectable(Entity):
    """A subclass of Entity representing a Collectable within the game. It can 
    be destroyed or collected by the player."""

    def display(self) -> str:
        """(str): Return the character representing a collectable."""
        return COLLECTABLE


class Blocker(Entity):
    """A subclass of Entity representing a Blocker within the game. It cannot be
    destoryed or collected by the player."""

    def display(self) -> str:
        """(str): Return the character representing a blocker."""
        return BLOCKER


class Grid:
    """A class representing the 2D grid of entities. The top left is (0, 0)."""

    def __init__(self, size: int) -> None:
        """Constructs a grid with a size representing number of rows (columns).

        Parameters:
            size (int): The size representing number of rows (columns) in the grid
        """
        self._size = size
        self._entities = {}
    
    def get_size(self) -> int:
        """(int): Return the size of the grid."""
        return self._size
    
    def add_entity(self, position: Position, entity: Entity) -> None:
        """Add a given entity into the grid at a specified position if it's valid
        
        Parameters:
            position (Position): The specified position to be added to in the grid
            entity (Entity): The entity to be added
        """
        if self.in_bounds(position):
            self._entities[position] = entity
    
    def get_entities(self) -> Dict[Position, Entity]:
        """(dict): Return the dictionary containing grid entities."""
        entities = {}

        for position, entity in list(self._entities.items()):
            entities[position] = entity
        return entities
    
    def get_entity(self, position: Position) -> Optional[Entity]: 
        """Return a entity from the grid at a specific position or None if the 
        position does not have a mapped entity.
        
        Parameters:
            positon (Position): The specific position to get entity.
        
        Returns:
            (Entity): Return a entity at a specific position.
        """
        if position in self._entities:
            return self._entities[position]
        else:
            return None
    
    def remove_entity(self, position: Position) -> None:
        """Remove an entity from the grid at a specified position."""
        del self._entities[position]
    
    def serialise(self) -> Dict[Tuple[int, int], str]:
        """Convert dictionary of Position and Entities into a simplified, 
        serialised dictionary mapping tuples to characters. 

        Returns:
            (dict): Return a serialised mapping.
        """
        serial_entities = {}

        for position, entity in list(self._entities.items()):
            coord_x = position.get_x()
            coord_y = position.get_y()
            serial_entities[(coord_x, coord_y)] = entity.display()

        return serial_entities
    
    def in_bounds(self, position: Position) -> bool:
        """(bool): Return a boolean based on whether the position is valid in
         terms of the dimensions of the grid.
        
        Parameters:
            positon (Position): The specific position to check the bounds.
        """
        coordx = position.get_x()
        coordy = position.get_y()
        return MIN_XCOORD <= coordx and coordx < self._size \
            and YCOORD_BOUND <= coordy and coordy < self._size
        

    def set_entities(self, entities: dict) -> None:
        """Set the position entity mapping according to the given entities.
        
        Parameters:
            entities (dict): The position entity mapping to be set to.
        """
        self._entities = entities

    def __repr__(self) -> str:
        """(str): Return a representation of this Grid."""
        return f'Grid({self.get_size()})'


class Game:
    """
    A class handles the logic to control actions of the entities in the grid.
    """

    def __init__(self, size: int) -> None:
        """Constructs a game with a grid size.

        Parameters:
            size (int): The size representing number of rows (columns) in game
        """
        self._size = size
        self._grid = Grid(self._size)
        self._won = False

        self._num_collected = 0
        self._num_destroyed = 0
        self._total_shots = 0
    
    def get_grid(self) -> Grid: 
        """(Grid): Return the instance of the grid held by the game."""
        return self._grid

    def get_player_position(self) -> Position:
        """(Position): Return the position of the player in the grid."""
        centered_xcoord = self._size // 2 
        return Position(centered_xcoord, MIN_YCOORD)
    
    def get_num_collected(self) -> int:
        """(int): Return the total of Collectables acquired."""
        return self._num_collected

    def get_num_destroyed(self) -> int:
        """(int): Return the total of Destroyables removed with a shot."""
        return self._num_destroyed

    def get_total_shots(self) -> int:
        """(int): Return the total of shots taken."""
        return self._total_shots
    
    def rotate_grid(self, direction: str) -> None:
        """Rotate the positions of the entities within the grid depending on 
        the direction they are being rotated.

        Parameters:
            direction(str): The direction positions of entities being rotated.
        """
        direction = direction.upper()
        rotate_entities = {}
        change = ROTATIONS[DIRECTIONS.index(direction)]

        if direction in DIRECTIONS:
            for position, entity in self.get_grid().get_entities().items():

                #Rotate positions and Player position doesn't change.
                if entity.display() == PLAYER:
                    new_position = position
                else:
                    new_position = position.add(Position(change[0], change[1]))
                
                #Reset position if out of bound
                coordx = new_position.get_x()
                coordy = new_position.get_y()
                if not self._grid.in_bounds(new_position):
                    if coordx >= self._size:
                        coordx = MIN_XCOORD
                    elif coordx < MIN_XCOORD:
                        coordx = self._size - X_ROTATE

                #Update grid after rotation
                new_entity = self._create_entity(entity.display())
                rotate_entities[Position(coordx, coordy)] = new_entity

            self._grid.set_entities(rotate_entities)

    def _create_entity(self, display: str) -> Entity:
        """Uses a display character to create an Entity.
        
        Parameters:
            display (str): The display character of entity.
        
        Returns:
            (Entity): The entity to be created.
        """
        if display == COLLECTABLE:
            return Collectable()
        elif display == DESTROYABLE:
            return Destroyable()
        elif display == BLOCKER:
            return Blocker()
        else:
            raise NotImplementedError()

    def generate_entities(self) -> None:
        """
        Method given to the students to generate a random amount of entities to
        add into the game after each step
        """
        # Generate amount
        entity_count = random.randint(0, self.get_grid().get_size() - 3)
        entities = random.choices(ENTITY_TYPES, k=entity_count)

        # Blocker in a 1 in 4 chance
        blocker = random.randint(1, 4) % 4 == 0

        # UNCOMMENT THIS FOR TASK 3 (CSSE7030)
        # bomb = False
        # if not blocker:
        #     bomb = random.randint(1, 4) % 4 == 0

        total_count = entity_count
        if blocker:
            total_count += 1
            entities.append(BLOCKER)

        # UNCOMMENT THIS FOR TASK 3 (CSSE7030)
        # if bomb:
        #     total_count += 1
        #     entities.append(BOMB)

        entity_index = random.sample(range(self.get_grid().get_size()),
                                     total_count)

        # Add entities into grid
        for pos, entity in zip(entity_index, entities):
            position = Position(pos, self.get_grid().get_size() - 1)
            #'Game' object has no attribute '_create_entity'
            new_entity = self._create_entity(entity)
            self.get_grid().add_entity(position, new_entity)
            
    def step(self) -> None:
        """Moves all entities on the board by an offset of (0, -1)."""
        step_entities = {}

        #Update positions of entities after step
        for position, entity in self._grid.get_entities().items():
            new_position = position.add(Position(MOVE[0], MOVE[1]))
            if self._grid.in_bounds(new_position):
                step_entities[new_position] = self._create_entity(entity.display())

        self._grid.set_entities(step_entities)
        self.generate_entities()

    def fire(self, shot_type: str) -> None:
        """Handles firing/collecting actions of player towards an entity.
        
        Parameters:
            shot_type (str): A collect or destroy shot has been fired.
        """
        self._total_shots += 1

        #Find the position and entity that will be fired
        fire_xcoord = self.get_player_position().get_x()
        positions = list(self._grid.serialise().keys())
        fire_ycoords = [coordy for coordx, coordy in positions \
            if coordx == fire_xcoord]

        if fire_ycoords != []:
            min_ycoord_entity = min(fire_ycoords)
            del_position = Position(fire_xcoord, min_ycoord_entity)
            entity_display = self._grid.get_entities()[del_position].display()

            #Collectable will be fired
            if entity_display == COLLECTABLE:
                if shot_type == COLLECT:
                    self._num_collected += 1
                    self.get_grid().remove_entity(del_position)
                if shot_type == DESTROY:
                    self._num_destroyed += 1
                    self.get_grid().remove_entity(del_position)

            #Destroyable will be fired
            if shot_type == DESTROY and entity_display == DESTROYABLE:
                self._num_destroyed += 1
                self.get_grid().remove_entity(del_position)

    def has_won(self) -> bool:
        """(bool): Return True if the player has won the game."""
        return self.get_num_collected() >= COLLECTION_TARGET
    
    def has_lost(self) -> bool:
        """(bool): Returns True if the game is lost."""
        entities = self.get_grid().serialise()
        destroy_ycoord = [coordy for (coordx, coordy), entity in entities.items()
            if entity == DESTROYABLE]

        for ycoord in destroy_ycoord:
            if ycoord == YCOORD_BOUND:
                return True
        return False


class AbstractField(tk.Canvas):
    """An abstract view class provides base functionality for other view classes.
    Can be thought of as a grid with a set number of rows and columns."""
    
    def __init__(self, master, rows, cols, width, height, **kwargs) -> None:
        """Constructs a AbstractField as grid with number of rows and columns.

        Parameters:
            master (tkinter): The parameter inherit from tkinter.
            rows (int): The rows of the grid in the field.
            cols (int): The columns of the grid in the field.
            width (int): The width of the field.
            height (int): The height of the field.
        """
        super().__init__(master, width=width, height=height, bg=FIELD_COLOUR)
        self._width = width
        self._height = height
        self._bwidth = width / cols
        self._bheight = height / rows
    
    def get_bbox(self, position) -> Tuple[int, int, int, int]:
        """Returns the bounding box for the position.
        
        Parameters:
            position (Position): A given position to find bounding box.
        
        Returns:
            (tuple): The pixel positions of the edges of the shape.
        """
        x_min = position.get_x()*self._bwidth
        y_min = position.get_y()*self._bheight
        x_max = x_min + self._bwidth
        y_max = y_min + self._bheight
        return (x_min, y_min, x_max, y_max)

    def pixel_to_position(self, pixel) -> Position:
        """Converts the (x, y) pixel position to a position.
        
        Parameters:
            pixel (tuple): The pixel position in graphics units.
        
        Returns:
            (Position): Return the position in 2D grid of the pixel position.
        """
        xpixel, ypixel = pixel
        coordx = xpixel // self._bwidth
        coordy = ypixel // self._bheight
        return Position(coordx, coordy)

    def get_position_center(self, position) -> Tuple[float, float]:
        """Gets graphics coordinates for the center of cell at a given position.
        
        Parameters:
            position (Position): The position of the cell in 2D grid.
        
        Returns:
            (tuple): Return the graphics coordinates for the center of cell at 
                    the position
        """
        col = position.get_x()
        row = position.get_y()
        x_mid = col*self._bwidth + self._bwidth/2
        y_mid = row*self._bheight + self._bheight/2
        return (x_mid, y_mid)
    
    def annotate_position(self, position, text) -> None:
        """Annotates the center of the cell at the given position with the 
        provided text.

        Parameters:
            position (Position): The position of the cell in 2D grid.
            text (str): The text will be annotated.
        """
        x_mid, y_mid = self.get_position_center(position)
        self.create_text(x_mid, y_mid, text=text, fill="white")


class GameField(AbstractField):
    """A class which is a visual representation of the game grid."""
    def __init__(self, master, size, width, height, **kwargs) -> None:
        """Constructs a visual representation of the game grid.

        Parameters:
            master (tkinter): The parameter inherit from tkinter.
            size (int): The columns and rows of the game grid.
            width (int): The width of the game field.
            height (int): The height of the game field.
        """
        super().__init__(master, rows=size, cols=size, width=width, height=height)
        self._size = size

    def draw_grid(self, entities) -> None:
        """Draws the entities in the game grid at their given position using
         a coloured rectangle with superimposed text identifying the entity.
         
        Parameters:
            entities (dict): A mapping of positions and entities in the grid.
        """
        for position, entity in list(entities.items()):
            color = COLOURS[entity.display()]
            bbox = self.get_bbox(position)
            center_position = self.get_position_center(position)

            self.create_rectangle(bbox, fill=color)
            self.create_text(center_position, text=entity.display(), fill="white")
    
    def draw_player_area(self) -> None:
        """Draws the grey area a player is placed on."""
        player_height = self._height / self._size
        self.create_rectangle(MIN_XCOORD, MIN_YCOORD, self._width, player_height,
                             fill=PLAYER_AREA)

        
class ScoreBar(AbstractField):
    """A class which is a visual representation of shot statistics."""
    def __init__(self, master, rows, **kwargs) -> None:
        """Constructs a visual representation of the shot statistics.

        Parameters:
            master (tkinter): The parameter inherit from tkinter.
            rows (int): The rows of the score bar.
        """
        super().__init__(master, rows=rows, cols=2, width=SCORE_WIDTH, height=MAP_HEIGHT)
        self.config(bg=SCORE_COLOUR)
        self._cols = 2
        self._width = SCORE_WIDTH

        self._num_xcoord = 1
        self._destroy_ycoord = 2
        
    def draw(self, collect_num, destroy_num) -> None:
        """Draw the number of collected entity and destroyed entity in score bar.
        
        Parameters:
        collect_num (int): The number of collectables acquired.
        destroy_num (int): The number of destroyables shot.
        """
        score_position = (self._width/self._cols, self._bheight/2)
        self.create_text(score_position, font=('Arial', 22), text="Score", 
                        fill="white")

        #Collect and Destroy Positions
        collect_pos = Position(MIN_XCOORD, YCOORD_BOUND)
        cnum_pos = Position(self._num_xcoord,YCOORD_BOUND)
        destroy_pos = Position(MIN_XCOORD, self._destroy_ycoord)
        dnum_pos = Position(self._num_xcoord,self._destroy_ycoord)

        #Draw Collect and Destroy Data
        collect_position = self.get_position_center(collect_pos)
        destroy_position = self.get_position_center(destroy_pos)
        self.create_text(collect_position, text="Collected", fill="white")
        self.create_text(destroy_position, text="Destroyed", fill="white")

        cnum_position = self.get_position_center(cnum_pos)
        dnum_position = self.get_position_center(dnum_pos)
        self.create_text(cnum_position, text=f"{collect_num}", fill="white")
        self.create_text(dnum_position, text=f"{destroy_num}", fill="white")

class ImageGameField(GameField):
    """A class using images to display each square in game field."""
    def __init__(self, master, size, width, height, **kwargs) -> None:
        """Constructs a representation with images of the game grid.

        Parameters:
            master (tkinter): The parameter inherit from tkinter.
            size (int): The columns and rows of the game grid.
            width (int): The width of the game field.
            height (int): The height of the game field.
        """
        super().__init__(master, size, width, height, **kwargs)
        self._box_size = int(width /size)
    
        #Import Images of Entities
        self._player = ImageTk.PhotoImage(Image.open("images/P.png").resize((
            self._box_size, self._box_size)))
        self._blocker = ImageTk.PhotoImage(Image.open("images/B.png").resize((
            self._box_size, self._box_size)))
        self._collectable = ImageTk.PhotoImage(Image.open("images/C.png").resize((
            self._box_size, self._box_size)))
        self._destroyable = ImageTk.PhotoImage(Image.open("images/D.png").resize((
            self._box_size, self._box_size)))

    def draw_grid(self, entities: dict) -> None:
        """Draws the entities in the game grid at their given position using
         images identifying the entity.
         
         Parameters:
            entities (dict): A mapping of positions and entities in the grid.
        """
        self.create_rectangle(MIN_XCOORD, self._box_size, MAP_WIDTH, MAP_HEIGHT,\
            fill=FIELD_COLOUR)

        #Draw Images of Entities
        for position, entity in entities.items():
            coordx, coordy = self.get_position_center(position)
            if entity.display() == PLAYER:
                self.create_image(coordx, coordy, image=self._player)
            if entity.display() == BLOCKER:
                self.create_image(coordx, coordy, image=self._blocker)
            if entity.display() == COLLECTABLE:
                self.create_image(coordx, coordy, image=self._collectable)
            if entity.display() == DESTROYABLE:
                self.create_image(coordx, coordy, image=self._destroyable)

class StatusBar(tk.Frame):
    """A class representing the status of the game, including total shots, timer
    and a pause button."""
    def __init__(self, master, **kwargs) -> None:
        """Constructs a representation of the status of the game.

        Parameters:
            master (tk.Frame): The parameter inherit from tkinter.
        """
        super().__init__(master, **kwargs)
        
        #Total shots
        frame_shots = tk.Frame(master)
        frame_shots.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        self._shot = tk.Label(frame_shots, text="Total Shots")
        self._shot.pack(side=tk.TOP)
        self._shot_num = tk.Label(frame_shots, text="0")
        self._shot_num.pack(side=tk.TOP)

        #Timer
        frame_timer = tk.Frame(master)
        frame_timer.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        self._timer = tk.Label(frame_timer, text="Timer")
        self._timer.pack(side=tk.TOP)
        self._time = tk.Label(frame_timer, text="0m 0s")
        self._time.pack(side=tk.TOP)

        #Pause Game
        press_frame = tk.Frame(master)
        press_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        self._press = tk.Button(press_frame, text="Pause")
        self._press.pack(side=tk.LEFT, expand=tk.TRUE)
    
class HackerController(object):
    """A class which is the controller for the Hacker game."""
    def __init__(self, master, size) -> None:
        """Constructs a controller of the Hacker game.

        Parameters:
            master (tkinter): The parameter inherit from tkinter.
        """
        self._master = master
        self._size = size
        self._game = Game(size)
        
        #HACKER Title
        self._title = tk.Frame(self._master)
        self._title.config(width=MAP_WIDTH + SCORE_WIDTH, 
                            height=BAR_HEIGHT/BAR_RATIO)
        self._title.pack(side=tk.TOP)
        self._title.pack_propagate(0)
        self._label = tk.Label(self._title, text=TITLE, bg=TITLE_BG,
                                font=TITLE_FONT, fg="white")
        self._label.pack(fill=tk.X)

        #Game field and Score bar
        self._game_score = tk.Frame(self._master)
        self._game_score.pack(side=tk.TOP)
        self._score_bar = ScoreBar(self._game_score, self._size, bg=SCORE_COLOUR)
        self._score_bar.pack(side=tk.RIGHT)
        self.game_field()
        self.draw(self._game)
        self._score_bar.draw(self._game.get_num_collected(), \
            self._game.get_num_destroyed())

        self._master.bind("<Key>", self.handle_keypress)
        self._master.after(2000, self.step)

    def game_field(self) -> None:
        """Construct the game field of the game."""
        self._game_field = GameField(self._game_score, self._size, MAP_WIDTH,
                                     MAP_HEIGHT, bg=FIELD_COLOUR)
        self._game_field.pack(side=tk.LEFT)
    
    def handle_keypress(self, event) -> None:
        """Handle error checking, event calling and update both the model and
        the view accordingly.
        
        Parameters:
            event (tk.Event): The user press event during the game.
        """
        if event.keysym.upper() in DIRECTIONS:
            self.handle_rotate(event.keysym.upper())

        if event.keysym.upper() in SHOT_TYPES:
            self.handle_fire(event.keysym.upper())

        self.draw(self._game)

    def draw(self, game) -> None:
        """Clears and redraws the view based on the current game state.
        
        Parameters:
            game (Game): The current game played by the player.
        """
        entities = game.get_grid().get_entities()
        entities[game.get_player_position()] = Player()

        self._game_field.delete(tk.ALL)
        self._score_bar.delete(tk.ALL)

        #Redraw the view
        self._game_field.create_rectangle(MIN_XCOORD, MIN_YCOORD, MAP_WIDTH, \
            MAP_HEIGHT, fill=FIELD_COLOUR)
        self._game_field.draw_player_area()
        self._game_field.draw_grid(entities)
        self._score_bar.draw(game.get_num_collected(), game.get_num_destroyed())
    
    def handle_rotate(self, direction) -> None:
        """Handles rotation of the entities and redrawing the game.
        
        Parameters:
            direction(str): The direction positions of entities being rotated.
        """
        self._game.rotate_grid(direction)

    def handle_fire(self, shot_type) -> None:
        """Handles the firing of the specified shot type and redraw the game.
        
        Parameters:
            shot_type (str): A collect or destroy shot has been fired.
        """
        self._game.fire(shot_type)

    def step(self) -> None:
        """Triggers the step for the game and updates view every 2 seconds"""

        #Check Game Over
        if self._game.has_lost() or self._game.has_won():
            if self._game.has_lost():
                messagebox.showinfo("Game Over", "You lost!")
            if self._game.has_won():
                messagebox.showinfo("Game Over", "You won!")
            exit(0)

        self._game.step()
        self.draw(self._game)
        self._master.after(2000, self.step)

class AdvancedHackerController(HackerController):
    """A interface class that extends the functionality of HackerController"""
    def __init__(self, master, size) -> None: 
        """Constructs an advanced controller of the Hacker game.

        Parameters:
            master (tkinter): The parameter inherit from tkinter.
        """
        super().__init__(master, size)
        self._pause = False
        self._time_count = -1

        #Status Bar
        self._status_bar = tk.Frame(self._master)
        self._status_bar.config(width=MAP_WIDTH + SCORE_WIDTH, 
                                height=BAR_HEIGHT/BAR_RATIO)
        self._status_bar.pack(side=tk.TOP)
        self._status_bar.pack_propagate(0)
        self._status = StatusBar(self._status_bar)
        self._status.pack()
        self._status._press.config(command=self.pause)
        self.status_step()

        #File Menu
        self._filename = None
        self._entity_line = 0
        self._time_line = 1
        self._shot_line = 2
        self._pause_line = 3
        self._collect_line = 4
        self._destroy_line = 5
        self.file()

    def game_field(self) -> None:
        """Construct the game field with images of the game."""
        self._game_field = ImageGameField(self._game_score, self._size, 
                                          MAP_WIDTH, MAP_HEIGHT, bg=FIELD_COLOUR)
        self._game_field.pack(side=tk.LEFT)

    def pause(self) -> None:
        """Pause the game when user press Pause button"""
        if self._pause:
            self._status._press.config(text="Pause")
        else:
            self._status._press.config(text="Play")
        self._pause = not self._pause 
    
    def step(self) -> None:
        """Triggers the step for the game and updates view every 2 seconds
        Pause the game when the game is over."""
        if not self._pause:
            if self._game.has_lost() or self._game.has_won():
                self.pause()
            super().step()
        else:
            self._master.after(2000, self.step)
    
    def file(self) -> None:
        """Add a file menu with new game, save game, load game, quit options"""
        menubar = tk.Menu(self._master)
        self._master.config(menu=menubar)
        filemenu = tk.Menu(menubar)

        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New Game", command=self.new_game)
        filemenu.add_command(label="Save Game", command=self.save_game)
        filemenu.add_command(label="Load Game", command=self.load_game)
        filemenu.add_command(label="Quit", command=self.quit_game)

    def status_step(self) -> None:
        """Triggers the step for the game and updates timer every 1 seconds"""
        if not self._pause:
            self._time_count += 1
            minute, second = time_format(self._time_count)
            self._status._time.config(text=f'{minute}m {second}s')

        self._master.after(1000, self.status_step)    

    def handle_fire(self, shot_type) -> None:
        """Handles the firing of the specified shot type, update total shots
        and redraw the game.
        
        Parameters:
            shot_type (str): A collect or destroy shot has been fired.
        """
        super().handle_fire(shot_type)
        self._status._shot_num.config(text=f'{self._game.get_total_shots()}')
    
    def new_game(self) -> None:
        """Start a new game with new grid when user choose to."""
        if self._pause:
            self.pause()

        self._game = Game(self._size)
        self.draw(self._game)
        self._status._shot_num.config(text=f'{self._game.get_total_shots()}')
        self._status._time.config(text="0m 0s")
        self._time_count = 0

    def save_game(self) -> None:
        """Prompt the user for the location to save their file and save necessary
        game data."""
        #Check if user pause the game before save it
        if self._pause:
            pause_before_save = True
        else:
            pause_before_save = False
            self.pause()

        if self._filename is None:
            filename = filedialog.asksaveasfilename()
            if filename:
                self._filename = filename

        #Save the necessary game information in the location chosen by user
        if self._filename:
            with open(f'{self._filename}', 'w') as file:
                file.write(str(self._game.get_grid().get_entities()))
                file.write("\n")
                file.write(str(self._time_count))
                file.write("\n")
                file.write(str(self._game.get_total_shots()))
                file.write("\n")
                file.write(str(pause_before_save))
                file.write("\n")
                file.write(str(self._game.get_num_collected()))
                file.write("\n")
                file.write(str(self._game.get_num_destroyed()))

    def load_game(self) -> None:
        """Prompt the user for the location of the file to load a game and load
        the game described in that file."""
        if not self._pause:
            self.pause()

        #Read saved game information
        filename = filedialog.askopenfilename()
        if filename:
            self._filename = filename
            with open(f'{self._filename}', 'r') as file:
                saveinfo = file.readlines()
                save_entities = eval(saveinfo[self._entity_line][:FILE_INDEX])
                save_time = int(saveinfo[self._time_line][:FILE_INDEX])
                save_shots = int(saveinfo[self._shot_line][:FILE_INDEX])
                pause_before_save = saveinfo[self._pause_line][:FILE_INDEX]
                save_collect = int(saveinfo[self._collect_line][:FILE_INDEX])
                save_destroy = int(saveinfo[self._destroy_line])

        #Start the game according to saved information        
        self._game = Game(self._size)
        self._game.get_grid().set_entities(save_entities)
        self._game._num_collected = save_collect
        self._game._num_destroyed = save_destroy
        self._game._total_shots = save_shots
        self._time_count = save_time

        minute, second = time_format(save_time)
        self.draw(self._game)
        self._status._shot_num.config(text=save_shots)
        self._status._time.config(text=f"{minute}m {second}s")

        #Set game pause state according to saved pause condition
        if pause_before_save == "False":
            self.pause()

    def quit_game(self) -> None:
        """Prompt the player via a messagebox to ask whether they are sure they 
        want to quit. Quit the game if they say yes."""
        #Check if user pause game before quit
        pause_before_quit = None
        if self._pause: 
            pause_before_quit = True
        else:
            pause_before_quit = False
            self.pause()

        message = messagebox.askyesno("Quit", "Are you sure you want to quit?")
        if message:
            exit(0)

        #Continue the previous game state
        if not pause_before_quit:
            self.pause()


def time_format(time_count) -> Tuple[int, int]:
    """Change time count to minute, second format.
    
    Parameters:
        time_count (int): The time count of the game.
    
    Returns:
        (tuple): The minutes and seconds of the game time.
    """
    minute = time_count // MINUTE_TO_SECOND
    second = time_count % MINUTE_TO_SECOND
    return minute, second

def start_game(root, TASK=TASK):
    controller = HackerController

    if TASK != 1:
        controller = AdvancedHackerController

    app = controller(root, GRID_SIZE)
    return app


def main():
    root = tk.Tk()
    root.title(TITLE)
    app = start_game(root)
    root.mainloop()


if __name__ == '__main__':
    main()
