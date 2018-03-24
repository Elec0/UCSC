# valueIterationAgents.py
# -----------------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

import mdp, util

from learningAgents import ValueEstimationAgent

class ValueIterationAgent(ValueEstimationAgent):
  """
      * Please read learningAgents.py before reading this.*

      A ValueIterationAgent takes a Markov decision process
      (see mdp.py) on initialization and runs value iteration
      for a given number of iterations using the supplied
      discount factor.
  """
  def __init__(self, mdp, discountRate = 0.9, iters = 100):
    """
      Your value iteration agent should take an mdp on
      construction, run the indicated number of iterations
      and then act according to the resulting policy.

      Some useful mdp methods you will use:
          mdp.getStates()
          mdp.getPossibleActions(state)
          mdp.getTransitionStatesAndProbs(state, action)
          mdp.getReward(state, action, nextState)
    """
    self.mdp = mdp
    self.discountRate = discountRate
    self.iters = iters
    self.values = util.Counter() # A Counter is a dict with default 0

    """Description:
    Iterate the specified number of times
    Loop through each state possible in the mdp.
    For each state get all the actions and get their qvalues into a list.
    Pick the max qvalue from the list and set the value of the state to that value
    """
    """ YOUR CODE HERE """
    
    # For each iteration set every value to the best possible qvalue
    for i in range(self.iters):
        vals = util.Counter()
        
        for state in self.mdp.getStates():
            actions = self.mdp.getPossibleActions(state)
            
            qValueList = []
            for act in actions:
                qValueList.append(self.getQValue(state, act))
            
            if len(qValueList) > 0:
                vals[state] = max(qValueList)
        self.values = vals
    """ END CODE """

  def getValue(self, state):
    """
      Return the value of the state (computed in __init__).
    """
    return self.values[state]

  def getQValue(self, state, action):
    """
      The q-value of the state action pair
      (after the indicated number of value iteration
      passes).  Note that value iteration does not
      necessarily create this quantity and you may have
      to derive it on the fly.
    """
    """Description:
    [Enter a description of what you did here.]
    """
    """ YOUR CODE HERE """
    # Return the sums of the values of all the states, adjusted for their probabilitites
    
    # Transitions[0] is the new location, transitions[1] is the probability to move there
    sum = 0
    for t in self.mdp.getTransitionStatesAndProbs(state, action):
        moveVal = self.getValue(t[0]) * self.discountRate
        sum += (moveVal + self.mdp.getReward(state, state, t[0])) * t[1]
    
    return sum
    """ END CODE """

  def getPolicy(self, state):
    """
      The policy is the best action in the given state
      according to the values computed by value iteration.
      You may break ties any way you see fit.  Note that if
      there are no legal actions, which is the case at the
      terminal state, you should return None.
    """

    """Description:
    [Enter a description of what you did here.]
    """
    """ YOUR CODE HERE """
    # Return the action that has the highest qvalue
    highest = None
    possibleActions = self.mdp.getPossibleActions(state)
    
    # Do nothing if there is nothing to do
    if len(possibleActions) == 0:
        return None
    
    for action in possibleActions:
        temp = self.getQValue(state, action)
        if highest == None or temp > self.getQValue(state, highest): # If there is no current highest, set it to the first action, otherwise we get an error
            highest = action
    
    return highest
    
    """ END CODE """

  def getAction(self, state):
    "Returns the policy at the state (no exploration)."
    return self.getPolicy(state)

    
    
    