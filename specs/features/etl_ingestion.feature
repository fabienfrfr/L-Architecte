Feature: Semantic Knowledge Ingestion
  As an Architect
  I want to identify entities using lightweight embeddings
  In order to build a flexible Knowledge Graph without heavy dependencies

  Scenario: Extracting technical concepts via semantic similarity
    Given a technical PDF source "specification.pdf"
    When the ETLMapper processes the document with FastEmbed
    Then it should identify entities semantically related to "Technology"
    And the ArangoDB graph should be updated with these discoveries