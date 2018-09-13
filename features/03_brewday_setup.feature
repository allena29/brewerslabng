Feature: Basic Setup of the Brewday

  Scenario: Setup the basic brewday parameters such as mash profile,
    femeration profiles etc.
    
    When we send the following CLI
    """
    configure
    set brewhouse temperature mash setpoint 67
    commit
    """

    But we wait for some poking around

