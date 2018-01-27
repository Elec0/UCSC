# search.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

"""
In search.py, you will implement generic search algorithms which are called 
by Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
   """
   This class outlines the structure of a search problem, but doesn't implement
   any of the methods (in object-oriented terminology: an abstract class).
   
   You do not need to change anything in this class, ever.
   """
   
   def startingState(self):
      """
      Returns the start state for the search problem 
      """
      util.raiseNotDefined()

   def isGoal(self, state): #isGoal -> isGoal
      """
      state: Search state

      Returns True if and only if the state is a valid goal state
      """
      util.raiseNotDefined()

   def successorStates(self, state): #successorStates -> successorsOf
      """
      state: Search state
       For a given state, this should return a list of triples, 
       (successor, action, stepCost), where 'successor' is a 
       successor to the current state, 'action' is the action
       required to get there, and 'stepCost' is the incremental 
       cost of expanding to that successor
      """
      util.raiseNotDefined()

   def actionsCost(self, actions): #actionsCost -> actionsCost
      """
         actions: A list of actions to take
 
       This method returns the total cost of a particular sequence of actions.   The sequence must
       be composed of legal moves
      """
      util.raiseNotDefined()
                

def tinyMazeSearch(problem):
   """
   Returns a sequence of moves that solves tinyMaze.   For any other
   maze, the sequence of moves will be incorrect, so only use this for tinyMaze
   """
   from game import Directions
   s = Directions.SOUTH
   w = Directions.WEST
   return [s,s,w,s,w,w,s,w]

DFSGoal = [] # poor programming
def depthFirstSearch(problem):
   """
   Search the deepest nodes in the search tree first [p 85].
   
   Your search algorithm needs to return a list of actions that reaches
   the goal.   Make sure to implement a graph search algorithm [Fig. 3.7].
   
   To get started, you might want to try some of these simple commands to
   understand the search problem that is being passed in:
   
   print "Start:", problem.startingState()
   print "Is the start a goal?", problem.isGoal(problem.startingState())
   print "Start's successors:", problem.successorStates(problem.startingState())
   """
   from game import Directions
   from util import Stack
   w = Directions.WEST
   
   print "Start", problem.startingState()
   
   S = Stack()
   visited = [problem.startingState()]
   path = []
   fringe = []
   
   #S.push(problem.startingState())
   for f in problem.successorStates(problem.startingState()):
      fringe.append(f)
      
   while len(fringe) > 0:
      curState = fringe[len(fringe)-1]
      # if we haven't visited the state yet
      if not curState[0] in visited:
         # mark it as visited, add it to the current path
         visited.append(curState[0])
         path.append(curState)
         # if we have found the goal state
         if problem.isGoal(curState[0]):
            actionPath = []
            # get the actions from the path
            for state in path:
               actionPath.append(state[1])
            return actionPath # we're done, we have found a path to the goal.
         else: # the state is not a goal, expand it's successor states
            for state in problem.successorStates(curState[0]):
               fringe.append(state)
               # we don't need to check if the state has been visited here, 
               #     it's already checking earlier in the loop
         
      else: # if we have visited the state before
         # remove the state from the fringe and just keep looping
         fringe.pop()
         # When we're backtracking, if we find a state we have already visited we must remove it, otherwise
         #  pacman will keep going down an invalid path.
         # This will remove the bad paths in each iteration as it goes backwards.
         if curState == path[len(path)-1]:
            path.pop()
   
   return [] # shouldn't ever happen
      
def breadthFirstSearch(problem):
   "Search the shallowest nodes in the search tree first. [p 81]"
   util.raiseNotDefined()
         
def uniformCostSearch(problem):
   "Search the node of least total cost first. "
   util.raiseNotDefined()

def nullHeuristic(state, problem=None):
   """
   A heuristic function estimates the cost from the current state to the nearest
   goal in the provided SearchProblem.   This heuristic is trivial.
   """
   return 0

def aStarSearch(problem, heuristic=nullHeuristic):
   "Search the node that has the lowest combined cost and heuristic first."
   util.raiseNotDefined()
      

   
# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
