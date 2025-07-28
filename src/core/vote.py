class Vote:
    """Base vote class with simple state management"""
    
    def __init__(self, config: dict):
        self.config = config
        self.success = False
        self.error = None
        self.vote_id = None
        self.calldata = None
    
    def validate(self) -> bool:
        """Validate inputs - to be implemented by subclasses"""
        raise NotImplementedError
    
    def simulate(self) -> bool:
        """Simulate the vote - to be implemented by subclasses"""
        raise NotImplementedError
    
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
    
    def _create_vote(self) -> bool:
        """Create the actual vote - to be implemented by subclasses"""
        raise NotImplementedError