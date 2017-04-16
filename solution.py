ASSIGNMENTS = []

ROWS = 'ABCDEFGHI'
cols = '123456789'

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

boxes = cross(ROWS, cols)
row_units = [cross(r, cols) for r in ROWS]
column_units = [cross(ROWS, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]

"""
The approach for solving diagonal sudoku involves adding the two diagonals to the list of
units that are already being checked when the puzzle is being solved. We create two arrays
in a list that represents the two diagonals and add that to the unit lists.
"""
diag1 = []
diag2 = []
for ch in range(0, 9):
    diag1.append(ROWS[ch] + cols[ch])
    diag2.append(ROWS[ch] + cols[len(cols)-ch-1])
diagonal_units = [diag1, diag2]

# In addition to row, column and squares, diagonals have also been added to list of units
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], []))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        ASSIGNMENTS.append(values.copy())
    return values

def naked_twins(values):
    """
    Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    """
    Naked twins are identified by any two boxes in a unit that contains the same two
    possibilities. This means that any other boxes that have those same possibilities can
    be eliminated. To start with, we iterate through the each of the units.
    """
    for boxes in unitlist:
        # This maintains the mapping of value to count of occurrences within a unit
        twins = {}

        # This maintains the box to value mapping
        twin_boxes = {}

        """
        We attempt to find the naked twins in three passes of the boxes of a unit
        In the first pass, we iterate through all the boxes looking for values of
        length 2 and for each that we find, we add it to the twins hash, keyed by the
        value along with incrementing the number of times that the value appeared in
        the hash
        """
        for box in boxes:
            val = values[box]
            if len(values[box]) == 2:
                if val not in twins.keys():
                    twins[val] = 0
                twins[val] = twins[val] + 1

        """
        We now iterate through the twins hash, and for each item with a count of 2,
        we scan through the boxes once again to identify the box number and add that
        to a twin_boxes hash.
        """
        for val, count in twins.items():
            if count == 2:
                for box in boxes:
                    if values[box] == val:
                        twin_boxes[box] = val

        """
        In the final step, we iterate through the boxes of the unit, and for each
        occurrence of a naked twin that doesn't exist in the twin_boxes hash, we
        eliminate the values of the twin
        """
        for twin, twinval in twin_boxes.items():
            for box in boxes:
                if box not in twin_boxes:
                    for ch in twinval:
                        assign_value(values, box, values[box].replace(ch, ''))

    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value,
                    then the value will be '123456789'.
    """
    grid = dict(zip(boxes, grid))
    for key, value in grid.items():
        if value == '.':
            grid[key] = '123456789'
    return grid

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in ROWS:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    for box, value in values.items():
        if len(value) == 1:
            prs = peers[box]
            for pr in prs:
                if len(values[pr]) != 1:
                    assign_value(values, pr, values[pr].replace(value, ''))
    return values


def only_choice(values):
    count = {}
    for unit in unitlist:
        for i in range(1, 10):
            count[str(i)] = 0
        for box in unit:
            for ch in values[box]:
                count[ch] = count[ch] + 1
        for box in unit:
            if len(values[box]) != 1:
                for ch in values[box]:
                    if count[ch] == 1:
                        assign_value(values, box, ch)
    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Your code here: Use the Eliminate Strategy
        values = eliminate(values)

        # Implement naked twin exclusion rule
        values = naked_twins(values)

        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])

        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after

        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)

    if values is False:
        return False

    complete = True
    for val in values.values():
        if len(val) > 1:
            complete = False
    if complete:
        return values

    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)

    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """

    # Convert the string representation to a dictionary
    values = grid_values(grid)

    # Invoke the search method and return the solved grid
    return search(values)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(ASSIGNMENTS)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
