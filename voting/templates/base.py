from voting.core.vote import Vote

class VoteTemplate(Vote):
    """Base class for all vote templates"""
    
    def __init__(self, config: dict, description: str = ""):
        """
        Initialize a vote template
        
        Args:
            config: Vote configuration dictionary
            description: Description of the vote
        """
        super().__init__(config)
        self.description = description
        self.vote_payload = []
        
    def validate(self) -> bool:
        """
        Validate the vote conditions by calling the subclass's _validate method
        Returns:
            bool: True if validation passes, False otherwise
        """
        try:
            return self._validate()
        except Exception as e:
            self.error = str(e)
            return False
        
    def _validate(self) -> bool:
        """
        Validate the vote conditions - to be implemented by subclasses
        
        Returns:
            bool: True if validation passes, False otherwise
        """
        raise NotImplementedError("This should be implemented by subclasses")
        
    def _simulate(self) -> bool:
        """
        Simulate the vote - to be implemented by subclasses
        
        Returns:
            bool: True if simulation passes, False otherwise
        """
        raise NotImplementedError("This should be implemented by subclasses")
        
    def simulate(self) -> bool:
        """
        Public method to simulate the vote
        Returns:
            bool: True if simulation passes, False otherwise
        """
        try:
            result = self._simulate()
            if result:
                self.success = True
            return result
        except Exception as e:
            self.error = str(e)
            return False
    
    def create_vote(self, simulation: bool = True) -> bool:
        """
        Create the vote (validate, simulate, create)
        Args:
            simulation: If True, simulate the vote. If False, connect to browser wallet for live voting
        Returns:
            bool: True if vote creation succeeds, False otherwise
        """
        if not self.validate():
            return False
        
        if self.config.get("simulate", True) and simulation:
            if not self.simulate():
                return False
        
        return self._create_vote(simulation=simulation)
    
    def _create_vote(self, simulation: bool = True) -> bool:
        """
        Create the actual vote - to be implemented by subclasses
        Args:
            simulation: If True, simulate the vote. If False, connect to browser wallet for live voting
        Returns:
            bool: True if vote creation succeeds, False otherwise
        """
        raise NotImplementedError("This should be implemented by subclasses")
