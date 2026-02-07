Feature: Native UI Workflow
  As an Architect
  I want to trigger the agentic pipeline from the native interface
  To get structured software artifacts

  Scenario: Successful SMART validation
    Given the client input "Building a Python API with Docker and SQL"
    When the user clicks on "START AGENTIC WORKFLOW"
    Then the PM status should be "✅ SMART"
    And a C4 diagram should be displayed