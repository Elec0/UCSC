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
import sys
import inspect
import heapq

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
   
   S = Stack()
   visited = [problem.startingState()]
   path = []
   fringe = []
   
   
   for f in problem.successorStates(problem.startingState()):
      fringe.append(f)
   
   # Algorithm taken from Wikipedia's DFS page
   while len(fringe) > 0:
      curState = fringe[len(fringe)-1]
      # if we haven't visited the state yet
      if not curState[0] in visited:
         # mark it as visited, add it to the current path
         visited.append(curState[0])
         path.append(curState)
         # if we have found the goal state
         # Source: https://www.geeksforgeeks.org/applications-of-depth-first-search/
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
   from game import Directions
   from util import Queue
   
   print "Start", problem.startingState()
   
   # The algorithm for BFS from the book, p.82
   frontier = util.Queue()
   # Populate the frontier the same way as in DFS
   for f in problem.successorStates(problem.startingState()):
      frontier.push(f)
   
   explored = [problem.startingState()]
   path = []
   prev = {}
   
   while True:
      if frontier.isEmpty():
        break # idk, fail
      
      node = frontier.pop() # Shallowest node
      explored.append(node[0])
      path.append(node)
      
      for state in problem.successorStates(node[0]):
         child = state[0]
         # If the child hasn't been expanded yet, do so.
         
         if (child not in explored) and not (True in [child==loc for loc,_,_ in frontier.list]): # child not in frontier.list
            if problem.isGoal(child):
               # Goal found
               pathList = [state[1]]
               # Backtrack over the prev list
               curState = node # Start at the node prior to this one
               
               while True:
                  pathList.insert(0, curState[1]) # Insert this in reverse order
                  if curState in prev:
                     curState = prev[curState] # Do the actual backtracking
                  else: #Done
                     break
               return pathList
               
            else: # State isn't a goal
               frontier.push(state)
               prev[state] = node # record where we came from
   
   return []
         
def uniformCostSearch(problem):
   "Search the node of least total cost first. "
   #from util import PriorityQueue
   
   # The UCS algorithm from the book, p.84
   frontier = PriorityQueue()
   # Populate the starting fringe
   for f in problem.successorStates(problem.startingState()):
      frontier.push(f, f[2])
      
   explored = [problem.startingState()]
   prev = {} # Use a dictionary for the backtracking, it's just easier
   # Doing it this way is probably less efficient than keeping track of the path as we go along
   
   while True:
      if frontier.isEmpty():
         break # fail
      
      (node, priority) = frontier.pop() # Lowest-cost node in frontier
      
      if problem.isGoal(node[0]):
         # Goal found
         actionList = []
         curState = node
         # As we did in BFS, create the action list by backtracking
         while True:
            actionList.insert(0, curState[1])
            if curState in prev:
               curState = prev[curState]
            else: # Done
               break
         return actionList
         
      else:
         explored.append(node[0])
         
         # Loop every edge
         for child in problem.successorStates(node[0]):
            if child[0] not in explored: 
               if child not in frontier.heap:
                  # Properly push the priority on to the queue
                  frontier.push(child, child[2] + priority)
                  prev[child] = node # set the predecessor node
               # if the child is in the frontier, and the new child has a lower cost than the old
               elif child in frontier.heap:
                  # So this doesn't actually do anything that I've found, although it's in the algorithms for UCS.
                  # If the print statement ever pops up I'll use that test case and add it, but idk what it's supposed to be doing
                  print (True in [(loc==child[0] and action==child[1] and child[2] < cost) for loc,action,cost in frontier.heap])
                  print "Replace existing node with child"
                  # replace existing node with child
                  # set child's predecessor to node
            
   return [] # Shouldn't happen

# There was no way to get the priority from the util.PriorityQueue class, so I replicated it here and changed it a tiny bit
class PriorityQueue:
   def  __init__(self):  
    self.heap = []
    
   def push(self, item, priority):
      pair = (priority,item)
      heapq.heappush(self.heap,pair)

   def pop(self):
      (priority,item) = heapq.heappop(self.heap)
      return (item,priority)

   def isEmpty(self):
    return len(self.heap) == 0
    
def nullHeuristic(state, problem=None):
   """
   A heuristic function estimates the cost from the current state to the nearest
   goal in the provided SearchProblem.   This heuristic is trivial.
   """
   return 0

def aStarSearch(problem, heuristic=nullHeuristic):
   "Search the node that has the lowest combined cost and heuristic first."
   
      # The UCS algorithm from the book, p.84
   frontier = PriorityQueue()
   # Populate the starting fringe
   for f in problem.successorStates(problem.startingState()):
      frontier.push(f, 0)
      
   explored = [problem.startingState()]
   prev = {} # Use a dictionary for the backtracking, it's just easier
   # Doing it this way is probably less efficient than keeping track of the path as we go along
   
   
   while True:
      if frontier.isEmpty():
         break # fail
      
      (node, priority) = frontier.pop() # Lowest-cost node in frontier
      if node[0] not in explored: 
         if problem.isGoal(node[0]):
            # Goal found
            actionList = []
            curState = node
            # As we did in BFS, create the action list by backtracking
            while True:
               actionList.insert(0, curState[1])
               if curState in prev:
                  curState = prev[curState]
               else: # Done
                  break
            return actionList
            
         else: # The goal has not been found
            explored.append(node[0])
            
            # Loop every edge
            for child in problem.successorStates(node[0]):
               if child[0] not in explored:
                  if not (True in [child==cur for cur in frontier.heap]): # child not in frontier.heap
                     # Properly push the priority on to the queue
                     frontier.push(child, child[2] + priority + heuristic(child[0], problem))
                     prev[child] = node # set the predecessor node
                  # if the child is in the frontier, and the new child has a lower cost than the old
                  else:
                     # So this doesn't actually do anything that I've found, although it's in the algorithms for UCS.
                     # If the print statement ever pops up I'll use that test case and add it, but idk what it's supposed to be doing
                     print (True in [(loc==child[0] and action==child[1] and child[2] < cost) for loc,action,cost in frontier.heap])
                     print "Replace existing node with child"
                     # replace existing node with child
                     # set child's predecessor to node
            
   return [] # Shouldn't happen
      

   
# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
