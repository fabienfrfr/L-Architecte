Feature: Architect Agent
  Scenario: Generate C4 Diagram
    Given system requirements
    When the architect agent processes them
    Then it should return a Mermaid diagram
