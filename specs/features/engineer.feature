Feature: Engineer Agent
  Scenario: Generate SOLID Code
    Given an ADR and C4 diagram
    When the engineer agent processes them
    Then it should return SOLID-compliant code with unit tests
