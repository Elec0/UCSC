# multiAgents.py
# --------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
   """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.   You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
   """


   def getAction(self, gameState):
      """
      You do not need to change this method, but you're welcome to.

      getAction chooses among the best options according to the evaluation function.

      Just like in the previous project, getAction takes a GameState and returns
      some Directions.X for some X in the set {North, South, West, East, Stop}
      """
      # Collect legal moves and successor states
      legalMoves = gameState.getLegalActions()

      # Choose one of the best actions
      scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
      bestScore = max(scores)
      bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
      chosenIndex = random.choice(bestIndices) # Pick randomly among the best

      "Add more of your code here if you want to"

      return legalMoves[chosenIndex]

   def evaluationFunction(self, currentGameState, action):
      """
      Design a better evaluation function here.

      The evaluation function takes in the current and proposed successor
      GameStates (pacman.py) and returns a number, where higher numbers are better.

      The code below extracts some useful information from the state, like the
      remaining food (oldFood) and Pacman position after moving (newPos).
      newScaredTimes holds the number of moves that each ghost will remain
      scared because of Pacman having eaten a power pellet.

      Print out these variables to see what you're getting, then combine them
      to create a masterful evaluation function.
      """
	
      # Useful information you can extract from a GameState (pacman.py)
      successorGameState = currentGameState.generatePacmanSuccessor(action)
      newPosition = successorGameState.getPacmanPosition()
      oldFood = currentGameState.getFood()
      newGhostStates = successorGameState.getGhostStates()
      newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
      oldScaredTimes = [ghostState.scaredTimer for ghostState in currentGameState.getGhostStates()]
	
	
      "*** YOUR CODE HERE ***"
      ghostPos = [None] * len(newGhostStates)
      
      for i in range(0, len(newGhostStates)):
		ghostPos[i] = newGhostStates[i].getPosition()
      tempDist = 0
      
      # Get the manhattan distance from pacman's new location to all of the ghosts
      for i in range(0, len(ghostPos)):
		tempDist += abs(newPosition[0] - ghostPos[i][0]) + abs(newPosition[1] - ghostPos[i][1])
      
      foodDist = 0
      # Get the manhattan distance from the new location to the closest food pellet
      i = 0
      closest = 99999
      
      for item in oldFood:
            for j in range(0, len(oldFood[i])):
                  if oldFood[i][j] == True:
                        t = abs(newPosition[0] - i) + abs(newPosition[1] - j)
                        if closest > t:
                              closest = t
            i += 1
      
      # If the ghost is farther than 4 squares away we don't really need to worry about it, so decrease the impact
      #    this variable has on the path picked
      if tempDist > 4:
            tempDist /= 2
            
      # If the ghosts aren't scared, worry about their location
      if oldScaredTimes[0] == 0:
            return successorGameState.getScore() + tempDist + (len(oldFood[0]) - closest)
      else:
            return (len(oldFood[0])*2 - closest)

def scoreEvaluationFunction(currentGameState):
   """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
   """
   return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
   """
      This class provides some common elements to all of your
      multi-agent searchers.   Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.   Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.   It's
      only partially specified, and designed to be extended.   Agent (game.py)
      is another abstract class.
   """

   def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
      self.index = 0 # Pacman is always agent index 0
      self.evaluationFunction = util.lookup(evalFn, globals())
      self.treeDepth = int(depth)
      
   def isPacman(self, agent):
      return agent == 0
      
   # Terminal state is when you either find a state that is a win or loss, or when you hit the maximum depth for your search
   def isTerminal(self, state, depth, agent):
      
      # If we're out of depth
      # If the agent has no more legal moves, also end
      # If the state is a win or a lose (Reading the docs is helpful for not duplicating code)
      return self.treeDepth <= depth or len(state.getLegalActions(agent)) == 0 or \
         state.isWin() or state.isLose()

class MinimaxAgent(MultiAgentSearchAgent):
   """
      Your minimax agent (question 2)
   """
   
   def getAction(self, gameState):
      """
      Returns the minimax action from the current gameState using self.treeDepth
      and self.evaluationFunction.

      Here are some method calls that might be useful when implementing minimax.

      gameState.getLegalActions(agentIndex):
      Returns a list of legal actions for an agent
      agentIndex=0 means Pacman, ghosts are >= 1

      Directions.STOP:
      The stop direction, which is always legal

      gameState.generateSuccessor(agentIndex, action):
      Returns the successor game state after an agent takes an action

      gameState.getNumAgents():
      Returns the total number of agents in the game
      """
      "*** YOUR CODE HERE ***"
      
      mmList = []
      actionList = []
      for a in gameState.getLegalActions(0):
         mmList.append(self.miniMax(gameState.generateSuccessor(0, a), 0, 1))
         actionList.append(a)
      
      # Return the action required to get to the 
      return actionList[mmList.index(max(mmList))]
      
      
   def miniMax(self, gameState, depth, agent):
      # Since we increment the agent every loop, check to see if we've looped
      #  over all the agents. If we have we've looped 1 ply and so the depth 
      #  should be incremented and the agent counter reset.
      if agent >= gameState.getNumAgents():
         depth += 1
         agent = 0
      
      # If is a terminal state, return the utility
      if(self.isTerminal(gameState, depth, agent)):
         return self.evaluationFunction(gameState)      
      
      successors = []
      for a in gameState.getLegalActions(agent):
         # Don't increment the depth until 1 ply has elapsed
         successors.append(self.miniMax(gameState.generateSuccessor(agent, a), depth, agent + 1))
      
      # If we're pacman, get the max
      if agent == 0:
         return max(successors)
      else: # We're a ghost, so get the min
         return min(successors)

class AlphaBetaAgent(MultiAgentSearchAgent):
   """
      Your minimax agent with alpha-beta pruning (question 3)
   """

   def getAction(self, gameState):
      """
         Returns the minimax action using self.treeDepth and self.evaluationFunction
      """
      "*** YOUR CODE HERE ***"
      mmList = []
      actionList = []
      for a in gameState.getLegalActions(0):
         mmList.append(self.miniMax(gameState.generateSuccessor(0, a), 0, 1, float('-inf'), float('inf')))
         actionList.append(a)
      
      # Return the action required to get to the 
      return actionList[mmList.index(max(mmList))]
      
      
   def miniMax(self, gameState, depth, agent, alpha, beta):
      # Since we increment the agent every loop, check to see if we've looped
      #  over all the agents. If we have we've looped 1 ply and so the depth 
      #  should be incremented and the agent counter reset.
      if agent >= gameState.getNumAgents():
         depth += 1
         agent = 0
      
      # If is a terminal state, return the utility
      if(self.isTerminal(gameState, depth, agent)):
         return self.evaluationFunction(gameState)      
      
      v = (float('-inf') if self.isPacman(agent) else float('inf'))
      successors = []
      for a in gameState.getLegalActions(agent):
         # Don't increment the depth until 1 ply has elapsed
         successors.append(self.miniMax(gameState.generateSuccessor(agent, a), depth, agent + 1, alpha, beta))
         v = successors[-1]
         
         if self.isPacman(agent): 
            if v >= beta: return v
            alpha = min(alpha, v)
         else: 
            if v <= alpha: return v
            beta = min(beta, v)
         
      # If we're pacman, get the max
      if agent == 0:
         return max(successors)
      else: # We're a ghost, so get the min
         return min(successors)

class ExpectimaxAgent(MultiAgentSearchAgent):
   """
      Your expectimax agent (question 4)
   """

   def getAction(self, gameState):
      """
         Returns the expectimax action using self.treeDepth and self.evaluationFunction

         All ghosts should be modeled as choosing uniformly at random from their
         legal moves.
      """
      "*** YOUR CODE HERE ***"
      mmList = []
      actionList = []
      for a in gameState.getLegalActions(0):
         mmList.append(self.expectiMax(gameState.generateSuccessor(0, a), 0, 1))
         actionList.append(a)
      
      # Return the action required to get to the 
      return actionList[mmList.index(max(mmList))]
      
      
   def expectiMax(self, gameState, depth, agent):
      # Since we increment the agent every loop, check to see if we've looped
      #  over all the agents. If we have we've looped 1 ply and so the depth 
      #  should be incremented and the agent counter reset.
      if agent >= gameState.getNumAgents():
         depth += 1
         agent = 0
      
      # If is a terminal state, return the utility
      if(self.isTerminal(gameState, depth, agent)):
         return self.evaluationFunction(gameState)      
      
      successors = []
      for a in gameState.getLegalActions(agent):
         # Don't increment the depth until 1 ply has elapsed
         successors.append(self.expectiMax(gameState.generateSuccessor(agent, a), depth, agent + 1))
      
      # If we're pacman, get the max
      if agent == 0:
         return max(successors)
      else: # We're a ghost, so get the average of our moves
         return sum(successors) / len(successors)

      

def betterEvaluationFunction(currentGameState):
   """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: 
      I took the evaulation code I had for part 1, which did pretty well, and tweaked it a small bit
      to work with this situation. The general idea of my approach is to calculate manhattan distances
      between the ghosts and the closest food pellet, then try to get to the food pellet. 
      The ghosts distance is straight out ignored if they are farther than 4 squares away, and if they
      are farther than 2 squares it's halved, because a lot can happen in 2 squares. When the ghost gets
      within 1 square the getScore() part kicks in and makes pacman run away because of the large negative
      point value for dying.
      Finding the closest food I also changed from my q1. Instead of subtracting the width of the board, 
      which was not giving values that were all that helpful, I use the reciprocal, to get higher values 
      for closer food pellets. 
   """
   "*** YOUR CODE HERE ***"
   # Useful information you can extract from a GameState (pacman.py)
   newPosition = currentGameState.getPacmanPosition()
   oldFood = currentGameState.getFood()
   newGhostStates = currentGameState.getGhostStates()
   newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]


   "*** YOUR CODE HERE ***"
   ghostPos = [None] * len(newGhostStates)
   
   for i in range(0, len(newGhostStates)):
      ghostPos[i] = newGhostStates[i].getPosition()
   tempDist = 0
   
   # Get the manhattan distance from pacman's new location to all of the ghosts
   for i in range(0, len(ghostPos)):
      tempDist += abs(newPosition[0] - ghostPos[i][0]) + abs(newPosition[1] - ghostPos[i][1])
   
   # Get the manhattan distance from the new location to the closest food pellet
   foodDistances = []
   for pellet in oldFood.asList():
      foodDistances.append(abs(newPosition[0] - pellet[0]) + abs(newPosition[1] - pellet[1]))
         
   # If the ghost is farther than 4 squares away we don't really need to worry about it, so decrease the impact
   #    this variable has on the path picked
   if tempDist > 2:
      tempDist /= 2
   if tempDist > 4:
      tempDist = 0
   
   # Instead of trying to subtract the length of the board, get the 'reciprocal' of the distance.
   # Except instead of 1 / n, we need a larger number to make the end value matter in terms of distance
   #  to the ghosts.   
   foodValue = 0
   if len(foodDistances) > 0:
      foodValue = 12 / min(foodDistances)
   
   # If the ghosts aren't scared, worry about their location
   if newScaredTimes[0] == 0:
      return currentGameState.getScore() + tempDist + foodValue
   else:
      return foodValue
   

# Abbreviation
better = betterEvaluationFunction

class ContestAgent(MultiAgentSearchAgent):
   """
      Your agent for the mini-contest
   """

   def getAction(self, gameState):
      """
         Returns an action.   You can use any method you want and search to any depth you want.
         Just remember that the mini-contest is timed, so you have to trade off speed and computation.

         Ghosts don't behave randomly anymore, but they aren't perfect either -- they'll usually
         just make a beeline straight towards Pacman (or away from him if they're scared!)
      """
      "*** YOUR CODE HERE ***"
      util.raiseNotDefined()

