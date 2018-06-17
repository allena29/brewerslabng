Feature: Basic Setup of the Brewrey

  Scenario: Create Temperature Probes

    When we send the following CLI
    """
    configure
    create brewhouse temperature hardware probe 28-000hlt
    commit
    """


