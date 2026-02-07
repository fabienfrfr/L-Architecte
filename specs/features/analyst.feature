Feature: Analyst Agent
  Scenario: Analyze CDC
    Given a CDC text
    When the analyst agent processes it
    Then it should return a CadrageReport with needs, constraints, and risks
