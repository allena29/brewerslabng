Feature: Basic CLI mode validations against test data structures

  Scenario: Login to the CLI and poke around operational mode

    When we open the command line interface
    Then we should be presented with a welcome prompt containing
      """
      Welcome to BREWERS COMMAND LINE INTERFACE
      """
