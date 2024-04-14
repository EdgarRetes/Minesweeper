import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # if the set of cells is equal to the count we know that they are mines
        if len(self.cells) == self.count and self.count != 0:
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # if the set of cells is equal to 0 we know that none of them are mines
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # If a mine is in the set then remove the cell from self.cells and decrease the count
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # If a cell is in the set and is marked as safe remove it from the set of cells
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # Mark the cell as a move that has been made
        self.moves_made.add(cell)

        # Mark the cell as safe
        self.mark_safe(cell)

        # Add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
        cells_set = set()

        # Loop to get the neighbor cells to add them into the cells_set if they exist in the board
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                new_cell = (i, j)
                if new_cell in self.mines:
                    count -= 1
                if 0 <= i < self.height and 0 <= j < self.width and new_cell not in self.safes and new_cell not in self.mines:
                    # Just add the cell if it passes all the cases
                    cells_set.add(new_cell)

        new_sentence = Sentence(cells_set, count)

        # Add the sentence to knowledge
        self.knowledge.append(new_sentence)

        while True:

            new_info = False

            # mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
                
            safes = set()
            mines = set()

            # add the safes and miens to the sets
            for sentence in self.knowledge:
                mines = mines.union(sentence.known_mines())
                safes = safes.union(sentence.known_safes())

            # If there are mine cells mark them as safe
            if mines:
                new_info = True
                for mine in mines:
                    self.mark_mine(mine)

            # If there are safe cells mark them as safe
            if safes:
                new_info = True
                for safe in safes:
                    self.mark_safe(safe)

            # Remove empty sets of cells
            for sentence in self.knowledge:
                if len(sentence.cells) == 0:
                    self.knowledge.remove(sentence)
                
            # add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
                    
            # If set1 is a subset of set2, then a new sentence is created given by set2 - set1 = count2 - count1
            new_knowledge = []
            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:
                    if sentence1.cells.issubset(sentence2.cells) and sentence1.count <= sentence2.count and sentence1 != sentence2:
                        new_cells_set = sentence2.cells - sentence1.cells
                        new_count = sentence2.count - sentence1.count
                        inferred_sentence = Sentence(new_cells_set, new_count)
                        if inferred_sentence not in self.knowledge:
                            new_info = True
                            # Remove any newly inferred mines or safes from existing sentences
                            new_knowledge.append(inferred_sentence)
        
            # Extend the knowledge after completing iteration:
            self.knowledge.extend(new_knowledge)

            if not new_info:
                break

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        available = []

        # Get the cells available
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    available.append((i, j))

        if len(available) != 0:
            return random.choice(available)
        
        return None

